# coding: utf8
"""
TProcessThreadPoolServer2

ChangeLog:
2014-8-21
    * emit metrics of everything:
        1. metrics of the remote procedures:
            <PREFIX>.thrift.process.latency         // global latency of rpc (ms)
            <PREFIX>.thrift.process.throughput      // throughput of rpc, tags: method
            <PREFIX>.thrift.process.latency.method  // latency of rpc(ms), tags: method
            <PREFIX>.thrift.func_<FUNC_NAME>.latency
            <PREFIX>.thrift.func_<FUNC_NAME>.throughput
            
            之所以不给latency加tag, 而是专门新开latency.method来支持tag,
            是因为加method tag后，会导致latency.avg的语意改变, 导致无法和
            后面的conn_life等进行对比
        2. metrics of queuing time:
            <PREFIX>.thrift.queue_latency     // the time from put to get
        3. metrics of I/O:
            <PREFIX>.thrift.conn_life         // the time from accept to close
            <PREFIX>.thrift.conn_read_latency
            <PREFIX>.thrift.conn_write_latency
    * export current client by handler.get_current_client()
    * add `birth_time` attribute to client

2014-8-22
    * add `keepalive` parameter for Non-persistent connection

"""
import logging, signal, sys, socket
from multiprocessing import  Process, Value, Condition
import random
from time import time, sleep
import threading
import Queue

from thrift.server.TServer import TServer
from thrift.Thrift import TProcessor
from thrift.Thrift import TType, TMessageType, TApplicationException
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


import pyutil.program.metrics2 as metrics
from pyutil.program.thread_helper import set_thread_name

METRICS_PREFIX = "thrift."
METRICS_PROCESS_LATENCY = METRICS_PREFIX + "process.latency"
METRICS_PROCESS_LATENCY_METHOD = METRICS_PREFIX + "process.latency.method"
METRICS_PROCESS_LATENCY_TPL = METRICS_PREFIX + "func_%s.latency"
METRICS_PROCESS_THROUGHPUT = METRICS_PREFIX + "process.throughput"
METRICS_PROCESS_THROUGHPUT_TPL = METRICS_PREFIX + "func_%s.throughput"
METRICS_QUEUING_TIME = METRICS_PREFIX + "queue_latency"
METRICS_CONN_LIFE = METRICS_PREFIX + "conn_life"
METRICS_READ_LATENCY = METRICS_PREFIX + "conn_read_latency"
METRICS_WRITE_LATENCY = METRICS_PREFIX + "conn_write_latency"
UNKNOWN_METHOD_NAME = 'unknown_method'


def define_all_metrics(processor):
    logging.info("define_all_metrics, prefix: %s" % metrics.namespace_prefix)
    metrics.define_counter(METRICS_PROCESS_THROUGHPUT)
    metrics.define_timer(METRICS_PROCESS_LATENCY)
    metrics.define_timer(METRICS_PROCESS_LATENCY_METHOD)
    metrics.define_timer(METRICS_QUEUING_TIME)
    metrics.define_timer(METRICS_CONN_LIFE)
    metrics.define_timer(METRICS_READ_LATENCY)
    metrics.define_timer(METRICS_WRITE_LATENCY)
    methods = [UNKNOWN_METHOD_NAME] + list(processor._processMap.iterkeys())
    metrics.define_tagkv('method', methods)
    for func_name in methods:
        metrics.define_counter(METRICS_PROCESS_THROUGHPUT_TPL % func_name)
        metrics.define_timer(METRICS_PROCESS_LATENCY_TPL % func_name)


class Timing(object):
    def __init__(self, name):
        self.name = name

    def begin(self):
        self.start_time = time()

    def end(self):
        latency = 1000 * (time() - self.start_time)
        metrics.emit_timer(self.name, latency)

    def __enter__(self):
        self.begin()

    def __exit__(self, ex_type, ex_value, traceback):
        self.end()


