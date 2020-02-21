#!/usr/bin/python
# -*- coding: utf8 -*-
import os
import re
import sys
import pdb
import json
import copy
import time
import urllib
import logging
import datetime
from pyutil.program.tsd import TsdbAnalyze
from django.conf import settings
if not settings.configured:
    settings.configure()

from django.template import Context, Template
import data_stats.stats_report.ranger.mail.mail  as mail

from data_stats.stats_report.ranger.mail.table_helper import DIMEN_SHOW_DICT, METRIC_SHOW_DICT
from data_stats.stats_report.ranger.mail.table_helper import TABLES_TEMPLATE, TABLES_STYLE

class TableModelGen(object):
    def __init__(self, rotate=False, vs_idxs=None, except_metrics=None):
        self.vs_idxs  = vs_idxs
        self.rotate   = rotate
        self.except_metrics = except_metrics or []
        return

    def rebuilding(self, table_data, table_meta):
        table_meta = self.get_table_meta(table_data, table_meta)
        ret_table_data = {}
        if 'idx_list' not in table_meta or not table_meta['idx_list']:
            table_meta['idx_list'] = [isinstance(idx, str) and idx.decode('utf-8') or idx for idx in table_data.keys()]
            table_meta['idx_list'].sort()

        if self.vs_idxs:
            table_data, table_meta['idx_list'] = self.fill_vs_stats_dict(table_data, table_meta['idx_list'], self.vs_idxs, self.except_metrics)

        # filter invalid idx & head
        ret_table_meta = copy.deepcopy(table_meta)
        idx_list1 = [isinstance(idx, str) and idx.decode('utf-8') or idx for idx in table_data.keys()]
        idx_list2 = [isinstance(idx, str) and idx.decode('utf-8') or idx for idx in table_meta['idx_list']]
        ret_table_meta['idx_list'] = [idx for idx in idx_list2 if idx in idx_list1]

        head_list2 = [isinstance(h, str) and h.decode('utf-8') or h for h in table_meta['head_list']]
        for idx, idx_stats in table_data.iteritems():
            head_list1 = [isinstance(h, str) and h.decode('utf-8') or h for h in idx_stats.keys()]
            ret_table_meta['head_list'] = [h for h in head_list2 if h in head_list1]
            break

        # rotate if neccessary
        if self.rotate:
            for k1, stats1 in table_data.iteritems():
                for k2, v in stats1.iteritems():
                    if k2 not in ret_table_data:
                        ret_table_data[k2] = {}
                    ret_table_data[k2][k1] = v

            idx_list                    = ret_table_meta['idx_list']
            ret_table_meta['idx_list']  = ret_table_meta['head_list']
            ret_table_meta['head_list'] = idx_list
            ret_table_meta['head_dict'] = copy.deepcopy(table_meta['idx_dict'])
            ret_table_meta['idx_dict']  = copy.deepcopy(table_meta['head_dict'])
        else:
            ret_table_data = copy.deepcopy(table_data)

        for k1 in ret_table_data.keys():
            kk1 = isinstance(k1, str) and k1.decode('utf-8') or k1
            for k2 in ret_table_data[k1].keys():
                kk2 = isinstance(k2, str) and k2.decode('utf-8') or k2
                keep2 = copy.deepcopy(ret_table_data[k1][k2])
                if type(k2) != type(kk2) or k2 != kk2:
                    del ret_table_data[k1][k2]
                ret_table_data[k1][kk2] = keep2

            keep1 = copy.deepcopy(ret_table_data[k1])
            if type(k1) != type(kk1) or k1 != kk1:
                del ret_table_data[k1]
            ret_table_data[kk1] = keep1

        return ret_table_data, ret_table_meta

    def value_format(self, value, idx):
        if isinstance(value, float):
            if isinstance(idx, basestring) and idx.endswith('%'):
                value = "%.2f%%" % (value*100)
            else:
                value = "%.4f" % (value)

        elif isinstance(value, long) or isinstance(value, int):
            value = format(value, ',')
        else:
            pass

        return value

    def datadict_to_datalist(self, data_in_dict, table_meta):
        data_in_dict, table_meta = self.rebuilding(data_in_dict, table_meta)

        data_in_list = []
        for idx in table_meta['idx_list']:
            if idx not in data_in_dict.keys():
                continue
            idx_data = data_in_dict.get(idx, {})
            mlist = [{table_meta['head_dict'].get(h, h):idx_data.get(h, 0)} for h in table_meta['head_list'] if h in idx_data.keys()]
            data_in_list.append({table_meta['idx_dict'].get(idx, idx):mlist})

        return data_in_list

    def get_head_and_content(self, table_data):
        table_head    = []
        table_content = []
        for td in table_data:
            if not table_head:
                table_head.append("数据指标")
                table_head += [minfo.keys()[0] for minfo in table_data[0].values()[0]]

            row = []
            row.append(td.keys()[0])
            row += [minfo.values()[0] for minfo in td.values()[0]]
            if len(table_head) != len(row):
                logging.error('row not match table_head: %s, %s' % (table_head, row))
                print 'row not match table_head: %s, %s' % (table_head, row)
                continue

            row = [self.value_format(row[i], table_head[i]) for i in xrange(len(table_head))]
            table_content.append(row)

        return table_head, table_content

    def fill_vs_stats_dict(self, stats, idx_list, vs_idxs, except_metrics):
        stats_list = []
        for idx in idx_list:
            stat = copy.copy(stats.get(idx, {}))
            stat.update({'index': idx})
            stats_list.append(stat)

        vs_stats = []
        for vs_idx in vs_idxs:
            vs_stat = self.get_vs_stats_list(stats_list, vs_idx=vs_idx, except_metrics=except_metrics+['index'])
            vs_stat.update({'index': 'vs_%s' % vs_idx})
            vs_stats.append(vs_stat)

        pos = 1
        for vs_stat in vs_stats:
            stats_list.insert(pos, vs_stat)
            pos += 1

        idx_list  = [stat.get('index', '') for stat in stats_list]
        ret_stats = dict([(stat['index'], dict([(key, stat[key]) for key in stat.keys() if key not in ['index']])) for stat in stats_list])
        return ret_stats, idx_list

    def get_vs_stats_list(self, stats, vs_idx, except_metrics):
        if not stats or not isinstance(stats, list):
            return None

        #fill info the same time n day ago
        base_stat = stats[0]
        vsto_stat = stats[vs_idx]
        ret_stat = {}

        for k, v in base_stat.iteritems():
            if k in except_metrics:
                continue

            ret_stat[k]  = ''
            if k not in vsto_stat:
                vsto_stat[k] = 0
            if isinstance(base_stat[k], int):
                base_stat[k] = long(base_stat[k])
            if isinstance(vsto_stat[k], int):
                vsto_stat[k] = long(vsto_stat[k])
            if type(base_stat[k]) == type(vsto_stat[k]):
                ret_stat[k]  = (k in vsto_stat and vsto_stat[k] != 0 and base_stat[k] != 0) and \
                    str('%.2f'%((float(float(base_stat[k]) - float(vsto_stat[k]))/float(vsto_stat[k]))*100)) + "%" or ""
            else:
                logging.info('k: %s, can not vs: %s, %s' % (k, base_stat[k], vsto_stat[k]))

        return ret_stat

    def get_table_meta(self, table_data, table_meta):
        if not table_meta:
            table_meta = {}

        table_meta.setdefault('table_name', '')
        table_meta.setdefault('idx_list',   [])
        table_meta.setdefault('head_list',  [])
        table_meta.setdefault('idx_dict',   {})
        table_meta.setdefault('head_dict',  {})

        if not table_meta['idx_list']:
            table_meta['idx_list'] = table_data.keys()
            table_meta['idx_list'].sort(reverse=True)
        if not table_meta['head_list']:
            table_meta['head_list'] = table_data.values()[0].keys()
            table_meta['head_list'].sort(reverse=True)

        return table_meta

    def build_table_info(self, table_data, table_meta=None):
        if isinstance(table_data, dict):
            table_data = self.datadict_to_datalist(table_data, table_meta)
        table_head, table_content = self.get_head_and_content(table_data)
        return table_head, table_content

    ''' input:
    stats = {'dim1':{'metric1':1,'metric2':2, ...}, 'dim2':{...}, ...}
    or
    stats = [{'dim1':[{'metric1':1},{'metric2':2}, ...]}, {'dim2':[...]}, ...}
    '''
    ''' output:
    richtablemodel like this: {
        'table_name'   : 'stats table',
        'table_head'   : ['','head1','head2',],
        'table_content':[
            ['index1','data11','data12',],
            ['index2','data21','data22',],],
        'table_instraction':'this is a table'
    }
    '''
    def gen_table(self, stats, table_meta=None, table_name='', table_instraction=''):
        table_model  = {}
        if table_name:
            table_model['table_name'] = table_name
        else:
            table_model['table_name'] = table_meta.get('table_name', '')

        table_model['table_head'], table_model['table_content'] = self.build_table_info(stats, table_meta)
        table_model['table_instraction'] = table_instraction
        if not table_model['table_content']:
            return {}
        return table_model

    def get_table_model(self, stats, table_meta=None, table_name='', table_instraction=''):
        return self.gen_table(stats, table_meta, table_name, table_instraction)

    def get_mail_content(self, stats, table_meta=None, table_name='', table_instraction=''):
        tmodel = self.get_table_model(stats, table_meta, table_name, table_instraction)
        mail_content = {'mtype':'richtable', 'model':tmodel}
        return mail_content

