#!/usr/local/bin/thrift --gen cpp  --gen py --gen go

namespace cpp idkv
namespace py idkv
namespace go idkv

service IdKvServer {
      // 获取objectID
      i64 getID(1:string object),
      
      // 获取object值
      string getObject(1:i64 id),

      // 批量获取objectID
      list<i64> getGroupID(1:list<string> objects),
      
      // 批量获取object值
      list<string> getGroupObject(1:list<i64> ids),
}
