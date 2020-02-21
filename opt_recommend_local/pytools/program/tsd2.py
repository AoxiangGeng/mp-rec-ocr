#!/usr/bin/python
#coding:utf-8

import time
import requests
import json


TSDB_HOST = ["metrics.byted.org"]
TSDB_PORT = ["80"]
TIMEOUT = 60
RETRY_TIMES = 3

class Tsd():
    def __init__(self):
        self.uri = "/api/query?"
        self.backends = self.get_backends()

    def date_to_timestamp(self, date, end=0):
        if end == 0:
            end = int(time.time())
        date = str(date)
        timestamp = ""
        if date.endswith("d-ago"):
            timestamp = end - int(date.strip("d-ago"))*24*60*60
        elif date.endswith("h-ago"):
            timestamp = end - int(date.strip("h-ago"))*60*60
        elif date.endswith("m-ago"):
            timestamp = end - int(date.strip("m-ago"))*60
        else:
            timestamp = int(date)
        return timestamp

    def get_start_end(self, start, end):
        if end:
            end = self.date_to_timestamp(end)
        else:
            end = int(time.time())
        start = self.date_to_timestamp(start, end)
        start = start - 60
        end = end - 60

        return (start, end)


    def time_filter(self, points, start, end):
        values = {}
        for k in sorted(points.keys()):
            if int(k) >= int(start) and int(k) <= int(end):
                values[k] = points[k]
        return values

    def query(self, start, murl, tags, end=""):
        start, end = self.get_start_end(start, end)
        params = self.get_params(start, murl, tags, end)
        status, data = self._query(params, 0)
        if status != 200:
            status, data = self._query(params, 1)
            if status != 200:
                return None
        points = []
        for p in data:
            points.append(self.time_filter(p['dps'], start, end))
        return points

    def query2(self, start, murl, tags, end=""):
        if end:
            end = self.date_to_timestamp(end)
        else:
            end = int(time.time())
        start = self.date_to_timestamp(start, end)
        start = start - 60
        end = end - 60
        params = self.get_params(start, murl, tags, end)
        status, data = self._query2(params, 0)
        if status != 200:
            status, data = self._query2(params, 1)
            if status != 200:
                return None
        return data

    def _query2(self, params, no, timeout=TIMEOUT):
        from collections import OrderedDict
        r = None
        for i in range(RETRY_TIMES):
            try:
                r = requests.get(self.backends[no] + params, timeout=timeout)
                if r.status_code == 200:
                    return 200, json.loads(r.text, object_pairs_hook=OrderedDict)
                else:
                    return r.status_code, None
            except Exception, e:
                continue
        return 500, None

    def _query(self, params, no, timeout=TIMEOUT):
        r = None
        for i in range(RETRY_TIMES):
            try:
                r = requests.get(self.backends[no] + params, timeout=timeout)
                if r.status_code == 200:
                    return 200, r.json()
                else:
                    return r.status_code, None
            except Exception, e:
                continue
        return 500, None

    def get_params(self, start, murl, tags=None, end=""):
         params = ""
         mtags = ""
         if not tags:
             mtags = ""
         else:
             for k, v in tags.items():
                 if mtags:
                     mtags = "%s,%s=%s" %(mtags, k, v)
                 else:
                     mtags = "%s=%s" %(k, v)
         if mtags:
            mtags = "{%s}" %mtags
         if end:
             params = "start=%s&end=%s&m=%s%s&ascii" %(start, end, murl, mtags)
         else:
             params = "start=%s&m=%s%s&ascii" %(start, murl, mtags)
         return params

    def get_backends(self):
        backends = []
        for i in range(len(TSDB_HOST)):
            backend = "http://%s:%s%s" %(TSDB_HOST[i], TSDB_PORT[i], self.uri)
            backends.append(backend)
        return backends

    def get_timestamps(self, points):
        timestamps = []
        for point in points:
            timestamps.extend(point.keys())
        timestamps = sorted(list(set(timestamps)))
        return timestamps

    def sum(self, start, murl, tags=None, end=""):
        points = self.query(start, murl, tags, end)
        sum = 0
        for point in points:
            for k, v in point.items():
                sum = sum + float(v)
        return sum

    def avg(self, start, murl, tags=None, end=""):
        sum = 0
        num = 0
        points = self.query(start, murl, tags, end)
        if points==[] or points==None:
            return 0
        for point in points:
            for k, v in point.items():
                sum = sum + float(v)
                num = num + 1
        if num == 0:
            return 0
        return sum/num

    def counter_sum(self, start, murl, tags=None, end=""):
        sum = 0

        points = self.query2(start, murl, tags, end)
        start, end = self.get_start_end(start, end)

        for point in points:
            isfirst = True
            a1 = 0
            a2 = 0
            for timek, val in point['dps'].items():
                if int(timek) > end or int(timek) < start:
                    continue
                if isfirst:
                    isfirst = False
                    a1 = val
                    continue
                else:
                    a2 = val
                diff =  a2-a1
                a1 = a2
                if diff < 0.0001:
                    continue
                sum = diff+sum
        return sum


    def sum_rate(self, start, metric_name, tags=None, end=""):
        """
            kwds:metric tags pairs
        """
        murl = "sum:rate:%s" %metric_name
        points = self.query(start, murl, tags, end)
        max = 0
        min = 1000000000
        for point in points:
            for p in point.values():
                if max < p:
                    max = p
                if min > p and p >= 0:
                    min = p
        return min,max

if __name__ == "__main__":
    tsd = Tsd()
    """
    ret = tsd.counter_sum("1h-ago", "sum:data.sort.throughput", {"host":"*"})
    print ret
    ret = tsd.sum("1h-ago", "sum:rate:data.sort.throughput")
    print ret
    ret = tsd.avg("1h-ago", "sum:rate:data.sort.throughput")
    print ret
    """
    ret = tsd.sum_rate("10m-ago", "web.nginx.feed.total", end="5m-ago")
    print ret
