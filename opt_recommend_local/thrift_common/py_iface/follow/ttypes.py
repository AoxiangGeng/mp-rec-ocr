#
# Autogenerated by Thrift Compiler (0.9.3)
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


class RspStatus:
  OK = 0
  INVALID_USER = 1
  INVALID_PARAM = 2
  SHORT_RESULT = 3
  NO_RESULT = 4

  _VALUES_TO_NAMES = {
    0: "OK",
    1: "INVALID_USER",
    2: "INVALID_PARAM",
    3: "SHORT_RESULT",
    4: "NO_RESULT",
  }

  _NAMES_TO_VALUES = {
    "OK": 0,
    "INVALID_USER": 1,
    "INVALID_PARAM": 2,
    "SHORT_RESULT": 3,
    "NO_RESULT": 4,
  }


class User:
  """
  Attributes:
   - udid
   - uid_type
   - user_id
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'udid', None, None, ), # 1
    (2, TType.I32, 'uid_type', None, 0, ), # 2
    (3, TType.I64, 'user_id', None, 0, ), # 3
  )

  def __init__(self, udid=None, uid_type=thrift_spec[2][4], user_id=thrift_spec[3][4],):
    self.udid = udid
    self.uid_type = uid_type
    self.user_id = user_id

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
          self.udid = iprot.readString()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.uid_type = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.user_id = iprot.readI64()
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
    oprot.writeStructBegin('User')
    if self.udid is not None:
      oprot.writeFieldBegin('udid', TType.STRING, 1)
      oprot.writeString(self.udid)
      oprot.writeFieldEnd()
    if self.uid_type is not None:
      oprot.writeFieldBegin('uid_type', TType.I32, 2)
      oprot.writeI32(self.uid_type)
      oprot.writeFieldEnd()
    if self.user_id is not None:
      oprot.writeFieldBegin('user_id', TType.I64, 3)
      oprot.writeI64(self.user_id)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.udid)
    value = (value * 31) ^ hash(self.uid_type)
    value = (value * 31) ^ hash(self.user_id)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Req:
  """
  Attributes:
   - user
   - num
   - exist_list
   - expose_filter
   - abtest_parameters
   - channel_id
   - pos_id
   - target_list
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'user', (User, User.thrift_spec), None, ), # 1
    (2, TType.I32, 'num', None, None, ), # 2
    (3, TType.LIST, 'exist_list', (TType.STRUCT,(User, User.thrift_spec)), None, ), # 3
    (4, TType.BOOL, 'expose_filter', None, True, ), # 4
    (5, TType.STRING, 'abtest_parameters', None, None, ), # 5
    (6, TType.I32, 'channel_id', None, 0, ), # 6
    (7, TType.I32, 'pos_id', None, 0, ), # 7
    (8, TType.LIST, 'target_list', (TType.STRUCT,(User, User.thrift_spec)), None, ), # 8
  )

  def __init__(self, user=None, num=None, exist_list=None, expose_filter=thrift_spec[4][4], abtest_parameters=None, channel_id=thrift_spec[6][4], pos_id=thrift_spec[7][4], target_list=None,):
    self.user = user
    self.num = num
    self.exist_list = exist_list
    self.expose_filter = expose_filter
    self.abtest_parameters = abtest_parameters
    self.channel_id = channel_id
    self.pos_id = pos_id
    self.target_list = target_list

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
        if ftype == TType.STRUCT:
          self.user = User()
          self.user.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.num = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.LIST:
          self.exist_list = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = User()
            _elem5.read(iprot)
            self.exist_list.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.BOOL:
          self.expose_filter = iprot.readBool()
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.abtest_parameters = iprot.readString()
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.I32:
          self.channel_id = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.I32:
          self.pos_id = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.LIST:
          self.target_list = []
          (_etype9, _size6) = iprot.readListBegin()
          for _i10 in xrange(_size6):
            _elem11 = User()
            _elem11.read(iprot)
            self.target_list.append(_elem11)
          iprot.readListEnd()
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
    oprot.writeStructBegin('Req')
    if self.user is not None:
      oprot.writeFieldBegin('user', TType.STRUCT, 1)
      self.user.write(oprot)
      oprot.writeFieldEnd()
    if self.num is not None:
      oprot.writeFieldBegin('num', TType.I32, 2)
      oprot.writeI32(self.num)
      oprot.writeFieldEnd()
    if self.exist_list is not None:
      oprot.writeFieldBegin('exist_list', TType.LIST, 3)
      oprot.writeListBegin(TType.STRUCT, len(self.exist_list))
      for iter12 in self.exist_list:
        iter12.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.expose_filter is not None:
      oprot.writeFieldBegin('expose_filter', TType.BOOL, 4)
      oprot.writeBool(self.expose_filter)
      oprot.writeFieldEnd()
    if self.abtest_parameters is not None:
      oprot.writeFieldBegin('abtest_parameters', TType.STRING, 5)
      oprot.writeString(self.abtest_parameters)
      oprot.writeFieldEnd()
    if self.channel_id is not None:
      oprot.writeFieldBegin('channel_id', TType.I32, 6)
      oprot.writeI32(self.channel_id)
      oprot.writeFieldEnd()
    if self.pos_id is not None:
      oprot.writeFieldBegin('pos_id', TType.I32, 7)
      oprot.writeI32(self.pos_id)
      oprot.writeFieldEnd()
    if self.target_list is not None:
      oprot.writeFieldBegin('target_list', TType.LIST, 8)
      oprot.writeListBegin(TType.STRUCT, len(self.target_list))
      for iter13 in self.target_list:
        iter13.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.user)
    value = (value * 31) ^ hash(self.num)
    value = (value * 31) ^ hash(self.exist_list)
    value = (value * 31) ^ hash(self.expose_filter)
    value = (value * 31) ^ hash(self.abtest_parameters)
    value = (value * 31) ^ hash(self.channel_id)
    value = (value * 31) ^ hash(self.pos_id)
    value = (value * 31) ^ hash(self.target_list)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Rsp:
  """
  Attributes:
   - Creater_list
   - status
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'Creater_list', (TType.STRUCT,(User, User.thrift_spec)), None, ), # 1
    (2, TType.I32, 'status', None,     0, ), # 2
  )

  def __init__(self, Creater_list=None, status=thrift_spec[2][4],):
    self.Creater_list = Creater_list
    self.status = status

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
        if ftype == TType.LIST:
          self.Creater_list = []
          (_etype17, _size14) = iprot.readListBegin()
          for _i18 in xrange(_size14):
            _elem19 = User()
            _elem19.read(iprot)
            self.Creater_list.append(_elem19)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.status = iprot.readI32()
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
    oprot.writeStructBegin('Rsp')
    if self.Creater_list is not None:
      oprot.writeFieldBegin('Creater_list', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.Creater_list))
      for iter20 in self.Creater_list:
        iter20.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.I32, 2)
      oprot.writeI32(self.status)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.Creater_list)
    value = (value * 31) ^ hash(self.status)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
