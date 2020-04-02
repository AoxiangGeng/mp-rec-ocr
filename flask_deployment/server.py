from flask import Flask, request, Response
import numpy as np
import json
sys.path.append("../opt_recommend_local")
sys.path.append("../chineseocr_lite")
from thrift_common.py_iface.ocr_lite_prediction import Ocr_Lite_Prediction
from thrift_common.py_iface.ocr_lite_prediction.ttypes import Req, Rsp, OcrPrediction

from config import  *
from crnn import FullCrnn,LiteCrnn,CRNNHandle
from  psenet import  PSENet,PSENetHandel
from angle_class import  AangleClassHandle,shufflenet_v2_x0_5
from utils import  rotate_cut_img,solve,sort_box,draw_bbox,crop_rect
from PIL import Image

app = Flask(__name__)
 
 
@app.route('/api/test', methods=['POST'])
def test():
    
    # response = {'message': 'Data type:{},Shape:{}'.format(type(numpy_data), numpy_data.shape)}
    # response_pickled = json.dumps(response)
    # return Response(response=response_pickled, status=200, mimetype="application/json")
 
"""*************"""
    # initialization
    result_list = []
    global_width = []
    global_height = []
    global_square = []
    global_counts = 0

    try:
        #从实时的request中获取信息
        # basic context build
        locations = request.location
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

    except Exception as e:
        #FAIL_COUNT.inc()
        print('api:%s', e)
        print(traceback.format_exc())
    

    return Response(response=Rsp(predictions=results), status=200, mimetype="application/json")
    # return Rsp(predictions=results)

"""*************"""



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


    app.run(debug=True)





