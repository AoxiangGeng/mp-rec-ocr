#!/usr/bin/env python
#! -*- coding: utf8 -*-
import sys

# Conf in conf.py is an alias for Conf in conf2.py
from pytools.program.conf2 import Conf as Conf

def string2list(s, sep=','):
    return [i.strip() for i in s.split(sep)]

# simulate cpputil::Conf interface
class ConvertedConf:
    def __init__(self, conf):
        self.conf = conf
    def get(self, key, val=''):
        _key = str(key).lower()
        if _key not in self.conf:
            return val
        return self.conf[_key]
    def get_values(self, key):
        val = self.get(key)
        vals = [v.strip() for v in val.split(',')]
        return vals
    def get_all(self):
        return self.conf

# convert cpputil::Conf (cpp) to ConvertedConf (py)
def cpp2py(conf):
    result = {}
    for k in conf.get_all():
      result[k] = conf.get(k)
    return ConvertedConf(result)

# Don't used this! Always use conf2
class _Conf(object):
    #缓存相同配置文件解析结果
    CacheHash = {}

    def __init__(self, filename, use_translate=True):
        exe_info = sys.version.lower()
        conf_obj = _Conf.CacheHash.get(filename, None)
        if conf_obj:
            self._conf = conf_obj
        else:
            if exe_info.find('pypy') == -1:
                import cppconf
                self._conf = cppconf.Conf(filename)
                if use_translate:
                    # translate can only be performed on dicts, hence the convertion
                    self._conf = cpp2py(self._conf)
                    from pyutil.consul.bridge import translate_conf
                    self._conf.conf = translate_conf(self._conf.conf, filename)
            else:
                from conf2 import ConfParse
                # conf2.ConfParse will do the translate
                self._conf = ConfParse(filename, use_translate=use_translate)
            _Conf.CacheHash[filename] = self._conf

        self.local_conf = {}
        from pyutil.net.get_local_ip import get_local_ip
        self.local_conf['local_ip'] = get_local_ip()

    def get_values(self, key):
        val = self.local_conf.get(key)
        if val:
            return [p.strip() for p in val.split(',')]
        sv = self._conf.get_values(key)
        vals = [val for val in sv]
        return vals

    def get(self, key, val=''):
        local_val = self.local_conf.get(key)
        if local_val:
            return local_val
        return self._conf.get(key, val)

    def get_all(self):
        all_conf = self._conf.get_all()
        real_all_conf = {}
        for key, value in all_conf.items():
            real_all_conf[key] = value
        real_all_conf.update(self.local_conf)
        return real_all_conf

    def __getattr__(self, name):
        try:
            return super(Conf, self).__getattr__(name)
        except:
            return self.get(name)

# test:
# python conf.py /opt/tiger/ss_site/conf/deploy.conf
if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        conf = _Conf(sys.argv[1])
        conf = conf.get_all()
        for key in conf:
            print key, conf[key]

