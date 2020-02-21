#coding=utf8
import os, sys, hashlib, threading, datetime, logging, re
import MySQLdb
from functools import wraps
from pyutil.program.fmtutil import pformat

def get_where_op(k, v=''):
    '''
    >>> get_where_op('a')
    'a = %s'
    >>> get_where_op('a__ne')
    'a != %s'
    >>> get_where_op('a__lt')
    'a < %s'
    >>> get_where_op('a__isnull', False)
    'a is not null'
    >>> get_where_op('a', [1, 2])
    'a in %s'
    >>> get_where_op('a__in', [1, 2])
    'a in %s'
    >>> get_where_op('a__in', 1)
    'a = %s'
    '''

    op_map = dict(
            ne='!=',
            lt='<',
            lte='<',
            gt='>',
            gte='>=',
            isnull='isnull',
            )
    op_map['in'] = 'in'

    parts = k.rsplit('__', 1)
    if len(parts) == 2:
        k, op = parts
        op = op_map[op]
        if op == 'in' and not isinstance(v, (list, tuple)):
            op = '='
    else:
        k = parts[0]
        op = 'in' if isinstance(v, (list, tuple)) else '='

    if op == 'isnull':
        return '%s is %s' % (k, 'null' if v else 'not null')
    else:
        return '%s %s %%s' % (k, op)

def get_where_sql(where):
    '''
    >>> get_where_sql(['a.b', 'c'])
    'a.b = %s and c = %s'
    >>> get_where_sql(['a__ne'])
    'a != %s'
    >>> get_where_sql(dict(a=[1,2], b='x'))
    'a in %s and b = %s'
    >>> get_where_sql(dict(a__in=[1,2], b='x'))
    'a in %s and b = %s'
    '''
    if isinstance(where, (list, tuple)):
        where_keys = where
        where = {x: '' for x in where}
    else:
        where_keys = where.keys()
    return ' and '.join(get_where_op(k, where[k]) for k in where_keys)

def get_insert_sql(table, keys):
    '''
    >>> get_insert_sql('foo', ['a', 'b'])
    'insert into foo (a, b) values (%s, %s)'
    '''
    sql = 'insert into %s (%s) values (%s)' % (table, ', '.join(keys), ', '.join(['%s'] * len(keys)))
    return sql

def get_update_sql(table, update_keys, where):
    '''
    >>> get_update_sql('foo', ['a', 'b'], dict(a=1, b__in=2, c__in=[3, 4], d=[5, 6]))
    'update foo set a=%s, b=%s where a = %s and c in %s and b = %s and d in %s'
    >>> get_update_sql('foo', ['a'], dict(id__isnull=True))
    'update foo set a=%s where id is null'
    '''
    sql = 'update %s set %s where %s' % (
            table,
            ', '.join(x + '=%s' for x in update_keys),
            get_where_sql(where),
            )
    return sql

def get_select_sql(table, keys, where=None, extra=None, order_by=None, limit=None):
    '''
    >>> get_select_sql('foo', ['a', 'b'], order_by='a asc', limit=1)
    'select a, b from foo order by a asc limit 1'
    >>> get_select_sql('foo', ['a', 'b'], extra="order by a asc", limit=1)
    'select a, b from foo order by a asc limit 1'
    >>> get_select_sql('foo', ['a', 'b'], ['b', 'c'])
    'select a, b from foo where b = %s and c = %s'
    >>> get_select_sql('foo', ['a', 'b'], where=dict(a__ne=5, b__isnull=True))
    'select a, b from foo where b is null and a != %s'
    >>> get_select_sql('foo', ['a', 'b'], where='b is null')
    'select a, b from foo where b is null'
    '''

    sql = 'select %s from %s' % (', '.join(keys), table)
    if where:
        if isinstance(where, basestring):
            sql += ' where ' + where
        else:
            sql += ' where ' + get_where_sql(where)
    if order_by:
        sql += ' order by ' + order_by
    if extra:
        sql += ' ' + extra
    if limit:
        sql += ' limit %s' % limit
    return sql

def unfold_one(lst):
    if isinstance(lst, (list, tuple)) and len(lst) == 1:
        return lst[0]
    else:
        return lst

local_conn = None

