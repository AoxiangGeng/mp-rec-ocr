# -*- coding: utf-8 -*- 

"""
A library for emitting and collecting metrics.

The python library is actualy a proxy to metrics library at cpputil::metrics.

The python library additionly support emitting metrics in multi-process 
programs. It creates a multiprocessing.Queue at initialization. All emitted 
metric data are put into the queue, while another stand-alone event_loop 
process consumes the queue and send data to the real MetricCollector.

In single-process programs it works in the same way with multi-process 
programs. So there will always be one more extra process.

Be aware that always call init() and start() methods before creating any
other sub-processes.


Code example:
    import pyutil.program.metrics as metrics
    import pyutil.program.conf
    
    conf_file = pyutil.program.conf.Conf('test_metrics.conf')

    # init metrics library.
    metrics.init(conf_file)
    metrics.define_counter('throughput', 'req');
    metrics.define_timer('latency', 'us');
    metrics.define_store('cpu_usage', 'us');
    metrics.start()

    # emit data anywhere you want.
    metrics.emit_counter('throughput', 1)
    metrics.emit_timer('latency', elapsed_time)
    metrics.emit_store('cpu_usage', cpu_usage)

    # use Timer
    with metrics.Timer('latency'):
        do_something()

    # use timing decorator
    @metrics.timing('latency'):
    def do_something():
        work()

Conf example:
    # 后端类型，支持stdout,file,ganglia,opentsdb. 
    # 多个后端间逗号分隔. 默认为stdout
    metrics_enabled_backends: stdout

    # 本地日志文件名，使用绝对路径
    metrics_backend_file_path_name: /var/log/tiger/example.metrics.log

    # ganglia服务端点，多个端点间逗号分隔
    metrics_backend_ganglia_endpoints: service-m0.gmond.d.byted.org:8600, service-m1.gmond.d.byted.org:8600

    # OpenTSDB服务端点，多个端点间逗号分隔
    metrics_backend_opentsdb_endpoints: 192.168.20.41:8400

    # 汇报周期，单位为秒，默认值为10秒。
    # 约定同一个服务所有metrics使用统一的flush周期，
    # 暂不支持为每个metric设置不同的flush周期
    metrics_flush_interval: 15

    # 查询监听端口.
    metrics_listening_port: 10086

    # 定义本服务所有metric的公共前缀。
    # 所有api中name参数可以省略该前缀。默认为空
    metrics_namespace_prefix: test


"""

import msgpack
import socket
import logging
import functools
import time
import sys
import traceback
import threading
if 'PyPy' not in sys.version:
    from pyutil.bdmonitor.bdmonitor import set_ruler
import pyutil.program.conf as Conf


'''
message format:
    message_type(int16): define_metric, define_alarm, emit_metric, reset_metric
    message_body: ...
        define_metric: 
'''

all_metrics = {}
all_tags = {}
namespace_prefix = None
default_alarm_recipients = None
send_batch_size = 1
udp_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
udp_socket.setblocking(0)
reqs_buffer = threading.local()
reqs_buffer.val = []

def init(conf_obj):
    global namespace_prefix
    global default_alarm_recipients
    global send_batch_size

    if conf_obj.get('metrics_namespace_prefix'):
        namespace_prefix = conf_obj.get('metrics_namespace_prefix')
    default_alarm_recipients = conf_obj.get('metrics_default_alarm_recipients')
    send_batch_size = conf_obj.get('send_batch_size', 1)

def _c(metric_name,prefix):
    global namespace_prefix
    if not prefix:
        return '%s.%s' % (namespace_prefix, metric_name)
    return '%s.%s' % (prefix, metric_name)

def define_tagkv(tagk,tagv_list):
    if isinstance(tagv_list,list):
        if tagk in all_tags :
            all_tags[tagk] = all_tags[tagk].union(set(tagv_list))
        else :
            all_tags[tagk] = set(tagv_list)
    else:
        #logging.warn('tagv_list must list type')
        sys.stderr.write('tagv_list must list type\n')

def define_counter(name, units=None, prefix=None):
    global all_metrics
    cname = _c(name, prefix)
    if cname in all_metrics and all_metrics[cname] != 'counter':
        #logging.warn('metric redefined. %s %s', cname, all_metrics[cname])
        sys.stderr.write('metric redefined. %s %s\n'%(cname, all_metrics[cname]))
        return
    all_metrics[cname] = 'counter'

def define_timer(name, units=None, prefix=None):
    global all_metrics
    cname = _c(name,prefix)
    if cname in all_metrics and all_metrics[cname] != 'timer':
        #logging.warn('metric redefined. %s %s', cname, all_metrics[cname])
        sys.stderr.write('metric redefined. %s %s\n'%(cname, all_metrics[cname]))
        return
    all_metrics[cname] = 'timer'

