import requests
import numpy as np
import json
import sys

sys.path.append("opt_recommend_local")
sys.path.append("chineseocr_lite")
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

location = '/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506254450397184_2.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_7.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/UXCeQqJFHxTVyViXtG9xHbBWeUTjAeaYIHopQg___2.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/BGCRZU1039g03fWkyUUy3sd6uiUBJBnh8sHqXw___1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/EVWquiYWCyWMQEPF8BkM4au-_aXoq5DtWutDxg___11.png'
    # locations = {'location':'/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_5.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_7.png'}
# js = json.dumps({'location':'/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6636999244068691968_1.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_5.png,/home/pipline/aoxiang/ocr/Personal_Temporary_Repo/videoshots/6639506626095091712_7.png'})
 
response = requests.post(test_url, data=location, headers=headers)

rsp = response.text.encode('latin-1').decode('unicode_escape')
print(rsp)
# print(response.videoLocation)
# for item in enumerate(response.predictions[:5]):
#     line = 'text : {}, weight : ;'.format(item.text,item.weight)
#     print(line)