#!/usr/bin/env python
# coding=utf-8

################################
# 公用client文件
# 不要提交非通用代码
# 请拷贝后修改用于本地处理
################################

import json
import os
import threading
import time
import datetime
import sys
import conf

sys.path.append("opt_recommend_local")
from pytools.thrift.transport import SocketPool
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction
from thrift_common.py_iface.ocr_lite_prediction.ttypes import Req, Rsp, OcrPrediction
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
class Client(threading.local):

    def __init__(self, host, port, timeout=20.0, conn_timeout=1):
        transport = SocketPool.TSocketPool(host, port, timeout, conn_timeout)
        transport = TTransport.TFramedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = Ocr_Lite_Prediction.Client(protocol)
        self.client.transport = transport

    def get_cids(self, req):
        try:
            self.client.transport.open()
            #thrift接口里面的方法
            return self.client.get(req)
        finally:
            self.client.transport.close()

def gen_req():

    return Req(
        location = '/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_5.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_7.png'
    )


def print_result(rsp, count=20):
    print(rsp.videoLocation)
    for item in enumerate(rsp.predictions[:count]):
        line = 'text : {}, weight : ;'.format(item.text,item.weight)
        print(line)

def main():
    req = gen_req()

    tt1 = datetime.datetime.now()
    host = 'localhost'
    #host = '192.168.111.30'
    #port = '80'
    port = int(conf.port[0])
    num = 1
    client = Client(host, port)
    #for i in range(num):
    rsp = client.get_cids(req)
    tt2 = datetime.datetime.now()
    print_result(rsp, 30)
    # print 'return:', rsp
    #print('[ client ] request num',(num),'costtime', tt2 - tt1, 'udid:', req.user.uid, 'result_len=', len(rsp.video_list))

if __name__ == '__main__':
    main()
