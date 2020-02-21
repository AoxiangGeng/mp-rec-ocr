#!/usr/bin/env python
# coding: utf-8
__author__ = 'zhenghuabin'

import time

import redis
from redis import ConnectionError, TimeoutError
from pytools.program import metrics2 as metrics


class StrictRedisWrapper(redis.StrictRedis):
    METRIC_PREFIX = 'inf.redisclient'

    def __init__(self, connection_pool, cluster='default', **kwargs):
        super(StrictRedisWrapper, self).__init__(connection_pool=connection_pool, **kwargs)
        self.cluster = cluster
        self._define_metrics()
        self._defined_cmds = set()
        self._defined_backends = set()

    def _define_metrics(self):
        metrics.define_counter('error', prefix=self.METRIC_PREFIX)
        metrics.define_counter('throughput', prefix=self.METRIC_PREFIX)
        metrics.define_timer('latency', units='us', prefix=self.METRIC_PREFIX)
        metrics.define_tagkv('cluster', [self.cluster, ])

    def execute_command(self, *args, **options):
        "Execute a command and return a parsed response"
        pool = self.connection_pool
        command_name = args[0]

        # 搞个list是为了让wrap中的connection host能传到外面来
        closure_backend = []

        def wrap():
            connection = pool.get_connection(command_name, **options)
            closure_backend.append(connection.host)
            try:
                connection.send_command(*args)
                return self.parse_response(connection, command_name, **options)
            except (ConnectionError, TimeoutError) as e:
                connection.disconnect()
                if not connection.retry_on_timeout and isinstance(e, TimeoutError):
                    raise
                connection.send_command(*args)
                return self.parse_response(connection, command_name, **options)
            finally:
                pool.release(connection)

        try:
            failed = False
            ts = time.time()
            return wrap()
        except:
            failed = True
            raise
        finally:
            cmd = str.lower(command_name)
            tags = {
                'cluster': self.cluster,
                'cmd': cmd,
            }
            if cmd not in self._defined_cmds:
                metrics.define_tagkv('cmd', [cmd, ])
                self._defined_cmds.add(cmd)
            if closure_backend:
                tags['backend'] = closure_backend[0]
                if closure_backend[0] not in self._defined_backends:
                    metrics.define_tagkv('backend', [closure_backend[0], ])
                    self._defined_backends.add(closure_backend[0])
            if failed:
                metrics.emit_counter('error', 1, self.METRIC_PREFIX, tags)
            metrics.emit_counter('throughput', 1, self.METRIC_PREFIX, tags)
            metrics.emit_timer('latency', int((time.time() - ts) * 1000000), self.METRIC_PREFIX, tags)

