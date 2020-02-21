#coding=utf8

import logging, logging.handlers, sys
from multi_process_logger import MultiProcessRotatingFileHandler
from scribe_logger.logger import ScribeLogHandler
import log_rt


WITH_PROCESS_THREAD_FORMAT='%(asctime)s, %(levelname)s %(process)d %(thread)d %(message)s'

# Notice : backend 选择用与的关系，如果日志收集到mfs， backend 参数为1
# 如果日志收集到kafka，backend 参数为2
# 如果日志同时收集到mfs 和 kafka，backend 参数为BACKEND_MFS|BACKEND_KAFKA = 3
BACKEND_MFS = 1
BACKEND_KAFKA = 2

switch_rt_logging = log_rt.switch_rt_logging

def logging_config(log_file, log_level=logging.DEBUG, console_log_level=logging.ERROR, log_format='%(asctime)s %(levelname)-5s %(message)s', category=None, scribe_host='127.0.0.1', scribe_port=1464, name=None, backend=1, kafka_topic=None, scribe_log_level=logging.WARNING):
    '''
    Deprecated, use config_logging or init_logging!
    '''
    logger = logging.getLogger()
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    ch.setFormatter(logging.Formatter(log_format))
    ch.setLevel(console_log_level)
    logger.addHandler(ch)
    if log_file:
        fh = MultiProcessRotatingFileHandler(filename=log_file, when='midnight')
        fh.setFormatter(logging.Formatter(log_format))
        fh.setLevel(log_level)
        logger.addHandler(fh)
    if backend or kafka_topic:
        scribe = ScribeLogHandler(category=category, backend=backend, \
            kafka_topic=kafka_topic, host=scribe_host, port=scribe_port)
        scribe.setFormatter(formatter)
        scribe.setLevel(scribe_log_level)
        logger.addHandler(scribe)



def config_logging(filename=None, format='%(asctime)s, %(levelname)s %(message)s', level=logging.INFO,
                    logger=None, category=None, scribe_host='127.0.0.1', scribe_port=1464, console_log_level=None,
                    name=None, propagate=True, backend=1, kafka_topic=None, scribe_format=None, multi_process_logger_kwargs={},
                    scribe_log_level=logging.WARNING, databus_channel=None, databus_key=None, databus_format=None,
                    sentry_dsn=None, sentry_level=logging.ERROR, file_format=None):
    if logger is None:
        logger = logging.getLogger()
    # need a clean state, for some module may have called logging functions already (i.e. logging.info)
    # in that case, a default handler would been appended, causing undesired output to stderr
    for handler in logger.handlers:
        logger.removeHandler(handler)
    formatter = logging.Formatter(format)
    logger.setLevel(level)
    if not propagate:
        logger.propagate = False
    if filename:
        if 'when' not in multi_process_logger_kwargs:
            multi_process_logger_kwargs['when'] = 'midnight'
        handler = MultiProcessRotatingFileHandler(filename=filename, **multi_process_logger_kwargs)
        file_formatter = formatter
        if file_format:
            file_formatter = logging.Formatter(file_format)
        handler.setFormatter(file_formatter)
        logger.addHandler(handler)
    if category or kafka_topic:
        scribe = ScribeLogHandler(category=category, backend=backend, \
            kafka_topic=kafka_topic, host=scribe_host, port=scribe_port)
        scribe_formatter = formatter
        if scribe_format:
            scribe_formatter = logging.Formatter(scribe_format)
        scribe.setFormatter(scribe_formatter)
        scribe.setLevel(scribe_log_level)
        logger.addHandler(scribe)
    if databus_channel:
        from pyutil.databus import DatabusLogHandler
        databus = DatabusLogHandler(databus_channel, databus_key)
        databus_formatter = formatter
        if databus_format:
            databus_formatter = logging.Formatter(databus_format)
        databus.setFormatter(databus_formatter)
        logger.addHandler(databus)
    if console_log_level is not None:
        ch = logging.StreamHandler()
        formatter = logging.Formatter(format)
        ch.setFormatter(logging.Formatter(format))
        ch.setLevel(console_log_level)
        logger.addHandler(ch)
    if sentry_dsn is not None:
        import raven
        from raven.handlers.logging import SentryHandler
        from raven.transport.registry import TransportRegistry, default_transports
        raven.Raven = None
        raven.Client.logger = logging.getLogger('raven')
        raven.Client._registry = TransportRegistry(transports=default_transports)
        client = raven.Client(sentry_dsn)
        handler = SentryHandler(client)
        handler.setLevel(sentry_level)
        logger.addHandler(handler)

def init_logging(conf):
    log_format = getattr(conf, 'log_format', '') or '%(asctime)s %(levelname)-5s %(message)s'
    console_log_level = getattr(conf, 'console_log_level', logging.ERROR) or logging.ERROR
    log_level = getattr(conf, 'log_level', logging.INFO) or logging.INFO
    scribe_log_level = getattr(conf, 'scribe_log_level', log_level) or log_level
    disable_scribe_log = getattr(conf, 'disable_scribe_log', False) or False
    log_file = getattr(conf, 'log_file', None)
    if isinstance(scribe_log_level, basestring):
        scribe_log_level = eval(scribe_log_level)
    if isinstance(console_log_level, basestring):
        console_log_level = eval(console_log_level)
    if isinstance(log_level, basestring):
        log_level = eval(log_level)
    if isinstance(disable_scribe_log, basestring):
        disable_scribe_log = eval(disable_scribe_log)

    logger = logging.getLogger()
    # need a clean state, for some module may have called logging functions already (i.e. logging.info)
    # in that case, a default handler would been appended, causing undesired output to stderr
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(log_format))
    ch.setLevel(console_log_level)
    logger.addHandler(ch)

    if log_file:
        fh = MultiProcessRotatingFileHandler(log_file, 'midnight', backupCount=1)
        fh.setFormatter(logging.Formatter(log_format))
        fh.setLevel(log_level)
        logger.addHandler(fh)

    # 通过配置文本文件加载的conf, hasattr(conf, 'any_key')始终为真, 故使用getattr代替
    if not disable_scribe_log and getattr(conf, 'log_category', None):
        log_host = getattr(conf, 'log_host', None) or '127.0.0.1'
        log_port = int(getattr(conf, 'log_port', None) or 1464)
        scribe = ScribeLogHandler(category=conf.log_category, host=log_host, port=log_port)
        scribe.setLevel(scribe_log_level)
        scribe.setFormatter(logging.Formatter(log_format))
        logger.addHandler(scribe)
    if getattr(conf, 'log_capture_warning', None) in ['True', '1', True, 1]: # 将warning打印到日志便于分析问题
        logging.captureWarnings(True)

    rt_category = getattr(conf, 'log_rt_category', None)
    if rt_category:
        rt_thread_support = getattr(conf, 'log_rt_thread_support', None) == 'True'
        switch_rt_logging(rt_category=rt_category, thread_support=rt_thread_support)

