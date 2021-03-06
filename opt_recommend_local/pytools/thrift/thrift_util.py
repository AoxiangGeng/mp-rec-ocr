#coding=utf-8
#!/usr/bin/env python
#
#
from thrift.transport import TTransport, TSocket, THttpClient
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from pyutil.thrift.transport import TSocketPool
from .thrift_unicode import thrift_unicode_client
from .thrift_utils import thrift_attrs
from .server.TProcessThreadPoolServer import TProcessThreadPoolServer

def thrift_serlize( thrift_obj, TProt=TBinaryProtocol.TBinaryProtocol ):
    trans=TTransport.TMemoryBuffer()
    prot=TProt(trans)
    thrift_obj.write(prot)
    data=trans.getvalue()
    trans.close()
    return data


def thrift_unserlize( data,TStruct,TProt=TBinaryProtocol.TBinaryProtocol ):
    thrift_obj=TStruct()
    trans=TTransport.TMemoryBuffer(data)
    prot=TProt(trans)
    thrift_obj.read(prot)
    trans.close()
    return thrift_obj

def get_thrift_server(ThriftServiceClass, handler, port, thread_num, worker_num=1):
    processor = ThriftServiceClass.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    if worker_num > 1:
        server = TProcessThreadPoolServer(processor, transport, tfactory, pfactory)
        server.setNumWorkers(worker_num)
    else:
        server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server.setNumThreads(thread_num)
    return server

get_thrift_thread_server = get_thrift_server # deprecated

class ThriftClient:
    def __init__(self, servers, client_class,
                 timeout=None, ports=None, use_unicode=False, use_framed=False, use_translate=False):
        if use_unicode:
            client_class = thrift_unicode_client(client_class)

        if ports==None:
            self.socket = TSocketPool.TSocketPool(servers,use_translate=use_translate)
        else:
            self.socket = TSocketPool.TSocketPool(servers,ports,use_translate=use_translate)

        self.socket.setTimeout(timeout)
        if use_framed:
            self.transport = TTransport.TFramedTransport(self.socket)
        else:
            self.transport = TTransport.TBufferedTransport(self.socket)

        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = client_class(self.protocol)

    def open(self):
        self.transport.open()
    
    def close(self):
        self.transport.close()
    
    def get_client(self):
        return self.client


    def __enter__(self):
        self.open()
        return self.client

    def __exit__(self, type, value, traceback):
        return self.close()

    def __getattr__(self,name):
        f = getattr(self.client, name)
        return f
