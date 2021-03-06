#
# Autogenerated by Thrift Compiler (0.8.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class Ruler:
  """
  Attributes:
   - service_name
   - metric_name
   - message
   - recipients
   - enabled
   - silent_mode
   - silent_interval
   - opentsdb_aggregator
   - opentsdb_downsampler
   - opentsdb_rate
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'service_name', None, None, ), # 1
    (2, TType.STRING, 'metric_name', None, None, ), # 2
    (3, TType.STRING, 'message', None, None, ), # 3
    (4, TType.LIST, 'recipients', (TType.STRING,None), None, ), # 4
    (5, TType.BOOL, 'enabled', None, None, ), # 5
    (6, TType.STRING, 'silent_mode', None, None, ), # 6
    (7, TType.I32, 'silent_interval', None, None, ), # 7
    (8, TType.STRING, 'opentsdb_aggregator', None, None, ), # 8
    (9, TType.STRING, 'opentsdb_downsampler', None, None, ), # 9
    (10, TType.STRING, 'opentsdb_rate', None, None, ), # 10
  )

  def __init__(self, service_name=None, metric_name=None, message=None, recipients=None, enabled=None, silent_mode=None, silent_interval=None, opentsdb_aggregator=None, opentsdb_downsampler=None, opentsdb_rate=None,):
    self.service_name = service_name
    self.metric_name = metric_name
    self.message = message
    self.recipients = recipients
    self.enabled = enabled
    self.silent_mode = silent_mode
    self.silent_interval = silent_interval
    self.opentsdb_aggregator = opentsdb_aggregator
    self.opentsdb_downsampler = opentsdb_downsampler
    self.opentsdb_rate = opentsdb_rate

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.service_name = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.metric_name = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.message = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.LIST:
          self.recipients = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = iprot.readString();
            self.recipients.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.BOOL:
          self.enabled = iprot.readBool();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.STRING:
          self.silent_mode = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.I32:
          self.silent_interval = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.STRING:
          self.opentsdb_aggregator = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.STRING:
          self.opentsdb_downsampler = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 10:
        if ftype == TType.STRING:
          self.opentsdb_rate = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Ruler')
    if self.service_name is not None:
      oprot.writeFieldBegin('service_name', TType.STRING, 1)
      oprot.writeString(self.service_name)
      oprot.writeFieldEnd()
    if self.metric_name is not None:
      oprot.writeFieldBegin('metric_name', TType.STRING, 2)
      oprot.writeString(self.metric_name)
      oprot.writeFieldEnd()
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 3)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    if self.recipients is not None:
      oprot.writeFieldBegin('recipients', TType.LIST, 4)
      oprot.writeListBegin(TType.STRING, len(self.recipients))
      for iter6 in self.recipients:
        oprot.writeString(iter6)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.enabled is not None:
      oprot.writeFieldBegin('enabled', TType.BOOL, 5)
      oprot.writeBool(self.enabled)
      oprot.writeFieldEnd()
    if self.silent_mode is not None:
      oprot.writeFieldBegin('silent_mode', TType.STRING, 6)
      oprot.writeString(self.silent_mode)
      oprot.writeFieldEnd()
    if self.silent_interval is not None:
      oprot.writeFieldBegin('silent_interval', TType.I32, 7)
      oprot.writeI32(self.silent_interval)
      oprot.writeFieldEnd()
    if self.opentsdb_aggregator is not None:
      oprot.writeFieldBegin('opentsdb_aggregator', TType.STRING, 8)
      oprot.writeString(self.opentsdb_aggregator)
      oprot.writeFieldEnd()
    if self.opentsdb_downsampler is not None:
      oprot.writeFieldBegin('opentsdb_downsampler', TType.STRING, 9)
      oprot.writeString(self.opentsdb_downsampler)
      oprot.writeFieldEnd()
    if self.opentsdb_rate is not None:
      oprot.writeFieldBegin('opentsdb_rate', TType.STRING, 10)
      oprot.writeString(self.opentsdb_rate)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