class DAL(threading.local):
    dry_run = False

    def __init__(self, host, name, user, passwd, port=3306, connect_timeout=1, read_timeout=0, charset='utf8'):
        self.host, self.port, self.name, self.user, self.passwd = host, int(port), name, user, passwd
        self.conn_key = '%s|%s:%s@%s:%s/%s' % (os.getpid(), user, passwd, host, port, name)
        self.cursor = None
        self.conn = None
        self.charset = charset
        # unit: second
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

    def open(self):
        global local_conn
        if not local_conn:
            local_conn = threading.local()
        if not hasattr(local_conn, 'connections'):
            local_conn.connections = {}
        conn = local_conn.connections.get(self.conn_key)
        if not conn:
            conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,
                                   db=self.name, charset=self.charset, autocommit=True,
                                   connect_timeout=self.connect_timeout,
                                   read_timeout=self.read_timeout,
                                  )
            local_conn.connections[self.conn_key] = conn
        self.conn = conn
        self.cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def get_cursor(self):
        if not self.cursor:
            self.open()
        return self.cursor

    def execute(self, sql_fmt, *params, **kwargs):
        retries = kwargs.get('retries', 1)
        while True:
            try:
                cursor = self.get_cursor()
                if self.dry_run:
                    m = re.search(r'^\s*(update|insert|replace|delete)', sql_fmt, re.I)
                    if m:
                        logging.info('%s called, sql(%s), args=%s, kws=%s', m.group(1), sql_fmt,
                                pformat(params, max_v_limit=200), pformat(kwargs, max_v_limit=200))
                        return cursor
                cursor.execute(sql_fmt, params or None)
                return cursor
            except:
                self.close()
                if retries <= 0:
                    raise
                retries -= 1

    def close(self):
        global local_conn
        if self.cursor:
            self.cursor.close()
            self.cursor = None

        if self.conn:
            conn = local_conn.connections.pop(self.conn_key, None)
            if conn:
                conn.close()
            self.conn = None



class BaseDAL(DAL):
    def insert(self, table, info):
        if not info:
            return
        sql = get_insert_sql(table, info.keys())
        self.execute(sql, *info.values())
        return self.cursor.connection.insert_id()

    def update(self, table, info, **where):
        if 'where' in where:
            where = where['where']
        if not info or not where:
            return
        where = {k: unfold_one(v) for k, v in where.iteritems()} # workaround: MySQLdb对于只有一个元素的list执行in操作有bug
        # isnull没有%s, 故需从values中去掉
        where_values = [v for k, v in where.iteritems() if not k.endswith('__isnull')]
        sql = get_update_sql(table, info.keys(), where)
        self.execute(sql, *(info.values() + where_values))
        return self.cursor.rowcount

    def _fetch(self, one, table, keys, order_by=None, limit=None, **where):
        if 'where_sql' in where:
            where = where['where_sql']
            where_values = []
        else:
            if 'where' in where:
                where = where['where']
            where = {k: unfold_one(v) for k, v in where.iteritems()} # workaround: MySQLdb对于只有一个元素的list执行in操作有bug
            # isnull没有%s, 故需从values中去掉
            where_values = [v for k, v in where.iteritems() if not k.endswith('__isnull')]
        sql = get_select_sql(table, keys, where, order_by=order_by, limit=limit)
        self.execute(sql, *where_values)
        if one:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

    def fetchone(self, table, keys, order_by=None, **where):
        return self._fetch(True, table, keys, order_by=order_by, limit=1, **where)

    def fetchall(self, table, keys, order_by=None, limit=None, **where):
        return self._fetch(False, table, keys, order_by=order_by, limit=limit, **where)

def _dry_run_execute(fn):
    import re
    from pyutil.program.fmtutil import pformat
    @wraps(fn)
    def wrapped(self, *args, **kws):
        sql = args[0]
        if re.search(r'^\s*(update|insert|replace|delete)', sql, re.I):
            logging.info('execute called, args=%s, kws=%s',
                    pformat(args, max_v_limit=200), pformat(kws, max_v_limit=200))
        else:
            fn(self, *args, **kws)
    return wrapped

def dry_run_dal(DalClass):
    '''
    decorator for dry run dal
    '''
    DryRunDal = type('DryRun%s' % DalClass.__name__, (DalClass,), {'__module__': DalClass.__module__})
    DryRunDal.execute = _dry_run_execute(DryRunDal.execute)
    return DryRunDal


def __autocommit_on(sender, **kwargs):
    kwargs['connection'].connection.autocommit(True)

def set_autocommit():
    """
    example:

    from pyutil.program.db import set_autocommit
    set_autocommit()

    """
    from django.db.backends.signals import connection_created
    connection_created.connect(__autocommit_on)


def dict_factory(cursor, row):
    return dict((col[0], row[idx])
                for idx, col in enumerate(cursor.description))


if __name__ == '__main__':
    from pyutil.program.conf import Conf
    conf = Conf("/opt/tiger/ss_conf/ss/db_recommend.conf")
    dal = DAL(host=conf.ss_recommend_read_host,
              port=conf.ss_recommend_read_port,
              user=conf.ss_recommend_read_user,
              passwd=conf.ss_recommend_read_password,
              name=conf.ss_recommend_name, connect_timeout=2, read_timeout=3)
    print dal.execute("select 1 + 1").fetchall()
    print dal.execute("select sleep(10)", retries=0) # raise 'Lost connection' error
