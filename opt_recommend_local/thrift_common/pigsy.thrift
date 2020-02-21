include "recommend.thrift"
namespace cpp pigsy

struct GroupVec{
  1:i64 gid,
  2:list<double> vec,
}

struct RspVec{
  1:list< GroupVec > group_vec_list,
}

typedef recommend.Req Req

service PigsyServer extends recommend.Recommend
{
  RspVec get_group_vec(1:Req req)
}

