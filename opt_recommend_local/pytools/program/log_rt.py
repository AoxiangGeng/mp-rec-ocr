__author__ = 'wangfengkun'

import logging
import os
import time
import threading

from pytools.program.conf2 import Conf
from pytools.redis.redis_proxy import make_redis_proxy_cli2


if __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)


class LogConfig():
    REDIS_TIMEOUT = 0.015

    REDIS_KEY_CATEGORY_LIST = "LOG_CONF_CATEGORY_LIST"
    REDIS_KEY_CATEGORY_CONF_TEMPLATE = "LOG_CONF_CATEGORY_%s"

    REDIS_CONF_TIMEOUT = 86400
    REDIS_DELTA_TIMEOUT = 43200
    REDIS_SYNC_TIME = 5
    REDIS_SYNC_TIME_WITHOUT_THREAD = 60

    def __init__(self, redis_client=None):
        self._log_conf_dict = {}
        self.redis_client = redis_client or self._init_redis()
        self.lock = threading.RLock()
        self._last_sync_time = 0

    def _init_redis(self):
        conf = Conf('/etc/ss_conf/redis.conf')
        return make_redis_proxy_cli2(conf.get_values('redis_ad_persistent_cluster'),
                                     connection_kwargs={'socket_timeout': self.REDIS_TIMEOUT},
                                     cluster='redis_ad_persistent_cluster')

    def _sync_redis(self):
        try:
            category_list = self.redis_client.smembers(self.REDIS_KEY_CATEGORY_LIST)
            if not category_list:
                return
            log_conf_dict = {}
            for category in category_list:
                category_conf_key = self.REDIS_KEY_CATEGORY_CONF_TEMPLATE % category
                category_conf = self.redis_client.hgetall(category_conf_key)
                if category_conf:
                    conf = {}
                    for k, v in category_conf.items():
                        a, b = v.split('|')
                        t, level = int(a), int(b)
                        if int(time.time()) - t > self.REDIS_CONF_TIMEOUT:
                            self.redis_client.hdel(category_conf_key, k)
                            continue
                        conf[k] = (t, level)
                    if conf:
                        log_conf_dict[category] = conf
                    else:
                        self.redis_client.srem(self.REDIS_KEY_CATEGORY_LIST, category)
            self._log_conf_dict = log_conf_dict
        except:
            pass

    def _start_cron(self, thread_support):
        sync_time = self.REDIS_SYNC_TIME if thread_support else self.REDIS_SYNC_TIME_WITHOUT_THREAD
        with self.lock:
            if self._last_sync_time == 0:
                thread_support = False  # sync redis in the same thread for the first time
            if time.time() - self._last_sync_time < sync_time:
                return
            self._last_sync_time = time.time()

        if thread_support:
            thread = threading.Thread(target=self._sync_redis)
            thread.setDaemon(True)
            thread.start()
        else:
            self._sync_redis()


    def _key_by_file_location(self, file_name, line_number):
        return '%s:%s' % (file_name, line_number)

    @property
    def log_conf_dict(self):
        self._start_cron(False)
        return self._log_conf_dict

    def remove_category(self, category):
        category_conf_key = self.REDIS_KEY_CATEGORY_CONF_TEMPLATE % category
        self.redis_client.delete(category_conf_key)

    def get_log_level(self, category_name, file_name, line_number, default_level, set_default=False,
                      thread_support=True):
        try:
            self._start_cron(thread_support)

            if category_name not in self._log_conf_dict:
                self._log_conf_dict[category_name] = {}
                self.redis_client.sadd(self.REDIS_KEY_CATEGORY_LIST, category_name)

            log_conf = self._log_conf_dict[category_name]
            key = self._key_by_file_location(file_name, line_number)

            t = int(time.time())
            if set_default or key not in log_conf or log_conf[key][0] + self.REDIS_DELTA_TIMEOUT < t:
                level = log_conf[key][1] if (key in log_conf and not set_default) else default_level
                value = (t, level)
                log_conf[key] = value
                category_conf_key = self.REDIS_KEY_CATEGORY_CONF_TEMPLATE % category_name
                self.redis_client.hset(category_conf_key, key, '%s|%s' % value)

            return log_conf[key][1]
        except:
            return default_level


class LogProxy():
    log_config = LogConfig()

    def __init__(self, category, logger, is_root, thread_support):
        self.category = category
        self.logger = logger
        self.is_root = is_root
        self.thread_support = thread_support

    def _findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv

    def _find_level(self, default_level):
        filename, lineno, _ = self._findCaller()
        return self.log_config.get_log_level(
            category_name=self.category, file_name=filename,
            line_number=lineno, default_level=default_level, thread_support=self.thread_support)

    def critical(self, msg, *args, **kwargs):
        self._log_it(self._find_level(logging.CRITICAL), msg, *args, **kwargs)

    fatal = critical

    def error(self, msg, *args, **kwargs):
        self._log_it(self._find_level(logging.ERROR), msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs['exc_info'] = 1
        self._log_it(self._find_level(logging.ERROR), msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log_it(self._find_level(logging.WARNING), msg, *args, **kwargs)

    warn = warning

    def info(self, msg, *args, **kwargs):
        self._log_it(self._find_level(logging.INFO), msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log_it(self._find_level(logging.DEBUG), msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self._log_it(self._find_level(level), msg, *args, **kwargs)

    def _log_it(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        if not isinstance(level, int):
            if self.logger.raiseExceptions:
                raise TypeError("level must be an integer")
            else:
                return
        if self.is_root and len(self.logger.handlers) == 0:
            logging.basicConfig()
        if self.logger.isEnabledFor(level):
            self.logger._log(level, msg, args, **kwargs)


def switch_rt_logging(rt_category, logger=None, thread_support=False):
    is_root = not logger
    if not logger:
        logger = logging.getLogger()

    rt_log_proxy = LogProxy(rt_category, logger, is_root, thread_support)
    logx = logging if is_root else logger
    logx.critical = rt_log_proxy.critical
    logx.fatal = rt_log_proxy.fatal
    logx.error = rt_log_proxy.error
    logx.exception = rt_log_proxy.exception
    logx.warning = rt_log_proxy.warning
    logx.warn = rt_log_proxy.warn
    logx.info = rt_log_proxy.info
    logx.debug = rt_log_proxy.debug
    logx.log = rt_log_proxy.log


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    switch_rt_logging('foo', thread_support=True)
    logging.info('xxxx')
