#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class ImpressionItem:
  """
  Attributes:
   - campaign_id
   - creative_id
   - user_id
   - unit_id
   - timestamp
   - source
   - pos_id
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'campaign_id', None, None, ), # 1
    (2, TType.I32, 'creative_id', None, None, ), # 2
    (3, TType.I32, 'user_id', None, None, ), # 3
    (4, TType.I32, 'unit_id', None, None, ), # 4
    (5, TType.I32, 'timestamp', None, None, ), # 5
    (6, TType.I32, 'source', None, None, ), # 6
    (7, TType.I16, 'pos_id', None, None, ), # 7
  )

  def __init__(self, campaign_id=None, creative_id=None, user_id=None, unit_id=None, timestamp=None, source=None, pos_id=None,):
    self.campaign_id = campaign_id
    self.creative_id = creative_id
    self.user_id = user_id
    self.unit_id = unit_id
    self.timestamp = timestamp
    self.source = source
    self.pos_id = pos_id

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
        if ftype == TType.I32:
          self.campaign_id = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.creative_id = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I32:
          self.user_id = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I32:
          self.unit_id = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.timestamp = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.I32:
          self.source = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.I16:
          self.pos_id = iprot.readI16()
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
    oprot.writeStructBegin('ImpressionItem')
    if self.campaign_id is not None:
      oprot.writeFieldBegin('campaign_id', TType.I32, 1)
      oprot.writeI32(self.campaign_id)
      oprot.writeFieldEnd()
    if self.creative_id is not None:
      oprot.writeFieldBegin('creative_id', TType.I32, 2)
      oprot.writeI32(self.creative_id)
      oprot.writeFieldEnd()
    if self.user_id is not None:
      oprot.writeFieldBegin('user_id', TType.I32, 3)
      oprot.writeI32(self.user_id)
      oprot.writeFieldEnd()
    if self.unit_id is not None:
      oprot.writeFieldBegin('unit_id', TType.I32, 4)
      oprot.writeI32(self.unit_id)
      oprot.writeFieldEnd()
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I32, 5)
      oprot.writeI32(self.timestamp)
      oprot.writeFieldEnd()
    if self.source is not None:
      oprot.writeFieldBegin('source', TType.I32, 6)
      oprot.writeI32(self.source)
      oprot.writeFieldEnd()
    if self.pos_id is not None:
      oprot.writeFieldBegin('pos_id', TType.I16, 7)
      oprot.writeI16(self.pos_id)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.campaign_id)
    value = (value * 31) ^ hash(self.creative_id)
    value = (value * 31) ^ hash(self.user_id)
    value = (value * 31) ^ hash(self.unit_id)
    value = (value * 31) ^ hash(self.timestamp)
    value = (value * 31) ^ hash(self.source)
    value = (value * 31) ^ hash(self.pos_id)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
