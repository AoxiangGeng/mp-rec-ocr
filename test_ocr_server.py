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

#from prometheus_def import *
from model import *
from model import text_predict
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction

from thrift_common.py_iface.ocr_lite_prediction.ttypes import Rsp, OcrPrediction



if __name__ == '__main__':
    """
    img_name = '/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png'
    print('img_name : ',img_name)
    img_rgb = cv2.imread(img_name)
    img_gray = cv2.cvtColor(img_rgb,cv2.COLOR_BGR2GRAY)
    img = np.array(img_gray,dtype=np.float32)
    print(img.shape)
    result = text_predict(img)
    print(result)
   """
    def get():
        # initialization
        result_list = []
        global_width = []
        global_height = []
        global_square = []
        global_counts = 0

        try:
            #从实时的request中获取信息
            # basic context build
            locations = '/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/BGCRZU1039g03fWkyUUy3sd6uiUBJBnh8sHqXw___1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639505830913773568_5.png'
            video_list = locations.strip().split(',')
            print(video_list)
            start_time = time.time()

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
                        print('empty image')
                        continue
                    for item in result:
                        #print('location : x--{}, y--{}, width--{}, height--{}'.format(item['cx'], item['cy'], item['w'], item['h']))
                        #print('rotation degree : ', item['degree'])
                        #print('text : ', item['text'])
                        tmp = OcrPrediction(degree = item['degree'], location = [item['cx'], item['cy']], width = item['w'], \
                                      height = item['h'], text = item['text'], weight = 1.0)
                        global_counts += 1
                        #print(tmp)
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
            print('global_square', global_square)
            MEAN = np.mean(global_square)
            GAP = np.max(global_square) - np.min(global_square)
            #print('result is : ', result_list)
            #归一化计算weights
            if len(result_list) != 0:
                print('length of result : ', len(result_list))
                for pred in result_list:
                    square = pred.width * pred.height
                    pred.weight = (pred.weight / global_counts) + ((square - MEAN) / GAP)
            results = sorted(result_list, key = lambda x:x.weight , reverse=True)
            print('result: ' ,type(results), results)
            print('Time consumed for ocr prediction: ', float(time.time()-start_time))
        except Exception as e:
            print(e)
    get() 