class TableMailDeliver(object):
    def __init__(self, tables_style=TABLES_STYLE, tables_template=TABLES_TEMPLATE):
        self.tables_style    = tables_style
        self.tables_template = tables_template

    def render(self, data_models, is_safe=False):
        if is_safe:
            t = Template("{% autoescape off %}"+self.tables_template+"{% endautoescape %}")
        else:
            t = Template(self.tables_template)
        c = Context({
            "data_models" : data_models,
            "styles"      : self.tables_style,
        })
        table = t.render(c)
        return table

    def send_mail(self, subject, mail_list, mail_content):
        if not mail_content:
            print 'tables is None'
            return
        contents = [{'type':'html', 'content':mail_content},]
        mail.send(subject, contents, mail_list)

    '''
    data_models = [
        {'mtype': 'text',  'model': 'this is Text Testing',},
        {'mtype': 'table', 'model': [
            ['TableTesting','head1','head2',],
            ['index1','data11','data12',],
            ['index2','data21','data22',],],},
        {'mtype': 'richtable', 'model' :{
            'table_name'   : 'RichTableTesting',
            'table_head'   : ['','head1','head2',],
            'table_content':[
                ['index1','data11','data12',],
                ['index2','data21','data22',],],
            'table_instraction':'this is a table'},},]
    '''
    def send_models(self, subject, data_models, mail_list, is_safe=False):
        mail_content = self.render(data_models, is_safe)
        mail_content = mail_content.replace("&lt;", "<")
        mail_content = mail_content.replace("&gt;", ">")
        mail_content = mail_content.replace("&quot;", "\"")
        self.send_mail(subject, mail_list, mail_content)

    '''
    stats = {'dim1':{'metric1':1,'metric2':2, ...}, 'dim2':{...}, ...}
    or
    stats = [{'dim1':[{'metric1':1},{'metric2':2}, ...]}, {'dim2':[...]}, ...]
    '''
    def send_stats(self, subject, stats, mail_list):
        model_gen   = TableModelGen()
        tmodel      = model_gen.gen_table(stats, table_name=subject)
        data_models = [{'mtype':'richtable', 'model':tmodel}]
        self.send_models(subject, data_models, mail_list)

