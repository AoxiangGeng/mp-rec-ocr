#!/usr/bin/env python

import os
import sys
import time
import json
import logging
import requests
import memcache


MC_HOST = "10.4.16.37"
MC_PORT = 11211

class AmsClient():
    def __init__(self):
        self.disk_cache = DiskCache()
        self.mc = memcache.Client(['%s:%s' % (MC_HOST, MC_PORT)], debug=0)

    def get(self, tags):
        hosts = []
        if "common" in tags:
            js = self.disk_cache.load()
            if not js:
                post_data = {
                        'token': 'e97f9912fe49a03f0cf639a009fc96eb',
                        'method': 'host.get',
                        }
                resp = requests.post("https://ams.byted.org/api.php", data=post_data, verify=False)
                if resp.status_code != 200:
                    return None
                js = resp.json()
            self.disk_cache.dump(json.dumps(js))
            for tag in js["response"].keys():
                if tag.startswith("aws"):
                    continue
                hosts.extend(js["response"][tag]["host"])
            hosts = list(set(hosts))
            return hosts
        for tag in tags:
            post_data = {
                    'token': 'e97f9912fe49a03f0cf639a009fc96eb',
                    'method': 'host.get',
                    'tag': tag
                    }
            resp = requests.post("https://ams.byted.org/api.php", data=post_data, verify=False)
            if resp.status_code != 200:
                return None
            js = resp.json()
            hosts.extend(js["response"][tag]["host"])
        return list(set(hosts))

    def get_mc(self, tags):
        hosts = []
        for tag in tags:
            tag = str(tag).replace(" ", "")
            host = self.mc.get(tag)
            if not host:
                continue
            hosts.extend(json.loads(host))
        return hosts

class DiskCache():
    def __init__(self, cache_dir="/tmp/.ams_info"):
        self.cache_dir = cache_dir
        now = int(time.time())
        m_time = 0
        try:
            stat = os.stat(self.cache_dir)
            m_time = int(stat.st_mtime)
        except:
            pass
        self.update = False
        if now - m_time >= 600:
            self.update = True

    def load(self):
        if self.update:
            return {}
        cache_file = open(self.cache_dir, 'r')
        res = cache_file.read()
        if not res:
            return {}
        return json.loads(res)

    def dump(self, ams_infos):
        if not self.update:
            return 
        with open(self.cache_dir, 'w+') as cache_file:
            cache_file.truncate()
            cache_file.write(ams_infos)

if __name__ == "__main__":
    h = AmsClient()
    #print h.get(["data.sort"])
    print h.get_mc(["inf.cassandra.data"])
