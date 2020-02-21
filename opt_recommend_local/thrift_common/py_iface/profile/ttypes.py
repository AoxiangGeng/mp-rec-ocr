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



class User:
  """
  Attributes:
   - uid_type
   - uid
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'uid_type', None, None, ), # 1
    (2, TType.STRING, 'uid', None, None, ), # 2
  )

  def __init__(self, uid_type=None, uid=None,):
    self.uid_type = uid_type
    self.uid = uid

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
          self.uid_type = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.uid = iprot.readString();
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
    if self.uid_type is not None:
      oprot.writeFieldBegin('uid_type', TType.I32, 1)
      oprot.writeI32(self.uid_type)
      oprot.writeFieldEnd()
    if self.uid is not None:
      oprot.writeFieldBegin('uid', TType.STRING, 2)
      oprot.writeString(self.uid)
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

class Topic:
  """
  Attributes:
   - topic_id
   - weight
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'topic_id', None, None, ), # 1
    (2, TType.DOUBLE, 'weight', None, None, ), # 2
  )

  def __init__(self, topic_id=None, weight=None,):
    self.topic_id = topic_id
    self.weight = weight

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
          self.topic_id = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.DOUBLE:
          self.weight = iprot.readDouble();
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
    oprot.writeStructBegin('Topic')
    if self.topic_id is not None:
      oprot.writeFieldBegin('topic_id', TType.I32, 1)
      oprot.writeI32(self.topic_id)
      oprot.writeFieldEnd()
    if self.weight is not None:
      oprot.writeFieldBegin('weight', TType.DOUBLE, 2)
      oprot.writeDouble(self.weight)
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

