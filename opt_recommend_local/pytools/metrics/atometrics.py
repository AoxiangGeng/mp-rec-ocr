# -*- coding: utf-8 -*-

import sys
import time
import socket
import functools
import ConfigParser
import threading

# pylint: disable=invalid-name

'''
全局变量
'''
metricPrefix = None
tagsDict = {}
metricsDict = {}
metricsUpdateTimeDict = {}
openTSDBAddr = ""
openTSDBPort = 0
udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setblocking(0)
sendBuffer = threading.local()
sendBuffer.buf = []
# 发送缓冲区大小
sendBufferCap = 1

'''
公共函数
'''
def init(configFilePath):
    """ init: 根据配置文件初始化atometrics """
    global metricPrefix, openTSDBAddr, openTSDBPort

    cf = ConfigParser.ConfigParser()
    cf.read(configFilePath)
    try:
        metricPrefix = cf.get('common', 'metrics_prefix')
    except:
        sys.stderr.write('config file has no metrics_prefix\n')

    openTSDBUrl = cf.get('common', 'opentsdb_addr')
    if openTSDBUrl == "":
        sys.stderr.write('openTSDBUrl empty!!\n')
        sys.exit(-1)
    tokens = openTSDBUrl.split(':')
    if len(tokens) != 2:
        sys.stderr.write('openTSDBUrl invalid: %s!!\n' % openTSDBUrl)
        sys.exit(-1)
    openTSDBAddr = tokens[0]
    openTSDBPort = int(tokens[1])

def newTag(tagName, tagValue):
    """ newTag: 新建tag, tagValue为该tag可选值列表 """
    if not isinstance(tagValue, list):
        sys.stderr.write('tagValue shoube be list type!!\n')
    else:
        if tagName in tagsDict:
            # 追加
            tagsDict[tagName] = tagsDict[tagName].union(set(tagValue))
        else:
            tagsDict[tagName] = set(tagValue)

def newCounter(name, prefix=None):
    """ newCounter: 新建counter """
    fullName = metricFullName(name, prefix)
    if fullName in metricsDict and metricsDict[fullName] != 'counter':
        sys.stderr.write('Creation failed, name in use. %s %s\n'%(fullName, metricsDict[fullName]))
        return
    metricsDict[fullName] = 'counter'

def newGauge(name, prefix=None):
    """ newGauge: 新建gauge """
    fullName = metricFullName(name, prefix)
    if fullName in metricsDict and metricsDict[fullName] != 'gauge':
        sys.stderr.write('Creation failed, name in use. %s %s\n'%(fullName, metricsDict[fullName]))
        return
    metricsDict[fullName] = 'gauge'

def newTimer(name, prefix=None):
    """ newTimer: 新建timer """
    fullName = metricFullName(name, prefix)
    if fullName in metricsDict and metricsDict[fullName] != 'timer':
        sys.stderr.write('Creation failed, name in use. %s %s\n'%(fullName, metricsDict[fullName]))
        return
    metricsDict[fullName] = 'timer'

def counterMark(name, value, prefix, tags={}):
    """ counterMark: counter打点 """
    mark('counter', name, value, prefix, tags)

def gaugeMark(name, value, prefix, tags={}):
    """ gaugeMark: gauge打点 """
    mark('gauge', name, value, prefix, tags)

def timerMark(name, value, prefix, tags={}):
    """ timerMark: timerer打点 """
    mark('timer', name, value, prefix, tags)

class Timer(object):
    """ Timer: decorator使用 """
    def __init__(self, name, prefix=None, tags={}):
        self.name = name
        self.prefix = prefix
        self.tags = tags

    def __enter__(self):
        self.startTime = time.time()

    def __exit__(self, type, value, callback):
        duration = time.time()-self.startTime
        timerMark(self.name, duration*1000, self.prefix, self.tags)

def timing(name, prefix=None, tags={}):
    ''' decorator '''
    def timingWrapper(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            with Timer(name, prefix, tags):
                return func(*args, **kwargs)
        return f
    return timingWrapper


'''
私有函数
'''
def metricFullName(name, prefix):
    """ metricFullName: 拼接完整的metric name """
    if not prefix:
        # 用config文件中的prefix拼接
        return '%s.%s' % (metricPrefix, name)
    return '%s.%s' % (prefix, name)

def sendMetrics(req):
    """ sendMetrics: 发送metrics日志 """
    global sendBufferCap
    reqs = getattr(sendBuffer, "buf", [])
    reqs.append(req)
    if len(reqs) < sendBufferCap:
        sendBuffer.buf = reqs
    else:
        sendBuffer.buf = []
        data = "".join(reqs)
        try:
            #sys.stderr.write('%s\n' % data)
            udpSocket.sendto(data, (openTSDBAddr, openTSDBPort))
        except Exception as e:
            sendBufferCap += 1
            sys.stderr.write('sendMetrics failed:(%s), addr(%s,%d), err:%s\n' % (data, openTSDBAddr, openTSDBPort, e))

def mark(metricType, name, value, prefix, tags):
    """ mark: 打点 """
    fullName = metricFullName(name, prefix)
    try:
        strTagsList = ""
        if fullName not in metricsDict:
            sys.stderr.write('(%s,%s)not exist\n' % (metricType, fullName))
            return
        elif metricsDict[fullName] != metricType:
            sys.stderr.write('(%s,%s)type not match:%s\n'
                             % (metricType, fullName, metricsDict[fullName]))
            return
        for k, v in tags.iteritems():
            if k not in tagsDict:
                sys.stderr.write('(%s,%s)k not exist. %s\n' % (metricType, fullName, k))
                return
            elif v not in tagsDict[k]:
                sys.stderr.write('(%s,%s)v not exist. %s=%s\n' % (metricType, fullName, k, v))
                return
            strTagsList += ' ' + ("=".join([k, v]))

        # tag list不能为空
        if strTagsList == "":
            return

        # 间隔2s以上才能投递
  	'''
        nowTime = time.time()
        if fullName in metricsUpdateTimeDict:
            lastUpdateTime = metricsUpdateTimeDict[fullName]
            if nowTime - lastUpdateTime < 2.0:
                return
        metricsUpdateTimeDict[fullName] = nowTime
	'''

        strReq = 'put '+fullName+' '+str(int(time.time()))+' '+str(value)+strTagsList+'\n'
        sendMetrics(strReq)
    except Exception as e:
        sys.stderr.write('(%s,%s)mark failed: %s\n' % (metricType, fullName, e))

