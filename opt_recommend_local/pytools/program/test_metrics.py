#! /usr/bin/python

import sys
sys.path.insert(0, './')
import metrics2 as metrics

#import pyutil.program.metrics as metrics
import pyutil.program.conf
import time
import multiprocessing

def func(counter_v, timer_v):
    while True:
        metrics.emit_counter('throughput', counter_v)
        metrics.emit_timer('latency', timer_v)
        time.sleep(0.001)

def start_process(counter_v, timer_v):
    w = multiprocessing.Process(target=func, args=(counter_v, timer_v, ))
    w.daemon = True
    w.start()

if __name__ == '__main__':
    conf_file = pyutil.program.conf.Conf('test_metrics.conf')
    metrics.init(conf_file)

    metrics.define_counter('throughput', 'req');
    metrics.define_timer('latency', 'us');
    metrics.start()

    start_process(1, 1)
    start_process(1, 10)
    start_process(1, 100)

    while True:
        metrics.emit_counter('throughput', 1)
        time.sleep(1)


