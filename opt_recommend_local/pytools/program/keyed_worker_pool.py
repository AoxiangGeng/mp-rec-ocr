#coding=utf-8
import logging
import multiprocessing
import time
import threading
from Queue import Queue, Empty
from multiprocessing import Process
from pyutil.program import metrics
from pyutil.program.fmtutil import pformat, fmt_exception
from pyutil.program.memory_profiler import memory_usage
from pyutil.program.timing import Timer
from pyutil.program.tracing import init_tracer, start_span, get_current_span, get_current_trace_id, start_child_span
from pyutil.program.worker import WorkerMetric
logger = logging.getLogger(__name__)

WORKER_STAGES = [
        'queue_get',
        'metric',
        'sleep',
        'process',
        ]
IN_QSIZE = 200 # worker的queue (multiprocessing.Queue), queue设置大一些，可避免某一worker临时queue满导致其他worker也堵住
PENDING_QSIZE = 1000 # thread的pending queue. 设置大一些，可避免某一线程queue满导致整个worker堵住

class PoolContext(object):
    def __init__(self, name, worker_num, thread_num, urgent_thread_num, process,
            post_fork_callback, post_fork_reload, reload_interval,
            worker_metric, pending_full_discard, **kwargs):
        self.name = name
        self.worker_num = worker_num
        self.thread_num = thread_num
        self.urgent_thread_num = urgent_thread_num
        self.total_thread_num = thread_num + urgent_thread_num
        self.process = process
        self.post_fork_callback = post_fork_callback
        self.post_fork_reload = post_fork_reload
        self.reload_interval = reload_interval
        self.worker_metric = worker_metric
        self.pending_full_discard = pending_full_discard
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_worker_name(self, worker_index):
        return '%sw%s' % (self.name, worker_index)

class KeyedWorkerPool(object):
    """
     see pyutil.program.worker.WorkerMetric for emitted metrics.
     确保同一key的task串行执行以避免竞争。
     1. put_task按key分发到某个进程的in_queue (multiprocessing normal_queue + urgent_queue)
     2. 每个线程自带一个pending_queue. 若pending_queue有任务，则取出并执行，否则从in_queue取任务
        a. 若对应key的任务正在其他线程执行，则把此任务加入其他线程的pending_queue, 并重新取任务
        b. 否则执行此任务
     3. 如因pending_put阻塞在某线程队列，将导致worker pool读取任务阻塞，可通过pending_full_discard丢弃任务
    """

    def __init__(self, name, process, thread_num, worker_num=1, metric_name=None,
            post_fork_callback=None, post_fork_reload=None, reload_interval=1,
            async_counting=False, key_hash=hash, pending_full_discard=None,
            urgent_thread_num=1,
            ):
        """
        :param callable process(task): handle task
        :param callable post_fork_callback:
        :param callable post_fork_reload:
        :param float reload_interval: seconds
        :param callable key_hash: hash function for key
        :param callable pending_full_discard(task): callback function for discarding pending_put task
        :param int thread_num: thread num for each worker
        :param int urgent_thread_num: urgent thread num for each worker
        """
        assert worker_num >= 1
        assert thread_num >= 1

        self.name = name
        self.key_hash = key_hash
        metric_prefix = 'worker.%s' % (metric_name or name)
        self.context = PoolContext(
                name=name,
                worker_num=worker_num,
                thread_num=thread_num,
                urgent_thread_num=urgent_thread_num,
                process=process,
                post_fork_callback=post_fork_callback,
                post_fork_reload=post_fork_reload,
                reload_interval=reload_interval,
                worker_metric=WorkerMetric(worker_num, thread_num + urgent_thread_num,
                    metric_prefix=metric_prefix,
                    async_counting=async_counting,
                    tagkv=dict(pool=name),
                    ),
                pending_full_discard=pending_full_discard,
                metric_latency_stage='%s.latency.stage' % metric_prefix,
                metric_latency='%s.latency' % metric_prefix,
                metric_throughput='%s.throughput' % metric_prefix,
                metric_qsize='%s.qsize' % metric_prefix, # in_queue size
                metric_pending_qsize='%s.pending_qsize' % metric_prefix,
                metric_taskget_throughput='%s.taskget.throughput' % metric_prefix,
                metric_taskget_latency_stage='%s.taskget.latency.stage' % metric_prefix,
                metric_taskget_latency='%s.taskget.latency' % metric_prefix,
                metric_memory_usage='%s.worker.memusage' % metric_prefix,
                )
        self.workers = []
        self._define_metrics()

    def _define_metrics(self):
        metrics.define_counter(self.context.metric_throughput, 'req')
        metrics.define_timer(self.context.metric_latency, 'ms')
        metrics.define_timer(self.context.metric_latency_stage, 'ms')
        metrics.define_store(self.context.metric_qsize, '')
        metrics.define_store(self.context.metric_pending_qsize, '')
        metrics.define_store(self.context.metric_memory_usage, 'mb')
        metrics.define_tagkv('stage', WORKER_STAGES)
        metrics.define_tagkv('task_run_status', ['normal', 'discard', 'exception'])
        metrics.define_tagkv('worker', map(str, range(self.context.worker_num)))
        metrics.define_tagkv('thread', map(str, range(self.context.thread_num + self.context.urgent_thread_num)))
        metrics.define_tagkv('pool', [self.name])
        metrics.define_tagkv('urgent', ['True', 'False'])

    def start(self):
        logger.info('start work pool %s with %s*(%s+%s) threads', self.name,self.context.worker_num,
                self.context.thread_num, self.context.urgent_thread_num)
        for i in range(self.context.worker_num):
            w = Worker(self.context.get_worker_name(i), self.context, worker_index=i)
            self.workers.append(w)
        [w.start() for w in self.workers]
        self.context.worker_metric.start()

    def stop(self):
        self.context.worker_metric.stop()

    def put_task(self, key, task, task_log_id, urgent=False):
        key_hash = self.key_hash(key)
        worker_index = key_hash % self.context.worker_num
        self.workers[worker_index].task_getter.put(key_hash, task, task_log_id, urgent)

