# -*- coding: utf-8 -*-
import re, os, threading

from pytools.program.conf2 import Conf, ConfParse

class ClientConf(object):
    # static data
    _clusters = {}
    _clusters_lock = threading.Lock()

    @staticmethod
    def get_conf_path(module, zone):
        conf_path = ''
        if module == 'memcache':
            conf_path = 'memcache.conf'
        elif module == 'redis':
            conf_path = 'redis.conf'
        elif module == 'springdb':
            conf_path = 'springdb.conf'
        elif module == 'twemproxy_deploy':
            conf_path = 'twemproxy_deploy.conf'
        else:
            raise ValueError("module '%s' not supported for client_conf" % module)

        conf_dir = ''
        if zone == 'auto':
            conf_dir = '/etc/ss_conf'
        elif zone == 'online':
            conf_dir = '/opt/tiger/ss_conf/ss'
        elif zone == 'offline':
            conf_dir = '/opt/tiger/ss_conf/ss_offline'
        elif zone == 'test':
            conf_dir = '/opt/tiger/ss_conf/ss_test'
        elif os.path.exists(zone): # a specific path
            conf_dir = zone
        else:
            raise ValueError("zone '%s' not found for client_conf" % zone)

        return conf_dir + '/' + conf_path

    @staticmethod
    def get_cluster_conf(module, cluster, zone='auto'):
        token = ClientConf._cluster_token(module, cluster, zone)
        if token not in ClientConf._clusters:
            with ClientConf._clusters_lock:
                if token not in ClientConf._clusters:
                    conf = ClientConf._parse_cluster_conf(module, cluster, zone)
                    ClientConf._clusters[token] = conf
        return ClientConf._clusters[token]

    @staticmethod
    def _cluster_token(module, cluster, zone):
        return '%s:%s:%s' % (module, cluster, zone)

    @staticmethod
    def _parse_cluster_conf(module, cluster, zone):
        path = ClientConf.get_conf_path(module, zone)
        if not os.path.exists(path):
            raise ValueError("conf path '%s' not exists" % path)

        if module == 'memcache':
            return ClientConf._parse_memcache_conf(module, cluster, path)
        elif module == 'springdb':
            return ClientConf._parse_db_conf(module, cluster, path)
        elif module == 'redis':
            return ClientConf._parse_db_conf(module, cluster, path)
        else:
            raise ValueError("module '%s' not supported for client_conf" % module)

    @staticmethod
    def _parse_memcache_conf(module, cluster, path):
        conf = ConfParse(path, resolve_ref=False)

        result = {'cluster': cluster}

        value = conf.get(cluster)
        ref_match = re.match(".*\\{\\{(.*?)\\}\\}", value)
        if ref_match: # a reference
            ref_value = ref_match.group(1).strip()
            if ref_value == cluster:
                raise ValueError("cluster '%s' is referenced to itself" %
                                 cluster)
            result['real_cluster'] = ref_value
            if conf.get(ref_value, '') == '':
                raise ValueError("servers not found for cluster '%s' in conf "
                                 "'%s'" % (cluster, path))
            result['servers'] = conf.get_values(ref_value)
        else:
            result['real_cluster'] = cluster
            if conf.get(cluster, '') == '':
                raise ValueError("servers not found for cluster '%s' in conf "
                                 "'%s'" % (cluster, path))
            result['servers'] = conf.get_values(cluster)

        result['use_proxy'] = conf.get(cluster + '_use_proxy', 0)

        return result

    @staticmethod
    def _parse_db_conf(module, cluster, path):
        conf = Conf(path)

        result = {'cluster': cluster}

        # use cluster as real cluster, if real_cluster not found
        result['real_cluster'] = conf.get(cluster + '_real_cluster', cluster)

        if conf.get(cluster + '_servers', '') == '':
            raise ValueError("servers not found for cluster '%s' in conf '%s'" %
                             (cluster, path))
        result['servers'] = conf.get_values(cluster + '_servers')

        if conf.get(cluster + '_tables', '') == '':
            raise ValueError("tables not found for cluster '%s' in conf '%s'" %
                             (cluster, path))
        result['tables'] = conf.get_values(cluster + '_tables')

        return result

if __name__ == '__main__':
    import json
    zone = '../../../ss_conf/ss_test'

    print '[springdb clusters]'
    r = ClientConf.get_cluster_conf('springdb', 'springdb_sandbox', zone)
    print json.dumps(r, indent=2)
    r = ClientConf.get_cluster_conf('springdb', 'springdb_sandbox_read', zone)
    print json.dumps(r, indent=2)
    r = ClientConf.get_cluster_conf('springdb', 'springdb_profile', zone)
    print json.dumps(r, indent=2)

    print '[memcache clusters]'
    r = ClientConf.get_cluster_conf('memcache', 'memcache9', zone)
    print json.dumps(r, indent=2)
    r = ClientConf.get_cluster_conf('memcache', 'memcache_group_info', zone)
    print json.dumps(r, indent=2)

