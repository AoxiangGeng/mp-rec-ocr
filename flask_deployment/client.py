import requests
import numpy as np
import json
import sys

sys.path.append("../opt_recommend_local")
sys.path.append("../chineseocr_lite")
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction
from thrift_common.py_iface.ocr_lite_prediction.ttypes import Req, Rsp, OcrPrediction

# from config import  *
# from crnn import FullCrnn,LiteCrnn,CRNNHandle
# from  psenet import  PSENet,PSENetHandel
# from angle_class import  AangleClassHandle,shufflenet_v2_x0_5
# from utils import  rotate_cut_img,solve,sort_box,draw_bbox,crop_rect
# from PIL import Image



addr = 'http://localhost:5000'
test_url = addr + '/api/test'
content_type = 'application/ocr'
headers = {'content-type': content_type}
 
locations = '/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_5.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_7.png'

 
response = requests.post(test_url, location=locations)

print(rsp.videoLocation)
for item in enumerate(response.predictions[:5]):
    line = 'text : {}, weight : ;'.format(item.text,item.weight)
    print(line)