class WorkerMixin(object):
    def _run_reload_thread(self):
        while True:
            time.sleep(self.context.reload_interval)
            try:
                self.context.post_fork_reload()
            except Exception as e:
                logger.exception(e)

    def _run_metric_thread(self):
        while True:
            metrics.emit_store(self.context.metric_qsize, self.task_getter.normal_queue.qsize(),
                    tagkv=dict(self.tagkv, urgent='False'))
            metrics.emit_store(self.context.metric_qsize, self.task_getter.urgent_queue.qsize(),
                    tagkv=dict(self.tagkv, urgent='True'))
            usage = memory_usage(-1, interval=.002, timeout=.01)
            if usage:
                metrics.emit_store(self.context.metric_memory_usage, usage[0], tagkv=self.tagkv)
            self._emit_thread_pending_queue_size()
            time.sleep(1)

    def _emit_thread_pending_queue_size(self):
        thread_index = 0
        for for_urgent, thread_num in [
                (False, self.context.thread_num),
                (True, self.context.urgent_thread_num),
                ]:
            for i in range(thread_num):
                metrics.emit_store(
                    self.context.metric_pending_qsize,
                    self.task_getter.get_pending_qsize(thread_index),
                    tagkv=dict(self.tagkv, thread=str(thread_index),
                               urgent='True' if for_urgent else 'False'))
                thread_index += 1

    def _get_worker_threads(self, task_getter):
        threads = []
        thread_index = 0
        for for_urgent, thread_num in [
                (False, self.context.thread_num),
                (True, self.context.urgent_thread_num),
                ]:
            for i in range(thread_num):
                t = WorkerThread(thread_index,
                        worker_tagkv=self.tagkv,
                        context=self.context,
                        task_getter=task_getter,
                        name='%st%s%s' % (self.name, thread_index, '_urgent' if for_urgent else ''),
                        for_urgent=for_urgent,
                        )
                t.setDaemon(True)
                threads.append(t)
                thread_index += 1
        return threads

