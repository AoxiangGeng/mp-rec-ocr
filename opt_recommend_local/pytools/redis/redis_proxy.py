#!/usr/bin/env python
# coding: utf-8
"""
The Redis Client using random.choice(self.redis_servers)
It is useful when using proxy like twemproxy

USAGE:
    cli = make_redis_proxy_cli(
                    ["10.4.16.28:6379", "10.4.16.29:6379"],
                    **connection_kwargs, strict_redis=False)

    connection_kwargs can be:
        db,
        password,
        socket_timeout,
        max_connections (in total, not per server)
"""

import pytools.twemproxy as twemproxy

import redis
from redis_wrapper import StrictRedisWrapper

def make_redis_proxy_cli(redis_servers, **connection_kwargs):
    strict_redis = connection_kwargs.pop('strict_redis', True)

    pool = twemproxy.RandomRedisConnectionPool(redis_servers, **connection_kwargs)
    if strict_redis:
        return redis.StrictRedis(connection_pool=pool)
    else:
        return redis.Redis(connection_pool=pool)

def make_redis_proxy_cli2(redis_servers, connection_kwargs=None, redis_kwargs=None, strict_redis=True,
                          cluster='default', thread_local_pool=False):
    '''
    NOTE: cluster设置成使用的cluster的名称，以便可以查看metrics

    :param redis_servers:
    :param connection_kwargs:
    :param redis_kwargs:
    :param strict_redis:
    :param cluster:
    :return:
    '''
    if connection_kwargs is None:
        connection_kwargs = {}
    if redis_kwargs is None:
        redis_kwargs = {}
    if thread_local_pool:
        pool = twemproxy.ThreadLocalConnectionPool(redis_servers, **connection_kwargs)
    else:
        pool = twemproxy.RandomRedisConnectionPool(redis_servers, **connection_kwargs)
    if strict_redis:
        return StrictRedisWrapper(connection_pool=pool, cluster=cluster, **redis_kwargs)
    else:
        return redis.Redis(connection_pool=pool, **redis_kwargs)


def make_redis_auto_conf_proxy_cli(cluster, connection_kwargs=None, redis_kwargs=None):
    '''
    NOTE: cluster设置成使用的cluster的名称，以便获取servers和查看metrics
          当配置发生变化时，可以自动获取新配置初始化client.

    :param cluster:
    :param connection_kwargs:
    :param redis_kwargs:
    :param strict_redis:
    :param cluster:
    :return:
    '''
    if connection_kwargs is None:
        connection_kwargs = {}
    if redis_kwargs is None:
        redis_kwargs = {}
    pool = twemproxy.AutoConfRedisConnectionPool(cluster_name=cluster, **connection_kwargs)
    return StrictRedisWrapper(connection_pool=pool, cluster=cluster, **redis_kwargs)