def define_store(name, units=None, prefix=None):
    global all_metrics
    cname = _c(name, prefix)
    if cname in all_metrics and all_metrics[cname] != 'store':
        #logging.warn('metric redefined. %s %s', cname, all_metrics[cname])
        sys.stderr.write('metric redefined. %s %s\n'%(cname, all_metrics[cname]))
        return
    all_metrics[cname] = 'store'

if 'PyPy' in sys.version:
    def register_alarm(metric_name, condition,
            metric_subfix="avg",
            metric_prefix=None,
            enabled=True,
            recipients=None,
            message=None,
            phones=None,
            silent_mode='fixed',
            silent_interval=60*5,
            rule_type=0,
            tongbi_interval=1,
            opentsdb_aggregator=None,
            opentsdb_downsampler='1m-avg',
            opentsdb_rate=None):
        pass
else:
    def register_alarm(metric_name, condition,
            metric_subfix="avg",
            metric_prefix=None,
            enabled=True,
            recipients=None,
            message=None,
            phones=None,
            silent_mode='fixed',
            silent_interval=60*5,
            rule_type=0,
            tongbi_interval=1,
            opentsdb_aggregator=None,
            opentsdb_downsampler='1m-avg',
            opentsdb_rate=None):
        global all_metrics
        global default_alarm_recipients
        global namespace_prefix
    
        cname = _c(metric_name,metric_prefix)
        if cname not in all_metrics:
            #logging.warn('metric not exist. %s', cname)
            sys.stderr.write('metric not exist. %s\n'%(cname))
            return
        metric_type = all_metrics[cname]
        if metric_type == "timer":
            cname = ".".join([cname,metric_subfix])
    
        req = {}
        req['service_name'] = namespace_prefix
        req['metric_name'] = cname
        req['metric_type'] = metric_type
        req['condition'] = condition
        req['enabled'] = enabled;
        if recipients:
            req['recipients'] = recipients
        else:
            req['recipients'] = default_alarm_recipients
        if phones:
            req['phones'] = phones
        else:
            req['phones'] = ''
        if message:
            req['message'] = message
        req['silent_mode'] = silent_mode
        req['silent_interval'] = silent_interval
        req['rule_type'] = rule_type
        req['tongbi_interva'] = tongbi_interval
        if metric_type == 'counter':
            req['opentsdb_aggregator'] = 'sum'
            req['opentsdb_rate'] = "rate:" 
        else:
            req['opentsdb_aggregator'] = 'avg'
            req['opentsdb_rate'] = "" 
        req['opentsdb_downsampler'] = opentsdb_downsampler
        #print req
        try:
            ret,msg = set_ruler(req)
            #res = set_ruler(req,port=12345)
            #import pdb;pdb.set_trace()
            if ret == 0:
                #logging.warn('fail to set_ruler:%s',msg)
                sys.stderr.write('fail to set_ruler:%s\n'%(msg))
        except Exception as e:
            #logging.warn('set_ruler raise exception %s', e)
            err = traceback.format_exc()
            sys.stderr.write('set_ruler raise exception %s\n'%err)

def _send_message(req):
    global udp_socket, send_batch_size
    server_address = '/tmp/metric.sock'
    reqs = getattr(reqs_buffer, "val", [])
    reqs.append(req)
    if len(reqs) < send_batch_size:
        reqs_buffer.val = reqs
    else:
        reqs_buffer.val = []
        send_buffer = msgpack.dumps(reqs)
        try:
            udp_socket.sendto(send_buffer, server_address)
        except:
            send_batch_size = send_batch_size + 1

def _emit(metric_type, name, value, prefix, tagkv):
    cname = _c(name, prefix)
    def _warn(msg):
        sys.stderr.write('[%s %s] %s\n' % (metric_type, cname, msg))
    # 非关键服务，但调用方很多, catch住异常以防出问题
    try:
        tag_list = []
        is_ok = True
        if cname not in all_metrics:
            _warn('metric not exist. %s' % cname)
            is_ok = False
        elif all_metrics[cname] != metric_type:
            _warn('metric type not matched. %s' % all_metrics[cname])
            is_ok = False
        for tagk, tagv in tagkv.iteritems():
            if tagk not in all_tags:
                _warn('tagk not exist. %s' % tagk)
                is_ok = False
            elif tagv not in all_tags[tagk]:
                    _warn('tagv not exist. %s=%s' % (tagk, tagv))
                    is_ok = False
            if is_ok:
                tag_list.append("=".join([tagk, tagv]))
        if not is_ok:
            return
        req = ['emit', metric_type, cname, str(value), "|".join(tag_list), ""]
        _send_message(req)
    except Exception as e:
        _warn('fail to emit: %s' % e)