class TsdTable():
    def __init__(self):
        self.tsd_host = "10.4.21.105"
        self.tsd_port = 8406
        self.tsd = TsdbAnalyze(host=self.tsd_host, port=self.tsd_port) 

    def get_data(self, start, end, metric_name, murl):
        try:
            ret = self.tsd.query(start, end, metric_name, murl)
            value = self.tsd.average_all(ret, only_number=True)
        except:
            value = 0
        if not value:
            return 0
        return value

    def all_get_data(self, metric_name, murl):
        one_day_seconds = 60*60*24
        one_week_seconds = one_day_seconds * 7
        one_month_seconds = one_day_seconds * 31
        cur_end = int(time.time())
        cur_start = cur_end - one_day_seconds

        last_month_end = cur_end - one_month_seconds
        last_month_start = last_month_end - one_day_seconds

        last_month_value = self.get_data(last_month_start, last_month_end, metric_name, murl)
        last_month_value = float('%0.3f' %last_month_value)
        d = datetime.datetime.now()
        date = datetime.datetime(d.year, d.month-1, d.day).strftime("%Y-%m-%d")

        return (date, last_month_value)

    def multi_get_data(self, metric_name, murl, date="", days=7):
        """
            date="2011-09-28"
        """
        one_day_seconds = 60*60*24
        d = datetime.datetime.now()
        if not date:
            date = (d - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        cur_start = int(time.mktime(time.strptime(date,'%Y-%m-%d')))
        cur_end = cur_start + one_day_seconds
        values = []

        for day in range(days):
            local_time = time.localtime(cur_start)
            date = time.strftime('%Y-%m-%d', local_time)
            value = self.get_data(cur_start, cur_end, metric_name, murl)
            value = float('%0.3f' %value)
            values.append((date, value))
            cur_start = cur_start - one_day_seconds
            cur_end = cur_end - one_day_seconds
        return values
        

    def send_stats(self, name, statlist, mails, date="", days=7):
        tsdb_pre_url = "http://%s:%s/#start=1d-ago&m=" %(self.tsd_host, self.tsd_port) 
        stats = []
        for stat in statlist:
            subject = stat[0]
            metric_name = stat[1]
            murl = stat[2]
            tsdb_url = "%s%s:%s" %(tsdb_pre_url, murl, metric_name)
            subject = "<a href=\"%s\">%s" %(tsdb_url, subject)
            values = self.multi_get_data(metric_name, murl, date, days)
            stat = []
            for value in values:
                stat.append({value[0]:value[1]})
            value = self.all_get_data(metric_name, murl)
            stat.append({"%s(上月同期)" %value[0]: value[1]})
            stats.append({subject:stat})
            
        tmail = TableMailDeliver()
        tmail.send_stats(name, stats, mails)

if __name__ == "__main__":
    table = TsdTable()
    table.send_stats("xx", [("aa", "data.sort.throughput", "sum:rate")], ["222@163.com"])
