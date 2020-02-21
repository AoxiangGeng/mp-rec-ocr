#coding=utf-8

import logging
import time
import threading
from Queue import Queue, PriorityQueue
from multiprocessing import Value, Process
from pyutil.program import metrics
from pyutil.program.fmtutil import pformat, fmt_exception
from pyutil.program.timing import Timer
from pyutil.program.worker import WorkerMetric

logger = logging.getLogger(__name__)


class WorkerPool(object):
    """
     see pyutil.program.worker.WorkerMetric for emitted metrics.
    """
    WORKER_STAGES = [
            'queue_get',
            'metric',
            'sleep',
            'process',
            ]

    def __init__(self, in_queue, handler, thread_num, worker_num=1, name='',
            post_fork_callback=None, post_fork_reload=None, reload_interval=1,
            async_counting=False, use_priority_inner_queue=False
            ):
        """
        :param post_fork_callback: callback or str
        :param post_fork_reload: callback or str
        :param float reload_interval: seconds
        :param use_priority_inner_queue: make sure put (score, (cmd, args, kwargs)) to in_queue
        """
        self.in_queue = in_queue
        self.handler = handler
        self.worker_num = worker_num
        self.thread_num = thread_num
        self.name = name
        self.workers = []
        self.running = Value('b', False)
        self.post_fork_callback = self.post_fork_reload = None
        self.use_priority_inner_queue = use_priority_inner_queue
        if post_fork_callback:
            self.post_fork_callback = post_fork_callback if callable(post_fork_callback) else getattr(handler, post_fork_callback)
        if post_fork_reload:
            self.post_fork_reload = post_fork_reload if callable(post_fork_reload) else getattr(handler, post_fork_reload)
        self.reload_interval = reload_interval
        self.worker_metric = WorkerMetric(self.worker_num, self.thread_num,
                metric_prefix='worker.%s' % name if name else 'worker',
                async_counting=async_counting
                )
        self._metric_latency_stage = 'worker.%s.latency.stage' % self.name
        self._metric_latency = 'worker.%s.latency' % self.name
        self._metric_throughput = 'worker.%s.throughput' % self.name
        self._metric_qsize = 'worker.%s.qsize' % self.name # in_queue size
        self._define_metrics()
        assert self.worker_num >= 1
        assert self.thread_num >= 1

    def _define_metrics(self):
        metrics.define_counter(self._metric_throughput, 'req')
        metrics.define_timer(self._metric_latency, 'ms')
        metrics.define_timer(self._metric_latency_stage, 'ms')
        metrics.define_store(self._metric_qsize, '')
        metrics.define_tagkv('stage', self.WORKER_STAGES)
        metrics.define_tagkv('task_run_status', ['normal', 'exception'])

    def start(self):
        logger.info('start work pool %s with %s*%s threads', self.name, self.worker_num, self.thread_num)
        self.running.value = True
        for i in range(self.worker_num):
            w = Process(target=self._run_process, name=self.name)
            if self.name:
                w.name = self.name if self.worker_num == 1 else '%s%s' % (self.name, i)
            w.daemon = True
            self.workers.append(w)
        [w.start() for w in self.workers]
        self.worker_metric.start()
        self.metric_thread = threading.Thread(target=self._run_metric_thread)
        self.metric_thread.start()

    def stop(self):
        self.running.value = False
        self.worker_metric.stop()


    def _get_worker_threads(self):
        threads = []
        for i in range(self.thread_num):
            t = threading.Thread(target=self._run_thread)
            if self.name:
                t.name = '%s%s' % (self.name, i)
            t.setDaemon(True)
            threads.append(t)
        return threads

    def _run_process(self):
        self.threads = self._get_worker_threads()
        q_maxsize = min(100, len(self.threads) * 2)
        if self.use_priority_inner_queue:
            self.inner_queue = PriorityQueue(maxsize=q_maxsize)
        else:
            self.inner_queue = Queue(maxsize=q_maxsize)
        if self.post_fork_callback:
            self.post_fork_callback()
        if self.post_fork_reload:
            self.post_fork_reload()
            t = threading.Thread(target=self._run_reload_thread, name='reload')
            t.setDaemon(True)
            self.threads.append(t)
        [t.start() for t in self.threads]
        while self.running.value == True:
            task = self.in_queue.get()
            if self.use_priority_inner_queue:
                assert len(task) == 2 # task[0]=PriorityScore, task[1]=item
            self.inner_queue.put(task)
            self.worker_metric.task_enqueued()

    def _run_reload_thread(self):
        while self.running.value == True:
            time.sleep(self.reload_interval)
            try:
                self.post_fork_reload()
            except Exception as e:
                logger.exception(e)

    def _run_metric_thread(self):
        while self.running.value == True:
            metrics.emit_store(self._metric_qsize, self.in_queue.qsize())
            time.sleep(1)

    def _run_thread(self):
        while self.running.value == True:
            task_run_status = 'normal'
            timer = Timer()
            try:
                r = self.inner_queue.get()
                timer.timing('queue_get')
                self.worker_metric.task_starts()
                timer.timing('metric')
                try:
                    cmd, args, kwargs = r[1] if self.use_priority_inner_queue else r
                    getattr(self.handler, cmd)(*args, **kwargs)
                    timer.timing('process')
                except Exception as e:
                    task_run_status = 'exception'
                    logger.exception('unexpected exception: e=%s, cmd=%s, args=%s, kwargs=%s',
                            fmt_exception(e),
                            cmd,
                            pformat(args, max_v_limit=200),
                            pformat(kwargs, max_v_limit=200)
                            )
                    time.sleep(1)
                    timer.timing('sleep')
                finally:
                    self.worker_metric.task_ends()
                    timer.timing('metric')
            except Exception as e:
                logger.exception(e)
                task_run_status = 'exception'
            for k, v in timer.dur.items():
                if k in self.WORKER_STAGES:
                    metrics.emit_timer(self._metric_latency_stage, 1000 * v, tagkv=dict(stage=k))
            metrics.emit_timer(self._metric_latency, 1000 * timer.total_seconds())
            metrics.emit_counter(self._metric_throughput, 1, tagkv=dict(task_run_status=task_run_status))