class UserProfile:
  """
  Attributes:
   - user
   - keywords
   - reg_time
   - follow
   - topic_2048
   - long_topic_2048
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'user', (User, User.thrift_spec), None, ), # 1
    (2, TType.LIST, 'keywords', (TType.STRING,None), None, ), # 2
    (3, TType.I64, 'reg_time', None, None, ), # 3
    (4, TType.LIST, 'follow', (TType.STRING,None), None, ), # 4
    (5, TType.LIST, 'topic_2048', (TType.STRUCT,(Topic, Topic.thrift_spec)), None, ), # 5
    (6, TType.LIST, 'long_topic_2048', (TType.STRUCT,(Topic, Topic.thrift_spec)), None, ), # 6
  )

  def __init__(self, user=None, keywords=None, reg_time=None, follow=None, topic_2048=None, long_topic_2048=None,):
    self.user = user
    self.keywords = keywords
    self.reg_time = reg_time
    self.follow = follow
    self.topic_2048 = topic_2048
    self.long_topic_2048 = long_topic_2048

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
        if ftype == TType.LIST:
          self.keywords = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = iprot.readString();
            self.keywords.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.reg_time = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.LIST:
          self.follow = []
          (_etype9, _size6) = iprot.readListBegin()
          for _i10 in xrange(_size6):
            _elem11 = iprot.readString();
            self.follow.append(_elem11)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.LIST:
          self.topic_2048 = []
          (_etype15, _size12) = iprot.readListBegin()
          for _i16 in xrange(_size12):
            _elem17 = Topic()
            _elem17.read(iprot)
            self.topic_2048.append(_elem17)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.LIST:
          self.long_topic_2048 = []
          (_etype21, _size18) = iprot.readListBegin()
          for _i22 in xrange(_size18):
            _elem23 = Topic()
            _elem23.read(iprot)
            self.long_topic_2048.append(_elem23)
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
    oprot.writeStructBegin('UserProfile')
    if self.user is not None:
      oprot.writeFieldBegin('user', TType.STRUCT, 1)
      self.user.write(oprot)
      oprot.writeFieldEnd()
    if self.keywords is not None:
      oprot.writeFieldBegin('keywords', TType.LIST, 2)
      oprot.writeListBegin(TType.STRING, len(self.keywords))
      for iter24 in self.keywords:
        oprot.writeString(iter24)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.reg_time is not None:
      oprot.writeFieldBegin('reg_time', TType.I64, 3)
      oprot.writeI64(self.reg_time)
      oprot.writeFieldEnd()
    if self.follow is not None:
      oprot.writeFieldBegin('follow', TType.LIST, 4)
      oprot.writeListBegin(TType.STRING, len(self.follow))
      for iter25 in self.follow:
        oprot.writeString(iter25)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.topic_2048 is not None:
      oprot.writeFieldBegin('topic_2048', TType.LIST, 5)
      oprot.writeListBegin(TType.STRUCT, len(self.topic_2048))
      for iter26 in self.topic_2048:
        iter26.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.long_topic_2048 is not None:
      oprot.writeFieldBegin('long_topic_2048', TType.LIST, 6)
      oprot.writeListBegin(TType.STRUCT, len(self.long_topic_2048))
      for iter27 in self.long_topic_2048:
        iter27.write(oprot)
      oprot.writeListEnd()
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

class GroupProfile:
  """
  Attributes:
   - content_id
   - keywords
   - author_id
   - duration
   - crawl_play_num
   - crawl_comment_num
   - crawl_digg
   - crawl_bury
   - crawl_favorite
   - category
   - author_level
   - digg
   - bury
   - play_num
   - comment_num
   - click_rate
   - avg_play_time
   - favorite
   - topic_2048
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'content_id', None, None, ), # 1
    (2, TType.LIST, 'keywords', (TType.STRING,None), None, ), # 2
    (3, TType.I64, 'author_id', None, None, ), # 3
    (4, TType.I32, 'duration', None, None, ), # 4
    (5, TType.I32, 'crawl_play_num', None, None, ), # 5
    (6, TType.I32, 'crawl_comment_num', None, None, ), # 6
    (7, TType.I32, 'crawl_digg', None, None, ), # 7
    (8, TType.I32, 'crawl_bury', None, None, ), # 8
    (9, TType.I32, 'crawl_favorite', None, None, ), # 9
    (10, TType.STRING, 'category', None, None, ), # 10
    (11, TType.I32, 'author_level', None, None, ), # 11
    (12, TType.I32, 'digg', None, None, ), # 12
    (13, TType.I32, 'bury', None, None, ), # 13
    (14, TType.I32, 'play_num', None, None, ), # 14
    (15, TType.I32, 'comment_num', None, None, ), # 15
    (16, TType.DOUBLE, 'click_rate', None, None, ), # 16
    (17, TType.DOUBLE, 'avg_play_time', None, None, ), # 17
    (18, TType.DOUBLE, 'favorite', None, None, ), # 18
    (19, TType.LIST, 'topic_2048', (TType.STRUCT,(Topic, Topic.thrift_spec)), None, ), # 19
  )

  def __init__(self, content_id=None, keywords=None, author_id=None, duration=None, crawl_play_num=None, crawl_comment_num=None, crawl_digg=None, crawl_bury=None, crawl_favorite=None, category=None, author_level=None, digg=None, bury=None, play_num=None, comment_num=None, click_rate=None, avg_play_time=None, favorite=None, topic_2048=None,):
    self.content_id = content_id
    self.keywords = keywords
    self.author_id = author_id
    self.duration = duration
    self.crawl_play_num = crawl_play_num
    self.crawl_comment_num = crawl_comment_num
    self.crawl_digg = crawl_digg
    self.crawl_bury = crawl_bury
    self.crawl_favorite = crawl_favorite
    self.category = category
    self.author_level = author_level
    self.digg = digg
    self.bury = bury
    self.play_num = play_num
    self.comment_num = comment_num
    self.click_rate = click_rate
    self.avg_play_time = avg_play_time
    self.favorite = favorite
    self.topic_2048 = topic_2048

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
        if ftype == TType.I64:
          self.content_id = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.LIST:
          self.keywords = []
          (_etype31, _size28) = iprot.readListBegin()
          for _i32 in xrange(_size28):
            _elem33 = iprot.readString();
            self.keywords.append(_elem33)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.author_id = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I32:
          self.duration = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.crawl_play_num = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.I32:
          self.crawl_comment_num = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.I32:
          self.crawl_digg = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.I32:
          self.crawl_bury = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.I32:
          self.crawl_favorite = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 10:
        if ftype == TType.STRING:
          self.category = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 11:
        if ftype == TType.I32:
          self.author_level = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 12:
        if ftype == TType.I32:
          self.digg = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 13:
        if ftype == TType.I32:
          self.bury = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 14:
        if ftype == TType.I32:
          self.play_num = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 15:
        if ftype == TType.I32:
          self.comment_num = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 16:
        if ftype == TType.DOUBLE:
          self.click_rate = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 17:
        if ftype == TType.DOUBLE:
          self.avg_play_time = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 18:
        if ftype == TType.DOUBLE:
          self.favorite = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 19:
        if ftype == TType.LIST:
          self.topic_2048 = []
          (_etype37, _size34) = iprot.readListBegin()
          for _i38 in xrange(_size34):
            _elem39 = Topic()
            _elem39.read(iprot)
            self.topic_2048.append(_elem39)
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
    oprot.writeStructBegin('GroupProfile')
    if self.content_id is not None:
      oprot.writeFieldBegin('content_id', TType.I64, 1)
      oprot.writeI64(self.content_id)
      oprot.writeFieldEnd()
    if self.keywords is not None:
      oprot.writeFieldBegin('keywords', TType.LIST, 2)
      oprot.writeListBegin(TType.STRING, len(self.keywords))
      for iter40 in self.keywords:
        oprot.writeString(iter40)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.author_id is not None:
      oprot.writeFieldBegin('author_id', TType.I64, 3)
      oprot.writeI64(self.author_id)
      oprot.writeFieldEnd()
    if self.duration is not None:
      oprot.writeFieldBegin('duration', TType.I32, 4)
      oprot.writeI32(self.duration)
      oprot.writeFieldEnd()
    if self.crawl_play_num is not None:
      oprot.writeFieldBegin('crawl_play_num', TType.I32, 5)
      oprot.writeI32(self.crawl_play_num)
      oprot.writeFieldEnd()
    if self.crawl_comment_num is not None:
      oprot.writeFieldBegin('crawl_comment_num', TType.I32, 6)
      oprot.writeI32(self.crawl_comment_num)
      oprot.writeFieldEnd()
    if self.crawl_digg is not None:
      oprot.writeFieldBegin('crawl_digg', TType.I32, 7)
      oprot.writeI32(self.crawl_digg)
      oprot.writeFieldEnd()
    if self.crawl_bury is not None:
      oprot.writeFieldBegin('crawl_bury', TType.I32, 8)
      oprot.writeI32(self.crawl_bury)
      oprot.writeFieldEnd()
    if self.crawl_favorite is not None:
      oprot.writeFieldBegin('crawl_favorite', TType.I32, 9)
      oprot.writeI32(self.crawl_favorite)
      oprot.writeFieldEnd()
    if self.category is not None:
      oprot.writeFieldBegin('category', TType.STRING, 10)
      oprot.writeString(self.category)
      oprot.writeFieldEnd()
    if self.author_level is not None:
      oprot.writeFieldBegin('author_level', TType.I32, 11)
      oprot.writeI32(self.author_level)
      oprot.writeFieldEnd()
    if self.digg is not None:
      oprot.writeFieldBegin('digg', TType.I32, 12)
      oprot.writeI32(self.digg)
      oprot.writeFieldEnd()
    if self.bury is not None:
      oprot.writeFieldBegin('bury', TType.I32, 13)
      oprot.writeI32(self.bury)
      oprot.writeFieldEnd()
    if self.play_num is not None:
      oprot.writeFieldBegin('play_num', TType.I32, 14)
      oprot.writeI32(self.play_num)
      oprot.writeFieldEnd()
    if self.comment_num is not None:
      oprot.writeFieldBegin('comment_num', TType.I32, 15)
      oprot.writeI32(self.comment_num)
      oprot.writeFieldEnd()
    if self.click_rate is not None:
      oprot.writeFieldBegin('click_rate', TType.DOUBLE, 16)
      oprot.writeDouble(self.click_rate)
      oprot.writeFieldEnd()
    if self.avg_play_time is not None:
      oprot.writeFieldBegin('avg_play_time', TType.DOUBLE, 17)
      oprot.writeDouble(self.avg_play_time)
      oprot.writeFieldEnd()
    if self.favorite is not None:
      oprot.writeFieldBegin('favorite', TType.DOUBLE, 18)
      oprot.writeDouble(self.favorite)
      oprot.writeFieldEnd()
    if self.topic_2048 is not None:
      oprot.writeFieldBegin('topic_2048', TType.LIST, 19)
      oprot.writeListBegin(TType.STRUCT, len(self.topic_2048))
      for iter41 in self.topic_2048:
        iter41.write(oprot)
      oprot.writeListEnd()
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

