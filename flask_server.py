from flask import Flask, request, Response
import sys
import os
import datetime
import gc
import json
import math
import multiprocessing
import random
import signal
import time
import traceback
import numpy as np
import cv2
sys.path.append("opt_recommend_local")
sys.path.append("chineseocr_lite")
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction
from thrift_common.py_iface.ocr_lite_prediction.ttypes import Req, Rsp, OcrPrediction

from config import  *
from crnn import FullCrnn,LiteCrnn,CRNNHandle
from psenet import  PSENet,PSENetHandel
from angle_class import  AangleClassHandle,shufflenet_v2_x0_5
from utils import  rotate_cut_img,solve,sort_box,draw_bbox,crop_rect
from PIL import Image

app = Flask(__name__)
 
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

 
@app.route('/api/test', methods=['POST'])
def test():
    
    # response = {'message': 'Data type:{},Shape:{}'.format(type(numpy_data), numpy_data.shape)}
    # response_pickled = json.dumps(response)
    # return Response(response=response_pickled, status=200, mimetype="application/json")


    # initialization
    result_list = []
    global_width = []
    global_height = []
    global_square = []
    global_counts = 0

    try:
        #从实时的request中获取信息
        # basic context build
        print('Start ##############')
        print(request)
        print(type(request.data.decode()), request)
        locations = request.data.decode()
        # rj = json.loads(r)
        # locations = rj['location']
        # locations = json.loads(request.json.decode())['location']
        print('locations : ', locations)
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


                preds, boxes_list, rects_re, t = text_handle.predict(img, long_size=pse_long_size)
                #print('Processing img : ', img)
                img2 = draw_bbox(img, boxes_list, color=(0, 255, 0))
                #cv2.imwrite("debug_im/draw.jpg", img2)
                #print('Processing img : ', img)
                result = crnnRec(np.array(img), rects_re)


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

        outputs = {}
        for item in results:
            optput[item.text] = item.weight

    except Exception as e:
        #FAIL_COUNT.inc()
        print('api:%s', e)
        print(traceback.format_exc())
    

    return Response(response=json.dumps(outputs), status=200, mimetype="application/json")
    # return Rsp(predictions=results)





if __name__ == '__main__':

    print('Start ! ')
    if  pse_model_type == "mobilenetv2":
        text_detect_net = PSENet(backbone=pse_model_type, pretrained=False, result_num=6, scale=pse_scale)

    # print('pse_model_path, text_detect_net, pse_scale')
    # print(pse_model_path, text_detect_net, pse_scale)
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


    app.run(host="0.0.0.0", port=5000)





