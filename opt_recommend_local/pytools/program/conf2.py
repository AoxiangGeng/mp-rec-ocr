#!/usr/bin/env python
#! -*- coding: utf8 -*-

import re
import os

def string2list(s, sep=','):
    return [i.strip() for i in s.split(sep)]

def is_separator(c):
    assert isinstance(c, basestring)
    if c == ":" or c == "=" or c.isspace():
        return True
    return False

RE_KEY_REF = re.compile(r"\{\{\s*([a-zA-Z0-9_\-]+)\s*\}\}")

class ConfParse(object):
    #缓存相同配置文件解析结果
    CacheHash = {}

    def __init__(self, filename, resolve_ref=True, use_translate=True, bypass_cache=False):
        self.conf = self.parse(filename, resolve_ref, bypass_cache)
        self.refkeys = set()
        if resolve_ref:
            self.resolve_reference()
        self.use_translate = use_translate
        self.translated = False
        self.filename = filename

    def __translate_all(self):
        if not self.use_translate or self.translated:
            return
        # with translate_conf, one can use something like "consul:comment"
        # bridge will automatically resolve these uris
        try:
            from pyutil.consul.bridge import translate_conf
            self.conf = translate_conf(self.conf, self.filename)
            self.translated = True
        except:
            # Raises for generating snapshot .zip file.
            if os.environ.get("RAISE_TRANSLATE_EXCEPTION", "0") == "1":
                raise

    def get(self, key, default="", resolve_ref=False):
        self.__translate_all()
        key = key.lower()
        value = self.conf.get(key, default)
        return value

    def get_values(self, key):
        val = self.get(key)
        vals = [v.strip() for v in val.split(',')]
        return vals

    def get_all(self):
        self.__translate_all()
        return self.conf

    # remove comments that starts with # or ; or \ from line
    # but keep it if preceding with \
    def remove_comments(self, line):
        if not line:
            return line

        str_list = []
        line_len = len(line)
        i = 0
        while i < line_len:
            if line[i] == '\\' and i+1 < line_len:
                i += 1
                str_list.append(line[i])
            elif self.is_comments(line[i]):
                break
            else:
                str_list.append(line[i])
            i += 1

        return ''.join(str_list)

    def is_comments(self, c):
        return c == '#' or c ==';'

    def parse(self, filename, resolve_ref, bypass_cache=False):
        if not bypass_cache:
            conf_obj = ConfParse.CacheHash.get(filename, None)
            if conf_obj:
                return conf_obj

        conf_obj = {}
        try:
            f = open(filename, 'r')
        except:
            return conf_obj

        def lines():
            whole_line = ""
            for line in f:
                line = line.strip()
                if line.endswith("\\"): # wrap lines
                    whole_line += line[:-1]
                    continue
                whole_line += line
                yield whole_line
                whole_line = ""
            if whole_line:
                yield whole_line

        for line in lines():
            # remove comments
            line = self.remove_comments(line)
            if not line:
                continue
            s_s_pos = -1
            s_e_pos = -1
            for pos, c in enumerate(line):
                if is_separator(c):
                    if s_s_pos == -1:
                        s_s_pos = pos
                    s_e_pos = pos
                elif s_s_pos != -1:
                    break # end-of-separator

            if s_e_pos == -1:
                key = line
                val = ''
            else:
                key = line[:s_s_pos]
                val = line[s_e_pos + 1:]

            key = key.strip()
            val = val.strip()

            if key == 'include':
                path = val
                if not os.path.isabs(path):
                    path = os.path.dirname(os.path.abspath(filename)) + '/' + val
                conf_obj.update(self.parse(path, resolve_ref, bypass_cache))
            else:
                conf_obj[key.lower()] = val
                conf_obj[key] = val
        ConfParse.CacheHash[filename] = conf_obj
        return conf_obj

    def resolve_reference(self):
        for key in self.conf:
            self.resolve_reference_key(key)

    def resolve_reference_key(self, key, default=""):
        value = self.conf.get(key, default)
        self.refkeys.add(key)
        def replace_ref(m):
            ref_key = m.groups()[0]
            assert ref_key not in self.refkeys, "recursion reference key: %s" % key
            return self.resolve_reference_key(ref_key)
        value = RE_KEY_REF.sub(replace_ref, value)
        if key in self.conf:
            self.conf[key] = value
        self.refkeys.remove(key)
        return value


class Conf(object):

    def __init__(self, filename, use_translate=True, bypass_cache=False):
        self._conf = ConfParse(filename, use_translate=use_translate, bypass_cache=bypass_cache)
        self.local_conf = {}
        from pytools.net.get_local_ip import get_local_ip
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

    def set(self, name, value):
        self.local_conf[name] = value

    def __getattr__(self, name):
        return self.get(name)


# test:
# python conf2.py /opt/tiger/ss_site/conf/deploy.conf
if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        conf = Conf(sys.argv[1])
        print conf.get("test")
        conf = conf.get_all()
        for key in conf:
            print key, conf[key]

#        from pyutil.program.conf import _Conf
 #       conf2 = _Conf(sys.argv[1])
  #      conf2 = conf2.get_all()
   #     assert cmp(conf, conf2) == 0

