#!/usr/bin/env python
# coding=utf8
import datetime
import gc
import json
import math
import multiprocessing
import random
import signal
import sys
import time
import traceback
import numpy as np

sys.path.append("opt_recommend_local")

import conf as vulgar_conf
from cityhash import CityHash32
from pytools.program.log import init_logging
from thrift_common.py_iface.recommend import Recommend
from thrift_common.py_iface.recommend.ttypes import Rsp, VideoWeight
from thrift.protocol import TBinaryProtocol
from thrift.server.TProcessPoolServer import TProcessPoolServer
from thrift.transport import TSocket, TTransport
from prometheus_def import *

free_worker_count = multiprocessing.Value('i')

global_useridx_map = {}
global_idxitem_map = {}
global_safecid_map = {}

readUserObj = open(vulgar_conf.user_feature_file)
readItemObj = open(vulgar_conf.content_feature_file)
uvecList = []
vvecList = []
for line in readUserObj:
    tokens = line.strip().split("\t")
    uidx = int(tokens[0])
    vec_str = tokens[1]
    vector = [float(t) for t in vec_str.split(",")]
    global_useridx_map[uidx] = len(uvecList)
    uvecList.append(vector)
readUserObj.close()
for line in readItemObj:
    tokens = line.strip().split("\t")
    vid = tokens[0]
    rmdList = tokens[1].split(",")
    for key in rmdList:
       if key=="11":
          global_safecid_map[vid] = 1
          break
    vec_str= tokens[2]
    vector = [float(t) for t in vec_str.split(",")]
    global_idxitem_map[len(vvecList)] = long(vid)
    vvecList.append(vector)
readItemObj.close()

global_userhash_feature = np.array(uvecList)
global_itemhash_feature = np.array(vvecList)

del uvecList
del vvecList

global_item_sss = np.sqrt(np.sum(np.square(global_itemhash_feature), 1))
global_itemhash_feature_T = global_itemhash_feature.T

def cos_npsim(userNp, itemsNpT, itemSSS):
    tmpUser = np.sqrt(np.sum(np.square(userNp)))
    return np.dot(userNp, itemsNpT) / (1.0+tmpUser * itemSSS)

class ServiceHandler(object):

    def __init__(self, conf):
        self.conf = conf
        self.expid = 'online'
        self.name = 'ucf'

    def get(self, req):
        with free_worker_count.get_lock():
            free_worker_count.value -= 1

        # initialization
        udid = ''
        channel_id = ''
        abtest_parameters = ''

        needsafe = False

        context_info_json = ''
        context_info_dic = {}
        try:
            # basic context build
            udid = req.user.uid
            context_info_json = req.context_info_json
            try:
                context_info_dic = json.loads(context_info_json)
            except:
                pass

            start_time = req.start_time
            tt1 = time.time()
            count = req.count
            filter_counter = 0
            channel_id = req.channel_id
            abtest_parameters = req.abtest_parameters
            abtest_parameters_dic = json.loads(abtest_parameters)

            result_set = set()
            result_list = []
            self.expid = abtest_parameters_dic.get(self.name + '_expid', 'online')

            if abtest_parameters_dic.get('safe_content_only', False):
                needsafe = True

            # history build
            impr_gids_set = set()
            if req.impr_gids != None:
                for impr_id in req.impr_gids:
                    impr_gids_set.add(impr_id)

            idxUid = CityHash32(udid) % 10000000
            if idxUid in global_useridx_map:
                tmpUserVec = global_userhash_feature[global_useridx_map.get(idxUid)]
                tmpItemScore = cos_npsim(tmpUserVec, global_itemhash_feature_T, global_item_sss)
                rltItemIdx = np.argsort(-tmpItemScore) 
                for idx in rltItemIdx[:3000]:
                    content_id = global_idxitem_map[idx]
                    video_weight = tmpItemScore[idx]
                    # 过滤一些数据
                    if content_id in impr_gids_set:
                        filter_counter += 1
                        continue
                    if content_id in result_set:
                        filter_counter += 1
                        continue
                    if needsafe and content_id not in global_safecid_map:
                        filter_counter += 1
                        continue

                    result_list.append(VideoWeight(content_id=content_id, weight=video_weight))
                    result_set.add(content_id)

            result_list = result_list[:req.count]
            print("result return to client: ", result_list)

        except Exception as e:
            FAIL_COUNT.inc()
            print('api:%s', e)
            print(traceback.format_exc())

        with free_worker_count.get_lock():
            free_worker_count.value += 1

        tt2 = time.time()
        if not result_list:
            RETURN_EMPTY_COUNT.inc()

        print('udid:%s, channel_id:%s, request_count=%s, result_length=%d, filter_count =%s, need_safe=%s, abtest_parameters=%s, cost_time=%s' % (
            udid, channel_id, count, len(result_list), filter_counter, needsafe, abtest_parameters, tt2 - tt1))
        print('we get %d videos', len(result_list))
        RETRIEVE_LATENCY.observe(int((tt2 - tt1) * 1000))

        sys.stdout.flush()
        return Rsp(video_list=result_list)


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
    signal_names = dict(
        (k, v) for v, k in signal.__dict__.iteritems() if v.startswith('SIG'))
    print('catch signal %s, exit ...', signal_names.get(sig, sig))
    while (multiprocessing.active_children()):
        for p in multiprocessing.active_children():
            p.terminate()
        time.sleep(.1)
    os._exit(0)


def init_handler():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGHUP, signal.SIG_DFL)
    signal.signal(signal.SIGUSR1, debug)


def main():
    print "start..."
    print('main() server  start on ..., time=%s', str(datetime.datetime.now()))
    signal.signal(signal.SIGINT, exit_signal_handler)
    signal.signal(signal.SIGTERM, exit_signal_handler)
    signal.signal(signal.SIGHUP, exit_signal_handler)
    signal.signal(signal.SIGUSR1, debug)

    service_name = 'ucf_recommend_service'

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