def emit_counter(name, value, prefix=None, tagkv={}):
    _emit('counter', name, value, prefix, tagkv)

def emit_timer(name, value, prefix=None, tagkv={}):
    _emit('timer', name, value, prefix, tagkv)

def emit_store(name, value, prefix=None, tagkv={}):
    _emit('store', name, value, prefix, tagkv)

def reset_counter(name, prefix=None,tagkv={}):
    global all_metrics

    cname = _c(name, prefix)
    if cname not in all_metrics:
        #logging.warn('metric not exist. %s', cname)
        sys.stderr.write('metric not exist. %s\n'%(cname))
        return
    if all_metrics[cname] != 'counter':
        #logging.warn('reset metric type not matched. %s', all_metrics[cname])
        sys.stderr.write('reset metric type not matched. %s\n'%(all_metrics[cname]))
        return
    tag_list = []
    for tagk,tagv in tagkv.iteritems():
        #print tagk,tagv
        if tagk not in all_tags:
            #logging.warn('tagk not exist. %s', tagk)
            sys.stderr.write('tagk not exist. %s\n'%(tagk))
            return
        else:
            if tagv not in all_tags[tagk]:
                #logging.warn('tagv not exist. %s', tagv)
                sys.stderr.write('tagv not exist. %s\n'%(tagv))
                return 
        tag_list.append("=".join([tagk,tagv]))


    req = ['reset', 'counter', cname, "|".join(tag_list), ""]

    _send_message(req)

def reset_timer(name, prefix=None, tagkv={}):
    global all_metrics

    cname = _c(name,prefix)
    if cname not in all_metrics:
        #logging.warn('metric not exist. %s', cname)
        sys.stderr.write('metric not exist. %s\n'%(cname))
        return
    if all_metrics[cname] != 'timer':
        #logging.warn('reset metric type not matched. %s', all_metrics[cname])
        sys.stderr.write('reset metric type not matched. %s\n'%(all_metrics[cname]))
        return
    tag_list = []
    for tagk,tagv in tagkv.iteritems():
        #print tagk,tagv
        if tagk not in all_tags:
            #logging.warn('tagk not exist. %s', tagk)
            sys.stderr.write('tagk not exist. %s\n'%(tagk))
            return
        else:
            if tagv not in all_tags[tagk]:
                #logging.warn('tagv not exist. %s', tagv)
                sys.stderr.write('tagv not exist. %s\n'%(tagv))
                return 
        tag_list.append("=".join([tagk,tagv]))


    req = ['reset', 'timer', cname, "|".join(tag_list),""]
    _send_message(req)

def reset_store(name, prefix=None, tagkv={}):
    global all_metrics

    cname = _c(name,prefix)
    if cname not in all_metrics:
        #logging.warn('metric not exist. %s', cname)
        sys.stderr.write('metric not exist. %s\n'%(cname))
        return
    if all_metrics[cname] != 'store':
        #logging.warn('reset metric type not matched. %s', all_metrics[cname])
        sys.stderr.write('reset metric type not matched. %s\n'%(all_metrics[cname]))
        return
    tag_list = []
    for tagk,tagv in tagkv.iteritems():
        #print tagk,tagv
        if tagk not in all_tags:
            #logging.warn('tagk not exist. %s', tagk)
            sys.stderr.write('tagk not exist. %s\n'%(tagk))
            return
        else:
            if tagv not in all_tags[tagk]:
                #logging.warn('tagv not exist. %s', tagv)
                sys.stderr.write('tagv not exist. %s\n'%(tagv))
                return 
        tag_list.append("=".join([tagk,tagv]))


    req = ['reset', 'store', cname, str(value), "|".join(tag_list),""]
    _send_message(req)

def start():
    pass

class Timer(object):
    def __init__(self, metric_name, prefix=None, tagkv={}):
        self.metric_name = metric_name
        self.prefix = prefix
        self.tagkv = tagkv

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        emit_timer(self.metric_name, 1000 * (time.time() - self.start_time), prefix=self.prefix, tagkv=self.tagkv)

def timing(metric_name,prefix=None, tagkv={}):
    '''
    timing decorator for function and method
    '''
    def timing_wrapper(func):
        @functools.wraps(func)
        def f2(*args, **kwargs):
            with Timer(metric_name,prefix, tagkv):
                return func(*args, **kwargs)
        return f2
    return timing_wrapper

if __name__ == "__main__":
    pass