class ProcessMetrics(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time()

    def __exit__(self, ex_type, ex_value, traceback):
        latency = 1000 * (time() - self.start)
        name = self.name or UNKNOWN_METHOD_NAME
        metrics.emit_timer(METRICS_PROCESS_LATENCY, latency)
        metrics.emit_timer(METRICS_PROCESS_LATENCY_METHOD, latency, tagkv=dict(method=name))
        metrics.emit_counter(METRICS_PROCESS_THROUGHPUT, 1, tagkv=dict(method=name))
        metrics.emit_timer(METRICS_PROCESS_LATENCY_TPL % name, latency)
        metrics.emit_counter(METRICS_PROCESS_THROUGHPUT_TPL % name, 1)


def patch_in_protocol(iprot, i_begin_cb, i_end_cb):
    in_msg_begin = iprot.readMessageBegin
    in_msg_end = iprot.readMessageEnd
    def _wrap_readMessageBegin():
        i_begin_cb()
        return in_msg_begin()
    def _wrap_readMessageEnd():
        ret = in_msg_end()
        i_end_cb()
        return ret
    iprot.readMessageBegin = _wrap_readMessageBegin
    iprot.readMessageEnd = _wrap_readMessageEnd


def patch_out_protocol(oprot, o_begin_cb, o_end_cb):
    out_msg_begin = oprot.writeMessageBegin
    out_msg_end = oprot.trans.flush
    def _wrap_writeMessageBegin(*args, **kwargs):
        o_begin_cb()
        return out_msg_begin(*args, **kwargs)
    def _wrap_trans_flush():
        ret = out_msg_end()
        o_end_cb()
        return ret
    oprot.writeMessageBegin = _wrap_writeMessageBegin
    oprot.trans.flush = _wrap_trans_flush


__current_thread_client = threading.local()
def get_current_client():
    return getattr(__current_thread_client, "val", None)

def set_current_client(cli):
    __current_thread_client.val = cli


class TProcessThreadPoolServer2(TServer):

    """
    Server with a fixed size pool of worker subprocesses which service requests.
    Note that if you need shared state between the handlers - it's up to you!
    Written by Dvir Volk, doat.com
    """

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        postForkReload: 异步处理线程
        reloadInterval: 异步处理线程运行周期，单位s，固定或者tuple表示区间
        heavyReload: 是否重量级处理，是的话会在处理前停止accept，以避免GIL竞争导致的处理超时
        """
        TServer.__init__(self, *args)
        self.numWorkers = 10
        self.workers = []
        self.isRunning = Value('b', False)
        self.stopCondition = Condition()
        self.postForkCallback = None 

        self.threads = 10
        self.daemon = kwargs.get("daemon", False)
        self.keepalive = kwargs.get("keepalive", True)

        self.pendingTaskCountMax = kwargs.get("pendingTaskCountMax", 0)
        self.postForkReload = kwargs.get('postForkReload')
        self.heavyReload = kwargs.get('heavyReload', False)
        self.reloadInterval = kwargs.get('reloadInterval', 1)
        self.busyCondition = Condition()
        self._is_busy = False
        processor = self.processor
        assert hasattr(processor, "_handler")
        assert hasattr(processor, "_processMap")
        # export current client by handler.get_current_client()
        processor._handler.get_current_client = get_current_client

    def setPostForkCallback(self, callback):
        if not callable(callback):
            raise TypeError("This is not a callback!")
        self.postForkCallback = callback

    def setNumWorkers(self, num):
        """Set the number of worker threads that should be created"""
        self.numWorkers = num

    def setNumThreads(self, num):
        """Set the number of worker threads that should be created"""
        self.threads = num

    def serveThread(self):
        """Loop around getting clients from the shared queue and process them."""
        queue_timing = Timing(METRICS_QUEUING_TIME)
        life_timing = Timing(METRICS_CONN_LIFE)
        while True:
            try:
                client = self.clients.get()
                try:
                    set_current_client(client)
                    queue_timing.start_time = client.birth_time
                    queue_timing.end()
                    with life_timing:
                        self.serveClient(client)
                except Exception as x:
                    logging.exception(x)
                finally:
                    self.free_workers.put(1)
            except Exception, x:
                logging.exception(x)

    def serveClient(self, client):
        """Process input/output from a client for as long as possible"""
        itrans = self.inputTransportFactory.getTransport(client)
        otrans = self.outputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)
        oprot = self.outputProtocolFactory.getProtocol(otrans)
        iprot_timing = Timing(METRICS_READ_LATENCY)
        oprot_timing = Timing(METRICS_WRITE_LATENCY)
        patch_in_protocol(iprot, iprot_timing.begin, iprot_timing.end)
        patch_out_protocol(oprot, oprot_timing.begin, oprot_timing.end)
        try:
            processor = self.processor
            process_map = processor._processMap
            keepalive = self.keepalive
            while True:
                name, _, seqid = iprot.readMessageBegin()
                process_func = process_map.get(name)
                if process_func:
                    with ProcessMetrics(name):
                        process_func(processor, seqid, iprot, oprot)
                else:
                    with ProcessMetrics(None):
                        iprot.skip(TType.STRUCT)
                        iprot.readMessageEnd()
                        x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
                        oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
                        x.write(oprot)
                        oprot.writeMessageEnd()
                        oprot.trans.flush()

                if not keepalive:
                    break

        except TTransport.TTransportException, tx:
            pass
        except socket.error as e:
            logging.warning('TProcessThreadPoolServer.serverClient socket.error: %s', e)
        except Exception, x:
            logging.exception(x)
        itrans.close()
        otrans.close()

    def _reloadThread(self):
        logging.info('[TProcessThreadPoolServer2] start reload thread')
        while True:
            if isinstance(self.reloadInterval, tuple):
                min_interval, max_interval = self.reloadInterval
                interval = random.random() * (max_interval - min_interval) + min_interval
            else:
                interval = self.reloadInterval
            sleep(interval)
            logging.info('[TProcessThreadPoolServer2] reload after sleep interval: %s' % interval)
            time_begin = time()
            try:
                if self.heavyReload:
                    self.busyCondition.acquire()
                    self._is_busy = True
                    self.busyCondition.release()
                self.postForkReload()
            except Exception as e:
                logging.exception(e)
            finally:
                if self.heavyReload:
                    self.busyCondition.acquire()
                    self._is_busy = False
                    self.busyCondition.notify_all()
                    self.busyCondition.release()
            time_cost = time() - time_begin
            logging.info('[TProcessThreadPoolServer2] reload_finish after sleep interval: %s, time_cost: %s'
                         % (interval, time_cost))

    def workerProcess(self):
        if self.postForkCallback:
            self.postForkCallback()
        if self.postForkReload:
            reload_thread = threading.Thread(target=self._reloadThread, name='reload')
            reload_thread.setDaemon(self.daemon)
            reload_thread.start()

        self.clients = Queue.Queue(maxsize=self.pendingTaskCountMax)
        logging.info('[TProcessThreadPoolServer2] init queue id: %s' % id(self.clients))
        self.free_workers = Queue.Queue()

        define_all_metrics(self.processor)

        for i in range(self.threads):
            try:
                t = threading.Thread(target=self.serveThread)
                self.free_workers.put(1)
                t.setDaemon(self.daemon)
                t.start()
                set_thread_name(t.ident, "thrift:worker")
            except Exception, x:
                logging.exception(x)

        """Loop around getting clients from the shared queue and process them."""
        # Pump the socket for clients
        def acceptThread():
            while self.isRunning.value:
                client = None
                try:
                    self.free_workers.get()  # 没有free_workers了，需要等待
                    if self.heavyReload:
                        self.busyCondition.acquire()  # 有其他线程密集处理，忙，由于GIL，需要等待
                        if self._is_busy:
                            self.busyCondition.wait()
                        self.busyCondition.release()
                    client = self.serverTransport.accept()
                    client.birth_time = time()
                    self.clients.put_nowait(client)
                except (KeyboardInterrupt, SystemExit):
                    return 0
                except Exception, x:
                    logging.exception(x)
                    if client:
                        itrans = self.inputTransportFactory.getTransport(client)
                        otrans = self.outputTransportFactory.getTransport(client)
                        itrans.close()
                        otrans.close()
                finally:
                    if client is None:
                        self.free_workers.put(1)
        t = threading.Thread(target=acceptThread)
        t.start()
        set_thread_name(t.ident, "thrift:accept")
        t.join()

    def serve(self):
        """Start a fixed number of worker threads and put client into a queue"""

        #this is a shared state that can tell the workers to exit when set as false
        self.isRunning.value = True

        #first bind and listen to the port
        self.serverTransport.listen()

        def _fork_sub_process(num):
            #fork the children
            for i in range(num):
                try:
                    w = Process(target=self.workerProcess)
                    w.daemon = True
                    w.start()
                    self.workers.append(w)
                except Exception, x:
                    logging.exception(x)

        _fork_sub_process(self.numWorkers)
        #wait until the condition is set by stop()

        while True:
            alive_workers = [w for w in self.workers if w.is_alive()]
            dead_count = len(self.workers) - len(alive_workers)
            self.workers = alive_workers
            sleep(0.2)
            _fork_sub_process(dead_count)

            self.stopCondition.acquire()
            try:
                self.stopCondition.wait(timeout=5)
                if not self.isRunning.value:
                    break
            except (SystemExit, KeyboardInterrupt):
                break
            except Exception, x:
                logging.exception(x)

        self.isRunning.value = False

    def stop(self):
        self.isRunning.value = False
        self.stopCondition.acquire()
        self.stopCondition.notify()
        self.stopCondition.release()

