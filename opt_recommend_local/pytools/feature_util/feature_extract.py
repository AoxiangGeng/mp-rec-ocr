#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import math
import logging
import traceback
import threading
from multiprocessing import Process
from cityhash import CityHash32, CityHash64, CityHash128

class FeatureExtractor(object):
    def __init__(self, mask=[]):
        self.mask_slots = [13,14,20,21,23,24]
        for item in mask:
            self.mask_slots.append(item)
        self.slots = {}
        self.slots['uid'] = 1
        self.slots['cid'] = 2
        self.slots['channel_id'] = 3
        self.slots['c_author_id'] = 4
        self.slots['u_keywords'] = 5
        self.slots['c_category'] = 6
        self.slots['c_keywords'] = 7
        self.slots['hourofday'] = 8
        self.slots['c_author_level'] =9
        self.slots['c_play_num'] = 10
        self.slots['c_ctr'] = 11
        self.slots['c_avg_play_time'] = 12
        self.slots['favourite'] = 13
        self.slots['fullscreen'] = 14
        self.slots['c_duration'] = 15
        self.slots['c_comment_num'] = 16
        self.slots['c_digg'] = 17
        self.slots['c_bury'] = 18
        self.slots['c_digg_bury_rate'] = 19
        self.slots['download'] = 20
        self.slots['comment'] = 21
        self.slots['uid-c_keywords'] = 22
        self.slots['u_keywords-c_keywords'] = 23
        self.slots['user_play_duration'] = 24
        self.slots['c_crawl_digg'] = 25
        self.slots['c_crawl_bury'] = 26
        self.slots['c_crawl_comment_num'] = 27
        self.slots['c_crawl_play_num'] = 28
        self.slots['c_crawl_favorite'] = 29
        self.slots['device_facturer'] = 30
        self.slots['follow'] = 31
        self.slots['c_crawl_digg_bury_rate'] = 32

        self.combine = []
        self.combine.append({"key":"uid-c_keywords","item_a":"uid","item_b":"c_keywords"})
        self.combine.append({"key":"u_keywords-c_keywords","item_a":"u_keywords","item_b":"c_keywords"})

    def is_blank(self, v):
        if v is None or str(v).strip() == "null" or str(v).strip() == "" or (isinstance(v,int) and v < 0):
            return True
        return False

    def loge(self, v):
        if int(v) < 0:
            return v
        return int(math.log(int(v) + 1))

    def get_cityhash_with_slot(self, v, slot, zion_res):
        if self.is_blank(v):
            return
        for item in self.mask_slots:
            if int(slot) == int(item):
                return
        hash_v = CityHash64(str(v)) & 0x003fffffffffffff
        slot = long(slot) << 54
        hash_v = long(hash_v) + slot
        zion_res.append(hash_v)


    def extract(self, group, zion_res):
        for k,v in group.items():
            if isinstance(v, list):
                for item in v:
                    self.get_cityhash_with_slot(item, self.slots[k], zion_res)
            else:
                self.get_cityhash_with_slot(v, self.slots[k], zion_res)

        for combine_item in self.combine:
            list_a = []
            list_b = []
            if isinstance(group[combine_item["item_a"]], list):
                list_a = group[combine_item["item_a"]]
            else:
                list_a.append(group[combine_item["item_a"]])
            if isinstance(group[combine_item["item_b"]], list):
                list_b = group[combine_item["item_b"]]
            else:
                list_b.append(group[combine_item["item_b"]])
            for item_a in list_a:
                for item_b in list_b:
                    if self.is_blank(item_a) or self.is_blank(item_b):
                        continue
                    self.get_cityhash_with_slot(str(item_a) + str(item_b), self.slots[combine_item["key"]], zion_res)


    def extract_feature(self, data):
        user = data.get("user") or {}
        content = data.get("content") or {}
        context = data.get("context") or {}
        union = data.get("union") or {}
        label = data.get("label") or -1
        device = data.get("device") or {}
        zion_res = []

        group = {}
        group['uid'] = user.get("uid") or ""
        group['cid'] = content.get("cid") or ""
        group['channel_id'] = -1 if context.get("channel_id") is None else context.get("channel_id")
        group['c_author_id'] = content.get("author") or ""
        group['u_keywords'] = user.get("keywords") or []
        group['c_category'] = content.get("category") or  ""
        group['c_keywords'] = content.get("keywords") or []
        group['c_author_level'] = -1 if content.get("author_level") is None else content.get("author_level")
        group['c_play_num'] = -1 if content.get("play_num") is None else content.get("play_num")
        group['c_play_num'] = self.loge(group['c_play_num'])
        group['c_ctr'] = -1
        if content.get("click_rate") is not None:
            ctr = float(content.get("click_rate"))
            group['c_ctr'] = int(ctr*100)
        #异常数据
        if group['c_ctr'] >= 100:
            group['c_ctr'] = -1
        group['c_duration'] = -1 if content.get("duration") is None else content.get("duration")
        group['c_duration'] = self.loge(group['c_duration'])
        group['c_avg_play_time'] = -1 if content.get("avg_play_time") is None else content.get("avg_play_time")
        if int(group['c_avg_play_time']) > int(group['c_duration']):
            group['c_avg_play_time'] = group['c_duration']
        group['c_avg_play_time'] = self.loge(group['c_avg_play_time'])
        group['favourite'] = -1
        if union.get('favourite') is not None:
            group['favourite'] = int(union['favourite'])
        group['fullscreen'] = -1
        if union.get("fullscreen") is not None:
            group['fullscreen'] = int(union.get("fullscreen"))
        group['c_comment_num'] = -1 if content.get("comment_num") is None else content.get("comment_num")
        group['c_comment_num'] = self.loge(group['c_comment_num'])
        group['c_digg'] = -1 if content.get("digg") is None else content.get("digg")
        group['c_bury'] = -1 if content.get("bury") is None else content.get("bury")
        group['download'] = -1
        if union.get("download") is not None:
            group['download'] = int(union.get("download"))
        group['comment'] = -1
        if union.get("comment") is not None:
            group['comment'] = int(union.get("comment"))
        group['c_digg_bury_rate'] = -1
        if group['c_bury'] >= 0 and group['c_digg'] >= 0:
            group['c_digg_bury_rate'] = int(float(group['c_digg']+0.1)/float(group['c_bury']+1)*10)
        group['c_digg'] = self.loge(group['c_digg'])
        group['c_bury'] = self.loge(group['c_bury'])
        request_time = -1 if context.get("time") is None else context.get("time")
        if request_time > 0:
            group['hourofday'] = int(request_time + 8*3600)/3600%24
        else:
            group['hourofday'] = -1
        group['user_play_duration'] = -1 if union.get("play_duration") is None else union.get("play_duration")
        group['user_play_duration'] = self.loge(group['user_play_duration'])
        group['c_crawl_digg'] = -1 if content.get("crawl_digg") is None else content.get("crawl_digg")
        group['c_crawl_bury'] = -1 if content.get("crawl_bury") is None else content.get("crawl_bury")
        group['c_crawl_digg_bury_rate'] = -1
        if group['c_crawl_bury'] >= 0 and group['c_crawl_digg'] >= 0:
            group['c_crawl_digg_bury_rate'] = int(float(group['c_crawl_digg']+0.1)/float(group['c_crawl_bury']+1)*10)
        group['c_crawl_bury'] = self.loge(group['c_crawl_bury'])
        group['c_crawl_digg'] = self.loge(group['c_crawl_digg'])
        group['c_crawl_comment_num'] = -1 if content.get("crawl_comment_num") is None else content.get("crawl_comment_num")
        group['c_crawl_comment_num'] = self.loge(group['c_crawl_comment_num'])
        group['c_crawl_play_num'] = -1 if content.get("crawl_play_num") is None else content.get("crawl_play_num")
        group['c_crawl_play_num'] = self.loge(group['c_crawl_play_num'])
        group['c_crawl_favorite'] = -1 if content.get("crawl_favorite") is None else content.get("crawl_favorite")
        group['c_crawl_favorite'] = self.loge(group['c_crawl_favorite'])
        group['device_facturer'] = device.get("facturer") or ""
        group['follow'] = -1
        following = user.get("follow") or []
        for item in following:
            if item == group['c_author_id']:
                group['follow'] = 1

        self.extract(group, zion_res)
        zion_res.sort(key=lambda x:int(x) >> 54)
        return zion_res

    def extract_instance(self, json_str):
        try:
            dict_data = json.loads(json_str)
            if dict_data.get("context") and dict_data.get("context").get('channel_id') and int(dict_data.get("context").get('channel_id')) == 0:
                dict_data["context"]["channel_id"] == 1
            #TODO 小频道脏数据过滤
            #if dict_data.get("context") and dict_data.get("context").get('channel_id') and int(dict_data.get("context").get('channel_id')) == 1:
            #    return None
            result = self.extract_feature(dict_data)
            result_str = [str(v) for v in result]
            result_map = {}
            if dict_data.get("label") and dict_data.get("user") and dict_data.get("user").get('uid') \
                and dict_data.get("context") and dict_data.get("context").get("time") \
                and dict_data.get("user").get("uid_type") \
                and dict_data.get("content") and dict_data.get("content").get("cid"):
                result_map["time"] = dict_data.get("context").get("time")
                result_map["instance"] = "%s '%s:%s#%s#%s | %s" % (dict_data.get("label"), dict_data.get("user").get("uid_type"), dict_data.get("user").get('uid'), dict_data.get("context").get("time"), dict_data.get("content").get("cid"), " ".join(result_str))
                return result_map
            else:
                return None
        except Exception,e:
            logging.info(traceback.print_exc())
            return None

    def extract_instance_from_file(self, filename, out_path):
        logging.info("start process %s...\n", filename)
        data = {}
        try:
            with open(filename, "r") as in_file:
                cnt = 0
                for line in in_file:
                    result_dict = self.extract_instance(line)
                    if not result_dict:
                        continue
                    out_filename = "%sinstance.%s" % (out_path, time.strftime('%Y-%m-%d', time.localtime(float(result_dict["time"]))))
                    if not data.get(out_filename):
                        data[out_filename] = []
                    data[out_filename].append(result_dict["instance"] + "\n")
                    cnt += 1
                    if cnt % 10000 == 0:
                        for (day_filename, lines) in data.items():
                            self.write_file(day_filename, lines)
                        data = {}
            for (day_filename, lines) in data.items():
                self.write_file(day_filename, lines)
        except Exception,e:
            logging.info(traceback.print_exc())
            return None
        logging.info("%s finished! \n", filename)

    def write_file(self, filename, lines):
        with open(filename, "a") as out_file:
            out_file.writelines(lines)