class UserProfileGetReq:
  """
  Attributes:
   - user_list
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'user_list', (TType.STRUCT,(User, User.thrift_spec)), None, ), # 1
  )

  def __init__(self, user_list=None,):
    self.user_list = user_list

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
          self.user_list = []
          (_etype45, _size42) = iprot.readListBegin()
          for _i46 in xrange(_size42):
            _elem47 = User()
            _elem47.read(iprot)
            self.user_list.append(_elem47)
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
    oprot.writeStructBegin('UserProfileGetReq')
    if self.user_list is not None:
      oprot.writeFieldBegin('user_list', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.user_list))
      for iter48 in self.user_list:
        iter48.write(oprot)
      oprot.writeListEnd()
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

class UserProfileGetRsp:
  """
  Attributes:
   - user_profile_list
   - status
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'user_profile_list', (TType.STRUCT,(UserProfile, UserProfile.thrift_spec)), None, ), # 1
    (2, TType.STRING, 'status', None, None, ), # 2
  )

  def __init__(self, user_profile_list=None, status=None,):
    self.user_profile_list = user_profile_list
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
          self.user_profile_list = []
          (_etype52, _size49) = iprot.readListBegin()
          for _i53 in xrange(_size49):
            _elem54 = UserProfile()
            _elem54.read(iprot)
            self.user_profile_list.append(_elem54)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.status = iprot.readString();
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
    oprot.writeStructBegin('UserProfileGetRsp')
    if self.user_profile_list is not None:
      oprot.writeFieldBegin('user_profile_list', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.user_profile_list))
      for iter55 in self.user_profile_list:
        iter55.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.STRING, 2)
      oprot.writeString(self.status)
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

