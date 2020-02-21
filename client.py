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
from thrift_common.py_iface.recommend import Recommend
from thrift_common.py_iface.recommend.ttypes import Req, Rsp, User, VideoWeight
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
class Client(threading.local):

    def __init__(self, host, port, timeout=20.0, conn_timeout=1):
        transport = SocketPool.TSocketPool(host, port, timeout, conn_timeout)
        transport = TTransport.TFramedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = Recommend.Client(protocol)
        self.client.transport = transport

    def get_cids(self, req):
        try:
            self.client.transport.open()
            #thrift接口里面的方法
            return self.client.get(req)
        finally:
            self.client.transport.close()

def gen_req():
    # 目前真正生效的参数是 uid & count
    #uid_type, uid = 14, 'FD5B854A047639DCFE706BDF7178E484'
    #uid_type, uid = 14, '0BDB850D432B9F38972BD31AB077C8B4'
    #uid_type, uid = 14, '5FE1812451487D9715B9478F25AD355B'
    #uid_type, uid = 14, '6ED3183D368FD1CD9BC49303562D8E71'
    #uid_type, uid = 14, '540AA316E1F5B03DF4497FADDB53D799'
    #uid_type, uid = 14, '57E216737959EC3D2464E0386FB9E786'
    #uid_type, uid = 14, '0001D9171EC7B78697C02D9C6DDB2CDA'
    #uid_type, uid = 14, '0BDB850D432B9F38972BD31AB077C8B4'
    uid_type, uid = 14, 'E9AAB842985D68E7B7E2E249989129D4'
    #global testId
    channel_id = 80
    end_time = time.time()
    #start_time = end_time - 86400
    #start_time = time.time() - 86400*3
    start_time = 0
    count = 1000
    ab_params = {
        'params': {
            'debug': True
        }
    }
    ab_params = json.dumps(ab_params)
    ab_params = '{"set_alpha_score": true, "doc2vec_video_retriever": true, "postclk_alpha": 0.33, "fine_model_recall_ratio": "20", "fine_model_names": "mp_recall_64_staytime", "preclk_alpha": 1, "group_store_version": 2, "fine_model_scores.mp_recall_64_staytime": "1", "preclick_model_name": "mp_recall_128_prec", "safe_content_only": false}'
    req_id = ''
    req_info = {
        'is_support_video': '1',
        #'is_support_live':'1',
        #'is_discover_sort':'1',
        #'is_single_sort':'1',
        #'source_type':'1',
        #'feed_type':'2',
        'location': '北京',
        'facturer' : 'xxxxxx'
    }

    return Req(
        user = User(uid_type=uid_type, uid=uid),
        channel_id=channel_id,
        start_time=start_time,
        end_time=end_time,
        impr_gids=[6448835161097241600],
        count=count,
        video_candidate = [],
        abtest_parameters=ab_params,
        info = req_info,
        context_info_json = json.dumps({"ipinfo": "中国 北京 北京"}),
    )


def print_result(rsp, count=20):
    for idx, v in enumerate(rsp.video_list[:count]):
        line = '%s:%s\t%.3f' % (idx, v.content_id, v.weight)
        print line

def main():
    req = gen_req()

    tt1 = datetime.datetime.now()
    host = 'localhost'
    #host = '192.168.111.30'
    #port = '80'
    port = int(conf.port[0])
    num = 1
    client = Client(host, port)
    for i in xrange(num):
      rsp = client.get_cids(req)
    tt2 = datetime.datetime.now()
    print_result(rsp, 30)
    # print 'return:', rsp
    print '[ client ] request num',(num),'costtime', tt2 - tt1, 'udid:', req.user.uid, 'result_len=', len(rsp.video_list)

if __name__ == '__main__':
    main()
