#coding=utf-8

import json, os
from pyutil.program.python import obj_unicode_to_str, unicode_json_dump

class JsonDict(dict):
    '''
    General json object that allows attributes to be bound to and also behaves like a dict.

    >>> jd = JsonDict(a=1, b='test')
    >>> jd.a
    1
    >>> jd.b
    'test'
    >>> jd['b']
    'test'
    >>> jd.c
    Traceback (most recent call last):
      ...
    AttributeError: 'JsonDict' object has no attribute 'c'
    >>> jd['c']
    Traceback (most recent call last):
      ...
    KeyError: 'c'
    '''
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value

def json_loads(s):
    '''
    Parse json string into JsonDict.

    >>> r = json_loads(r'{"name":"Michael","score":95}')
    >>> r.name
    u'Michael'
    >>> r['score']
    95
    >>> json_loads(r'1')
    1
    '''
    return json.loads(s, object_hook=lambda pairs: JsonDict(pairs.iteritems()))

unicode_json_dumps = unicode_json_dump
def json_dumps(d, to_unicode=False):
    res = unicode_json_dumps(d)
    res = res if to_unicode else res.encode('utf-8')
    return res


def json_default(obj):
    """
    dump any object
    usage: json.dumps(obj, defult=json_default)
    """
    from datetime import datetime
    import copy, time
    if isinstance(obj, datetime):
        return int(time.mktime(obj.timetuple()))
    else:
        obj_dict = copy.copy(obj.__dict__)
        if '_sa_instance_state' in obj_dict:
            del obj_dict['_sa_instance_state']
        return obj_dict

def load_json_list(file_name):
    """
    load list of json object from file, each line as a json
    :param file_name:
    :return:
    """
    res = []
    if not os.path.isfile(file_name):
        return res
    with open(file_name) as fr:
        res = [json.loads(x.strip('\n')) for x in fr.readlines()]

    return res

def dump_json_list(data_list, file_name):
    """
    dump list of json object to a file, each json object on a line
    :param data_list:
    :param file_name:
    :return:
    """
    with open(file_name, 'w') as fw:
        for data in data_list:
            fw.write('%s\n' % json.dumps(data))