class UserProfilePutReq:
  """
  Attributes:
   - user_profiles
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'user_profiles', (TType.STRUCT,(UserProfile, UserProfile.thrift_spec)), None, ), # 1
  )

  def __init__(self, user_profiles=None,):
    self.user_profiles = user_profiles

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
          self.user_profiles = []
          (_etype59, _size56) = iprot.readListBegin()
          for _i60 in xrange(_size56):
            _elem61 = UserProfile()
            _elem61.read(iprot)
            self.user_profiles.append(_elem61)
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
    oprot.writeStructBegin('UserProfilePutReq')
    if self.user_profiles is not None:
      oprot.writeFieldBegin('user_profiles', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.user_profiles))
      for iter62 in self.user_profiles:
        iter62.write(oprot)
      oprot.writeListEnd()
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

class UserProfilePutRsp:
  """
  Attributes:
   - status
   - count
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'status', None, None, ), # 1
    (2, TType.I32, 'count', None, None, ), # 2
  )

  def __init__(self, status=None, count=None,):
    self.status = status
    self.count = count

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
          self.status = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.count = iprot.readI32();
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
    oprot.writeStructBegin('UserProfilePutRsp')
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.STRING, 1)
      oprot.writeString(self.status)
      oprot.writeFieldEnd()
    if self.count is not None:
      oprot.writeFieldBegin('count', TType.I32, 2)
      oprot.writeI32(self.count)
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