if __name__ == '__main__':
    extractor = FeatureExtractor()
    #json_str = '{"union": {"favourite": false, "fullscreen": false, "download": false, "play_duration": 0, "comment": false}, "label": -1, "content": {"category": "", "crawl_digg": 142,"author_level": null, "cid": 6206311505697181696, "comment_num": 0, "author": 6200214737385425921, "crawl_bury": 52, "crawl_comment_num": 20, "duration": 622, "click_rate": 0.07569721115537849, "keywords": [12904, 36, 9724, 382, 12257, 1959], "avg_play_time": 308, "digg": 0, "bury": 0, "crawl_play_num": 188595, "crawl_favorite": 142, "play_num": 52}, "user": {"keywords": [259, 301, 4369, 124, 1149, 470, 91, 2320, 14967, 1825], "follow": [6183965004237111296], "reg_time": 1477721965, "uid": "05C662E7031755472301653136F8892E", "uid_type":12}, "context": {"channel_id": "104", "time": 1480663678}, "device": {"facturer": "Meizu"}}'
    #json_str = '{ "union": { "favourite": false, "fullscreen": false, "download": false, "comment": false, "playDuration": 0 }, "label": -1, "content": { "category": "video_tech", "crawl_digg": 12, "author_level": 3, "cid": 6206402363545095000, "comment_num": 0, "author": 6183965445767299000, "crawl_bury": 9, "crawl_comment_num": 17, "duration": 133, "click_rate": 0, "keywords": [ 2462, 3001, 1177, 3002 ], "avg_play_time": 37, "digg": 0, "bury": 0, "crawl_play_num": 16891, "crawl_favorite": 12, "play_num": 31 }, "user": { "keywords": [ 111, 222 ], "follow": [], "reg_time": 1479706692, "uid": "0000D52D0079CB58332C2F49C363CBCA" }, "context": { "channel_id": 0, "time": 1479706676 }, "device": { "facturer": "xiaomi" } }'
    #data = {"context":{"channel_id":1}}
    #print extractor.extract_feature(data)
    #print extractor.extract_instance(json_str)
    #extractor.extract_instance_from_file("part-00000", "/mnt/feature_sample/")
    log_file = "./keyword_regen_instance.log"
    logging.basicConfig(filename = log_file, level = logging.DEBUG)
    #path = "/ssd/sample_data/"
    path = "/mnt/SampleByDay_2/"
    path_dir =  os.listdir(path)
    try:
        for filename in path_dir:
            child = os.path.join('%s%s' % (path, filename))
            p = Process(target=extractor.extract_instance_from_file, args=(child, "/mnt/instance/SampleByDay_2/"))
            p.start()
    except Exception,e:
        logging.info(traceback.print_exc())
