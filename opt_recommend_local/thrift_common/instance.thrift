#!/usr/local/bin/thrift --gen cpp  --gen py

namespace cpp instance
namespace py instance

struct Instance {
      1:string uid,
      2:i64 content_id,
      3:i32 create_time,
      4:string features,
      5:string impression_id,
}

struct InstancePutReq {
      1:list<Instance> instance_list,
}

struct InstancePutRsp {
      1:string status,
      2:i32 count,
}

service InstanceService {
      // getter
      InstancePutRsp put_instance(1:InstancePutReq req),
}