class GroupProfileGetReq:
  """
  Attributes:
   - video_list
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'video_list', (TType.I64,None), None, ), # 1
  )

  def __init__(self, video_list=None,):
    self.video_list = video_list

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
          self.video_list = []
          (_etype66, _size63) = iprot.readListBegin()
          for _i67 in xrange(_size63):
            _elem68 = iprot.readI64();
            self.video_list.append(_elem68)
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
    oprot.writeStructBegin('GroupProfileGetReq')
    if self.video_list is not None:
      oprot.writeFieldBegin('video_list', TType.LIST, 1)
      oprot.writeListBegin(TType.I64, len(self.video_list))
      for iter69 in self.video_list:
        oprot.writeI64(iter69)
      oprot.writeListEnd()
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

class GroupProfileGetRsp:
  """
  Attributes:
   - group_profile_list
   - status
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'group_profile_list', (TType.STRUCT,(GroupProfile, GroupProfile.thrift_spec)), None, ), # 1
    (2, TType.STRING, 'status', None, None, ), # 2
  )

  def __init__(self, group_profile_list=None, status=None,):
    self.group_profile_list = group_profile_list
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
          self.group_profile_list = []
          (_etype73, _size70) = iprot.readListBegin()
          for _i74 in xrange(_size70):
            _elem75 = GroupProfile()
            _elem75.read(iprot)
            self.group_profile_list.append(_elem75)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.status = iprot.readString();
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
    oprot.writeStructBegin('GroupProfileGetRsp')
    if self.group_profile_list is not None:
      oprot.writeFieldBegin('group_profile_list', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.group_profile_list))
      for iter76 in self.group_profile_list:
        iter76.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.STRING, 2)
      oprot.writeString(self.status)
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

class GroupProfilePutReq:
  """
  Attributes:
   - group_profile_list
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'group_profile_list', (TType.STRUCT,(GroupProfile, GroupProfile.thrift_spec)), None, ), # 1
  )

  def __init__(self, group_profile_list=None,):
    self.group_profile_list = group_profile_list

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
          self.group_profile_list = []
          (_etype80, _size77) = iprot.readListBegin()
          for _i81 in xrange(_size77):
            _elem82 = GroupProfile()
            _elem82.read(iprot)
            self.group_profile_list.append(_elem82)
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
    oprot.writeStructBegin('GroupProfilePutReq')
    if self.group_profile_list is not None:
      oprot.writeFieldBegin('group_profile_list', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.group_profile_list))
      for iter83 in self.group_profile_list:
        iter83.write(oprot)
      oprot.writeListEnd()
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

class GroupProfilePutRsp:
  """
  Attributes:
   - status
   - count
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'status', None, None, ), # 1
    (2, TType.I32, 'count', None, None, ), # 2
  )

  def __init__(self, status=None, count=None,):
    self.status = status
    self.count = count

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
          self.status = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.count = iprot.readI32();
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
    oprot.writeStructBegin('GroupProfilePutRsp')
    if self.status is not None:
      oprot.writeFieldBegin('status', TType.STRING, 1)
      oprot.writeString(self.status)
      oprot.writeFieldEnd()
    if self.count is not None:
      oprot.writeFieldBegin('count', TType.I32, 2)
      oprot.writeI32(self.count)
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
