#coding=utf8

import logging, time, socket, threading, random

from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport
from thrift.protocol import TMultiplexedProtocol
from thrift.Thrift import TException

from pytools.thrift.transport import SocketPool

__all__ = ['ThriftClient']

class ThriftClient(threading.local):

    def __init__(self, service_module, host, port, timeout=3, conn_timeout=0.2, max_retries=1, nonblocking_server=False, multiplexed=False, service_name=""):
        self.max_retries = max_retries
        name_sign = 'client:%s:%s:%s:%s:%s' % (service_module.__name__, host, port, timeout, conn_timeout)
        client = self.__dict__.get(name_sign)
        if not client:
            self.randomizer = random.Random()
            self.socketpool = SocketPool.TSocketPool(host, port, timeout, conn_timeout, self.randomizer)
            if nonblocking_server:
                transport = TTransport.TFramedTransport(self.socketpool)
            else:
                transport = TTransport.TBufferedTransport(self.socketpool)
            protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
            if multiplexed:
                multiplexed_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, service_name)
                client = service_module.Client(multiplexed_protocol)
            else:
                client = service_module.Client(protocol)
            client.transport = transport
            setattr(self, name_sign, client)
        self.client = client

    def __getattr__(self, attr):
        retry_times = 0
        func = getattr(self.client, attr)
        def wrap(*args, **kw):
            retry_times = 0
            while retry_times < self.max_retries:
                retry_times += 1
                try:
                    self.client.transport.open()
                    return func(*args, **kw)
                except:
                    if retry_times >= self.max_retries:
                        raise
                finally:
                    self.client.transport.close()
        return wrap

    def get_peer_addr(self):
        return '%s:%s' % (self.socketpool.host, self.socketpool.port)

