#coding=utf8

import MySQLdb
import time
from elasticsearch import Elasticsearch
from pyutil.program.conf import Conf
from pyutil.program.cmd import run_command

def get_commitlist(repo):
    cmd = 'cd /opt/tiger/%s; git fetch; git log origin/online|head -n5|tail -n5' % repo
    for i in range(0, 5):
        res = run_command(cmd)
        if res:
            break
    if not res:
        return ''
    parts = res.split('\n')
    commitlist = ''
    for part in parts:
        if part:
            commitlist += part + '\n'
    #print commitlist
    return commitlist

def emit_timeline(data):
    conf = Conf('/opt/tiger/ss_conf/ss/db_op_data.conf')
    op_data_conn = MySQLdb.connect(host=conf.op_data_write_host, \
            user=conf.op_data_write_user, \
            passwd=conf.op_data_write_password,\
            db=conf.op_data_db_name,
            port=int(conf.op_data_write_port), charset='utf8')
    op_data_cur = op_data_conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    op_data_conn.autocommit(True)
    # id, online_time, repo, changelist, commitlist, user, args, ttype, reviewer
    start_time = data.get('start_time', int(time.time()))
    online_time = data.get('end_time', int(time.time()))
    repo = data.get('repo', '')
    if not repo:
        return {'status': False, 'message': 'no repo'}
    changelist = data.get('changelist', '')
    #if not changelist:
    #    return {'status': False, 'message': 'no changelist'}
    commitlist = data.get('commitlist', '')
    if not commitlist:
        commitlist = get_commitlist(repo)
    #    return {'status': False, 'message': 'no commitlist'}
    user = data.get('user', '')
    if not user:
        return {'status': False, 'message': 'no user'}
    args = data.get('args', '')
    ttype = data.get('ttype', 1)
    reviewer = data.get('reviewer', 0)
    insert_sql = 'insert into timelineconf (id, online_time, repo, changelist, commitlist, \
            user, args, ttype, reviewer, start_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
    op_data_cur.execute(insert_sql, (0, online_time, repo, changelist, commitlist, user, args, ttype, reviewer, start_time))
    # emit to es
    es = Elasticsearch([{"host": "10.4.16.143", "port": 9200}])
    esdata = { }
    #"@timestamp":"2014-09-28T00:23:34+08:00
    gmt = time.gmtime(online_time)
    utc_time = time.strftime('%Y-%m-%dT%H:%M:%S+00:00',gmt)
    esdata['@timestamp'] = utc_time
    if commitlist:
        esdata['title'] = commitlist
    else:
        esdata['title'] = 'no commit'
    if ttype == 1:
        esdata['tags'] = 'deploy'
        stype = 'deploy'
    else:
        esdata['tags'] = 'restart'
        stype = 'restart'
    text = 'repo: %s, user: %s, type: %s, args: %s' % (repo, user, stype, args)
    esdata['text'] = text
    #import pdb; pdb.set_trace()
    es.index(index="event", doc_type="event", body=esdata)

    return {'status': True, 'message': 'success add a new timeline'}

def test():
    data = {'repo': 'ss_op',
            'changelist': 'test.py',
            'user': 'baiqingqi',
            'args': '-mall',
            'reviewer' : 'baiqingqi'
            }
    emit_timeline(data)

if __name__ == '__main__':
    test()

