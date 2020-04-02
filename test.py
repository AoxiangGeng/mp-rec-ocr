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
# from pytools.program.log import init_logging
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction
from thrift_common.py_iface.ocr_lite_prediction.ttypes import Rsp, OcrPrediction
from thrift.protocol import TBinaryProtocol
from thrift.server.TProcessPoolServer import TProcessPoolServer
from thrift.transport import TSocket, TTransport
from prometheus_def import *
# from model import *
# from model import text_predict

from config import  *
from crnn import FullCrnn,LiteCrnn,CRNNHandle
from  psenet import  PSENet,PSENetHandel
from angle_class import  AangleClassHandle,shufflenet_v2_x0_5
from utils import  rotate_cut_img,solve,sort_box,draw_bbox,crop_rect
from PIL import Image

# free_worker_count = multiprocessing.Value('i')
# print(free_worker_count)


def crnnRec(im, rects_re, leftAdjust=False, rightAdjust=False, alph=0.2, f=1.0):
    """
    crnn模型，ocr识别
    @@model,
    @@converter,
    @@im:Array
    @@text_recs:text box
    @@ifIm:是否输出box对应的img

    """
    results = []
    im = Image.fromarray(im)
    for index, rect in enumerate(rects_re):

        degree, w, h, cx, cy = rect


        # partImg, newW, newH = rotate_cut_img(im,  90  + degree  , cx, cy, w, h, leftAdjust, rightAdjust, alph)
        partImg = crop_rect(im,  ((cx, cy ),(h, w),degree))
        newW,newH = partImg.size
        partImg_array  = np.uint8(partImg)

        #
        if newH > 1.5* newW:
            partImg_array = np.rot90(partImg_array,1)

        # partImg = Image.fromarray(partImg_array).convert("RGB")

        # partImg.save("./debug_im/{}.jpg".format(index))

        angel_index = angle_handle.predict(partImg_array)

        angel_class = lable_map_dict[angel_index]
        # print(angel_class)
        rotate_angle = rotae_map_dict[angel_class]


        if rotate_angle != 0 :
            partImg_array = np.rot90(partImg_array,rotate_angle//90)
        




        partImg = Image.fromarray(partImg_array).convert("RGB")
        #
        # partImg.save("./debug_im/{}.jpg".format(index))
        
        partImg_ = partImg.convert('L')

        try:

            if crnn_vertical_handle is not None and angel_class in ["shudao", "shuzhen"]:

                simPred =  crnn_vertical_handle.predict(partImg_)
            else:
                simPred = crnn_handle.predict(partImg_)  ##识别的文本
        except :
            continue

        if simPred.strip() != u'':
            #定义结果为字典
            results.append({'cx': cx * f, 'cy': cy * f, 'text': simPred, 'w': newW * f, 'h': newH * f,
                            'degree': degree })
    return results


def text_predict(img):
    #封装Detection+Classification两部分，读取图片进行ocr识别,图片需提前转成黑白格式
    # img = cv2.imread(imgpath)
    preds, boxes_list, rects_re, t = text_handle.predict(img, long_size=pse_long_size)
    #print('Processing img : ', img)

    img2 = draw_bbox(img, boxes_list, color=(0, 255, 0))
    #cv2.imwrite("debug_im/draw.jpg", img2)
    #print('Processing img : ', img)
    result = crnnRec(np.array(img), rects_re)
    #print('Processing img : ', img)
    return result

class ServiceHandler(object):

    def __init__(self, conf):
        self.conf = conf
        self.expid = 'online'
        self.name = 'ocr'

    def get(self, req):
        #with free_worker_count.get_lock():
        #    free_worker_count.value -= 1

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
            print('{} videoshots to be processed......'.format(len(video_list)))
            for img_name in video_list:
                if img_name.endswith('png') or img_name.endswith('jpg'):
                    print('img_name : ',img_name)
                    #读取图像并转成黑白格式
                    img_rgb = cv2.imread(img_name)
                    img_gray = cv2.cvtColor(img_rgb,cv2.COLOR_BGR2GRAY)
                    img = np.array(img_gray,dtype=np.float32)
                    print('image shape : ', img.shape)
                    #识别
                    result = text_predict(img)
                    #打印识别结果
                    if len(result) == 0:
                        print('Empty image')
                        continue
                    for item in result:
                        #print('location : x--{}, y--{}, width--{}, height--{}'.format(item['cx'], item['cy'], item['w'], item['h']))
                        #print('rotation degree : ', item['degree'])
                        print('text : ', item['text'])
                        tmp = OcrPrediction(degree = item['degree'], location = [item['cx'], item['cy']], width = item['w'], \
                                      height = item['h'], text = item['text'], weight = 1.0)
                        global_counts += 1
                        if len(result_list) == 0:
                            result_list.append(tmp)
                            global_width.append(tmp.width)
                            global_height.append(tmp.height)
                            global_square.append(tmp.width*tmp.height)
                        else:
                            for i in range(len(result_list)):
                                #统计text出现频次
                                if result_list[i].text.strip() == tmp.text.strip():
                                    result_list[i].weight += 1
                                    i = -1
                                    break
                            if i == len(result_list) - 1:
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
            #依照权重大小对结果降序排列
            results = sorted(result_list, key = lambda x:x.weight , reverse=True)
            #返回的视频存在result_list中
            print("result return to client: ", results)

        except Exception as e:
            #FAIL_COUNT.inc()
            print('api:%s', e)
            print(traceback.format_exc())

        # with free_worker_count.get_lock():
        #     free_worker_count.value += 1

        end_time = time.time()
        if not results:
            #RETURN_EMPTY_COUNT.inc()
            print('the result list is empty')
        sys.stdout.flush()
        return Rsp(predictions=results)


# sort video by weight
def take_weight(elem):
    return elem.weight


def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for interactive debugging."""
    d = {'_frame': frame}  # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    # message = "Debug Signal received : \nTraceback:\n"
    # message += ''.join(traceback.format_stack(frame))
    # with open("user1.log", "w") as f:
    #     f.write(message)


def exit_signal_handler(sig=None, frame=None):
    #从数字中获取信号名称
    signal_names = dict(
        (k, v) for v, k in signal.__dict__.items() if v.startswith('SIG'))
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

    # init_logging(vulgar_conf)

    # global free_worker_count
    # free_worker_count.value = vulgar_conf.server_thread_num

    gc.set_threshold(20000, 10, 10)

    global handler
    handler = ServiceHandler(vulgar_conf)
    port = int(vulgar_conf.port[0]) if isinstance(
        vulgar_conf.port, list) else int(vulgar_conf.port)
    processor = Ocr_Lite_Prediction.Processor(handler)
    transport = TSocket.TServerSocket(host='localhost',port=port)
    tfactory = TTransport.TFramedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TProcessPoolServer(processor, transport, tfactory, pfactory)
    server.setNumWorkers(vulgar_conf.server_thread_num)
    server.setPostForkCallback(init_handler)

    print('server %s start on %s ..., time=%s', service_name, port, str(datetime.datetime.now()))
    server.serve()
    print('server %s start on %s ..., time=%s', service_name, port, str(datetime.datetime.now()))



if __name__ == '__main__':
    if  pse_model_type == "mobilenetv2":
        text_detect_net = PSENet(backbone=pse_model_type, pretrained=False, result_num=6, scale=pse_scale)


    text_handle = PSENetHandel(pse_model_path, text_detect_net, pse_scale, gpu_id=GPU_ID)
    crnn_net = None

    if crnn_type == "full_lstm" or crnn_type == "full_dense":
        crnn_net  = FullCrnn(32, 1, len(alphabet) + 1, nh, n_rnn=2, leakyRelu=False, lstmFlag=LSTMFLAG)
    elif crnn_type == "lite_lstm" or crnn_type == "lite_dense":
        crnn_net =  LiteCrnn(32, 1, len(alphabet) + 1, nh, n_rnn=2, leakyRelu=False, lstmFlag=LSTMFLAG)



    assert  crnn_type is not None
    crnn_handle  =  CRNNHandle(crnn_model_path , crnn_net , gpu_id=GPU_ID)

    crnn_vertical_handle = None
    if crnn_vertical_model_path is not None:
        crnn_vertical_net = LiteCrnn(32, 1, len(alphabet) + 1, nh, n_rnn=2, leakyRelu=False, lstmFlag=True)
        crnn_vertical_handle = CRNNHandle(crnn_vertical_model_path , crnn_vertical_net , gpu_id=GPU_ID)


    assert angle_type in ["shufflenetv2_05"]



    if angle_type == "shufflenetv2_05":
        angle_net = shufflenet_v2_x0_5(num_classes=len(lable_map_dict), pretrained=False)


    angle_handle = AangleClassHandle(angle_model_path,angle_net,gpu_id=GPU_ID)
    print('Model has been loaded......')

    main()