class Worker(WorkerMixin, multiprocessing.Process):

    def __init__(self, name, context, worker_index, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self.name = name
        self.context = context
        self.tagkv = dict(pool=self.context.name, worker=str(worker_index))
        self.daemon = True
        self.span_tags = dict(component='pool.worker')
        self.task_getter = TaskGetter(context, self.tagkv, thread_mode=False)

    def run(self):
        self.threads = self._get_worker_threads(self.task_getter)
        if self.context.post_fork_callback:
            self.context.post_fork_callback()
        init_tracer()
        if self.context.post_fork_reload:
            self.context.post_fork_reload()
            t = threading.Thread(target=self._run_reload_thread, name='reload')
            self.threads.append(t)
        metric_thread = threading.Thread(target=self._run_metric_thread)
        self.threads.append(metric_thread)
        [t.setDaemon(True) for t in self.threads]
        [t.start() for t in self.threads]
        while True:
            time.sleep(5)


class WorkerThread(threading.Thread):
    def __init__(self, thread_index, worker_tagkv, context, task_getter, for_urgent, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.context = context
        self.thread_index = thread_index
        self.task_getter = task_getter
        self.for_urgent = for_urgent
        self._worker_tagkv = worker_tagkv
        self.span_tags = dict(component='pool.worker_thread')

    def run(self):
        while True:
            try:
                with start_span('thread_run', tags=self.span_tags) as span:
                    self._run_once(span)
            except Exception as e:
                logger.exception('Fail to process: %s', fmt_exception(e))

    def _run_once(self, span):
        timer = Timer()
        with start_child_span(span, 'task_get', tags=self.span_tags):
            (key_hash, task, task_log_id), task_source = self.task_getter.get(self.thread_index, urgent=self.for_urgent)
        should_discard = task_source == 'pending_discard'
        timer.timing('queue_get')
        task_run_status = 'discard' if should_discard else 'normal'
        try:
            with start_child_span(span,
                    'pending_discard' if should_discard else 'task_process',
                    tags=dict(self.span_tags, task_source=task_source, task_log_id=task_log_id)):
                if should_discard:
                    self.context.pending_full_discard(task)
                    timer.timing('discard')
                else:
                    self.context.process(task)
                    timer.timing('process')
        except Exception as e:
            task_run_status = 'exception'
            logger.exception('%s trace=%s unexpected exception: e=%s',
                    task_log_id, get_current_trace_id(), fmt_exception(e))
            time.sleep(1)
            timer.timing('sleep')
        finally:
            self.task_getter.task_done(key_hash, self.thread_index)
        for k, v in timer.dur.items():
            if k in WORKER_STAGES:
                metrics.emit_timer(self.context.metric_latency_stage, 1000 * v, tagkv=dict(self._worker_tagkv, stage=k))
        metrics.emit_timer(self.context.metric_latency, 1000 * timer.total_seconds(), tagkv=self._worker_tagkv)
        metrics.emit_counter(self.context.metric_throughput, 1, tagkv=dict(self._worker_tagkv,
            task_run_status=task_run_status
            ))

class TaskGetter(object):
    TASKGET_STAGES = ['pending_get', 'main_get', 'pending_put', 'compute', 'pending_discard']
    def __init__(self, context, worker_tagkv, thread_mode):
        self.context = context
        self._worker_tagkv = worker_tagkv
        queue_class = Queue if thread_mode else multiprocessing.Queue
        self.normal_queue = queue_class(maxsize=IN_QSIZE)
        self.urgent_queue = queue_class(maxsize=IN_QSIZE)
        # 各线程pending的任务数(包括pending_queue里的和正在执行的)
        self._pending_counts = [0] * context.total_thread_num
        # 某个key执行的thread index
        self._key2running_index = {}
        self._lock = threading.Lock()
        self._pending_queues = [Queue(maxsize=PENDING_QSIZE) for _ in range(context.total_thread_num)]
        self._define_metrics()
        self.span_tags = dict(component='pool.worker_thread')

    def _define_metrics(self):
        metrics.define_counter(self.context.metric_taskget_throughput, '')
        metrics.define_timer(self.context.metric_taskget_latency_stage, 'ms')
        metrics.define_timer(self.context.metric_taskget_latency, 'ms')
        metrics.define_tagkv('task_source', ['pending_get', 'main_get', 'pending_put', 'pending_discard'])
        metrics.define_tagkv('stage', self.TASKGET_STAGES)

    def put(self, key_hash, task, task_log_id, urgent=False):
        q = self.urgent_queue if urgent else self.normal_queue
        q.put((key_hash, task, task_log_id))
        self.context.worker_metric.task_enqueued()

    def get_pending_qsize(self, thread_index):
        return self._pending_queues[thread_index].qsize()

    def get(self, thread_index, urgent):
        while True:
            t, task_source = self._get(thread_index, urgent=urgent)
            if t:
                self.context.worker_metric.task_starts()
                return t, task_source

    def _get_from_queue(self, urgent):
        if urgent:
            return self.urgent_queue.get()

        while True:
            # urgent queue多数时候应该是空的，用if empty判断以改进性能
            if not self.urgent_queue.empty():
                try:
                    return self.urgent_queue.get_nowait()
                except Empty:
                    pass
            try:
                return self.normal_queue.get(block=True, timeout=0.01)
            except Empty:
                pass

    def _get(self, thread_index, urgent):
        span = get_current_span()
        timer = Timer()
        pending_count = self._pending_counts[thread_index]
        if pending_count:
            # 当前线程尚有任务未处理，则直接取
            with start_child_span(span, 'pending_get', tags=dict(self.span_tags, pending_count=str(pending_count))):
                task_tuple = self._pending_queues[thread_index].get()
            task_source = 'pending_get'
            timer.timing('pending_get')
        else:
            # pending_queue无任务，从主queue取
            with start_child_span(span, 'main_get', tags=self.span_tags):
                task_tuple = key_hash, task, task_log_id = self._get_from_queue(urgent)
            timer.timing('main_get')
            with self._lock:
                # running_index为task应该执行的线程
                running_index = self._key2running_index.get(key_hash)
                if running_index is None:
                    # 此key无任务在其他线程执行，故在当前线程执行
                    task_source = 'main_get'
                    running_index = thread_index
                    self._key2running_index[key_hash] = thread_index
                else:
                    # 此key有任务正在其他线程执行, 故此任务也该在那个线程执行
                    pending_count = self._pending_counts[running_index]
                    pending_full = pending_count >= PENDING_QSIZE
                    if pending_full:
                        logger.info('%s trace=%s pending_put thread=%s, pending_count=%s/%s, key_hash=%s, discard=%s',
                                    task_log_id, get_current_trace_id(),
                                    running_index, pending_count,
                                    self._pending_queues[running_index].qsize(),
                                    key_hash,
                                    'yes' if self.context.pending_full_discard else 'no',
                                    )
                    if self.context.pending_full_discard and pending_full:
                        # pending queue满了，在当前线程discard
                        running_index = thread_index
                        task_source = 'pending_discard'
                    else:
                        # pending queue未满或不允许discard, 任务放入那个线程的pending queue
                        task_source = 'pending_put'
                self._pending_counts[running_index] += 1
            timer.timing('compute')

            if task_source == 'pending_put':
                # 加入queue操作可能比较慢，故放到_lock之外
                with start_child_span(span, 'pending_put',
                        tags=dict(self.span_tags, task_log_id=task_log_id, pending_count=str(pending_count))):
                    self._pending_queues[running_index].put(task_tuple)
                timer.timing('pending_put')
                task_tuple = None

        for k, v in timer.dur.items():
            if k in self.TASKGET_STAGES:
                metrics.emit_timer(self.context.metric_taskget_latency_stage, 1000 * v, tagkv=dict(self._worker_tagkv, stage=k))
        metrics.emit_timer(self.context.metric_taskget_latency, 1000 * timer.total_seconds(), tagkv=self._worker_tagkv)
        metrics.emit_counter(self.context.metric_taskget_throughput, 1, tagkv=dict(self._worker_tagkv, task_source=task_source))

        return task_tuple, task_source

    def task_done(self, key_hash, thread_index):
        with self._lock:
            self._pending_counts[thread_index] -= 1
            if self._pending_counts[thread_index] == 0:
                # discard任务不会在running_index执行，这种情况不能pop key
                if self._key2running_index.get(key_hash) == thread_index:
                    self._key2running_index.pop(key_hash)
        self.context.worker_metric.task_ends()
