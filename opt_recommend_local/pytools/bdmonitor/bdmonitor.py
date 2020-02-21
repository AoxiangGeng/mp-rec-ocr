#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Overview
========

A small tool to push data to bdmonitor

Usage summary
=============

How to use this to push data to bdmonitor::
"""
from thrift.Thrift import TException

def set_ruler(r, timeout=5000, host='10.4.16.143', port=7731):
        # config
        rule = {}
        rule['service_name'] = r.get('service_name', '')
        rule['metric_name'] = r.get('metric_name', '')
        rule['condition'] = str(r.get('condition', ''))
        rule['message'] = r.get('message', '')
        rule['recipients'] = r.get('recipients', '')
        rule['phones'] = r.get('phones', '')
        if r.get('enabled', True):
            rule['enabled'] = '1'
        else:
            rule['enabled'] = '0'
        rule['silent_mode'] = r.get('silent_mode', 'fixed')
        rule['silent_interval'] = str(r.get('silent_interval', 200))
        rule['rule_type'] = str(r.get('rule_type', 0))
        rule['tongbi_interval'] = str(r.get('tongbi_interval', 1))
        rule['opentsdb_aggregator'] = r.get('opentsdb_aggregator', '')
        rule['opentsdb_downsampler'] = r.get('opentsdb_downsampler', '')
        rule['opentsdb_rate'] = r.get('opentsdb_rate', '')
        rule['start_time'] = r.get('start_time', '1m-ago')
        from pyutil.thrift.thrift_util import ThriftClient
        from ss.bdmonitor import BdMonitor  # @UnresolvedImport
        server = []
        server.append((host, port))
        client = ThriftClient(server, BdMonitor.Client, 5000)
        client.open()
        res = client.set_ruler(rule)
        client.close()
        if res == 1:
            return (True, 'Set Ruler success')
        else:
            return (False, 'Server Exception')

def del_ruler(r, timeout=5000, host='10.4.16.143', port=7731):
        # config
        rule = {}
        rule['service_name'] = r.get('service_name', '')
        rule['metric_name'] = r.get('metric_name', '')
        rule['condition'] = str(r.get('condition', ''))
        rule['message'] = r.get('message', '')
        rule['recipients'] = r.get('recipients', '')
        rule['phones'] = r.get('phones', '')
        if r.get('enabled', True):
            rule['enabled'] = '1'
        else:
            rule['enabled'] = '0'
        rule['silent_mode'] = r.get('silent_mode', 'fixed')
        rule['silent_interval'] = str(r.get('silent_interval', 200))
        rule['rule_type'] = str(r.get('rule_type', 0))
        rule['tongbi_interval'] = str(r.get('tongbi_interval', 1))
        rule['opentsdb_aggregator'] = r.get('opentsdb_aggregator', '')
        rule['opentsdb_downsampler'] = r.get('opentsdb_downsampler', '')
        rule['opentsdb_rate'] = r.get('opentsdb_rate', '')
        rule['start_time'] = r.get('start_time', '1m-ago')
        from pyutil.thrift.thrift_util import ThriftClient
        from ss.bdmonitor import BdMonitor  # @UnresolvedImport
        server = []
        server.append((host, port))
        client = ThriftClient(server, BdMonitor.Client, 5000)
        client.open()
        res = client.del_ruler(rule)
        client.close()
        if res == 1:
            return (True, 'Del Ruler success')
        else:
            return (False, 'Server Exception')

def test_set():
    r = {
        'service_name': 'data.sort_test',
        'metric_name': 'data.sort.throughput.test',
        'condition': '<100',
        'message': 'sort吞吐低',
        'recipients': 'yuyuntao',
        'enabled': True,
        'silent_mode': 'fixed',
        'silent_interval': 200,
        'opentsdb_aggregator': 'sum',
        'opentsdb_downsampler': '1m-avg',
        'opentsdb_rate': 'rate:',
        }
    res = set_ruler(r)
    print res

def test_del():
    r = {
        'service_name': 'data.sort_test',
        'metric_name': 'data.sort.throughput.test',
        'condition': '<100',
        'message': 'sort吞吐低',
        'recipients': 'yuyuntao',
        'enabled': True,
        'silent_mode': 'fixed',
        'silent_interval': 200,
        'opentsdb_aggregator': 'sum',
        'opentsdb_downsampler': '1m-avg',
        'opentsdb_rate': 'rate:',
        }
    res = del_ruler(r)
    print res

def main():
    test_set()
    #import time
    #time.sleep(100)
    test_del()

if __name__ == "__main__":
    main()
