#!/usr/bin/env python
# coding=utf8
import datetime
import gc
import os
import json
import math
import multiprocessing
import random
import signal
import sys
import time
import traceback
import numpy as np
import cv2

sys.path.append("opt_recommend_local")
sys.path.append("chineseocr_lite")

import conf as vulgar_conf
from cityhash import CityHash32
from pytools.program.log import init_logging
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction
from thrift_common.py_iface.ocr_lite_prediction.ttypes import Rsp, OcrPrediction
from thrift.protocol import TBinaryProtocol
from thrift.server.TProcessPoolServer import TProcessPoolServer
from thrift.transport import TSocket, TTransport
from prometheus_def import *
from model import *

free_worker_count = multiprocessing.Value('i')
print(free_worker_count)



class ServiceHandler(object):

    def __init__(self, conf):
        self.conf = conf
        self.expid = 'online'
        self.name = 'ocr'

    def get(self, req):
        with free_worker_count.get_lock():
            free_worker_count.value -= 1

        # initialization
        result_list = []
        global_width = []
        global_height = []
        global_square = []
        global_counts = 0

        try:
            #从实时的request中获取信息
            # basic context build
            locations = req.location
            video_list = locations.strip().split(',')
            start_time = time.time()

            for img_name in os.listdir(video_list):
                if img_name.endswith('png') or img_name.endswith('jpg'):
                    print('img_name : ',img_name)
                    #读取图像并转成黑白格式
                    img_rgb = cv2.imread(img_name)
                    img_gray = cv2.cvtColor(img_rgb,cv2.COLOR_BGR2GRAY)
                    img = np.array(img_gray,dtype=np.float32)
                    print('image shape : ', img.shape)
                    #识别
                    result = model.text_predict(img)
                    #打印识别结果
                    for item in result:
                        print('location : x--{}, y--{}, width--{}, height--{}'.format(item['cx'], item['cy'], item['w'], item['h']))
                        print('rotation degree : ', item['degree'])
                        print('text : ', item['text'])
                        tmp = OcrPrediction(degree = item['degree'], location = [item['cx'], item['cy']], width = item['w'], \
                                      height = item['h'], text = item['text'], weight = 1.0)
                        global_counts += 1
                        if len(result_list) != 0:
                            for pred in result_list:
                                #统计text出现频次
                                if pred.text.strip() == tmp.text.strip():
                                    pred.weight += 1
                                else:
                                    result_list.append(tmp)
                                    global_width.append(tmp.width)
                                    global_height.append(tmp.height)
                                    global_square.append(tmp.width*tmp.height)
            global_square = np.array(global_square,dtype=np.float32)
            MEAN = np.mean(global_square)
            GAP = np.max(global_square) - np.min(global_square)
            #归一化计算weights
            if len(result_list) != 0:
                for pred in result_list:
                    square = pred.width * pred.height
                    pred.weight = (pred.weight / global_counts) + ((square - MEAN) / GAP)
            print('Time consumed for ocr prediction: ', float(time.time()-start_time))

            #返回的视频存在result_list中
            print("result return to client: ", result_list)

        except Exception as e:
            FAIL_COUNT.inc()
            print('api:%s', e)
            print(traceback.format_exc())

        with free_worker_count.get_lock():
            free_worker_count.value += 1

        end_time = time.time()
        if not result_list:
            RETURN_EMPTY_COUNT.inc()

        sys.stdout.flush()
        return Rsp(predictions=result_list)


# sort video by weight
def take_weight(elem):
    return elem.weight


def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for interactive debugging."""
    d = {'_frame': frame}  # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    message = "Debug Signal received : \nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    with open("user1.log", "w") as f:
        f.write(message)


def exit_signal_handler(sig=None, frame=None):
    #从数字中获取信号名称
    signal_names = dict(
        (k, v) for v, k in signal.__dict__.iteritems() if v.startswith('SIG'))
    print('catch signal %s, exit ...', signal_names.get(sig, sig))
    #终止所有子进程
    while (multiprocessing.active_children()):
        for p in multiprocessing.active_children():
            p.terminate()
        time.sleep(.1)
    os._exit(0)


def init_handler():
    #将信号的处理方式恢复为默认
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGHUP, signal.SIG_DFL)
    signal.signal(signal.SIGUSR1, debug)


def main():
    print ("start...")
    print('main() server  start on ..., time=%s', str(datetime.datetime.now()))
    signal.signal(signal.SIGINT, exit_signal_handler)
    signal.signal(signal.SIGTERM, exit_signal_handler)
    signal.signal(signal.SIGHUP, exit_signal_handler)
    signal.signal(signal.SIGUSR1, debug)

    service_name = 'ocr_prediction_service'

    init_logging(vulgar_conf)

    global free_worker_count
    free_worker_count.value = vulgar_conf.server_thread_num

    gc.set_threshold(20000, 10, 10)

    global handler
    handler = ServiceHandler(vulgar_conf)
    port = int(vulgar_conf.port[0]) if isinstance(
        vulgar_conf.port, list) else int(vulgar_conf.port)
    processor = Recommend.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TFramedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TProcessPoolServer(processor, transport, tfactory, pfactory)
    server.setNumWorkers(vulgar_conf.server_thread_num)
    server.setPostForkCallback(init_handler)

    print('server %s start on %s ..., time=%s', service_name, port, str(datetime.datetime.now()))
    server.serve()
    print('server %s start on %s ..., time=%s', service_name, port, str(datetime.datetime.now()))


if __name__ == '__main__':
    main()
