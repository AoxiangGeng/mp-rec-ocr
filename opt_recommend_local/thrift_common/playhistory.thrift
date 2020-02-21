#!/usr/local/bin/thrift --gen cpp  --gen py --gen go

namespace cpp playhistory
namespace py playhistory
namespace go playhistory

struct PlayHistoryReq {
      1:string    app,        // "bb", "mp"
      2:string    udid,
      3:i32       count,
      4:list<i32> sources,
      5:i64       startTime,
      6: optional i32 typ,    // 种类，0全部，1视频，2图文；默认视频
}

struct PlayHistoryRes {
      1:i64 cid,
      2:i32 source,
      3:i32 playDuration
      4:i64 timestamp,
      5: optional i32 typ,    // 种类，1视频，2图文
      6: optional i64 aid,    // 作者id
}

service PlayHistory {
      // 获取用户最近观看的视频
      list<PlayHistoryRes>       getPlayHistory(1:PlayHistoryReq req),

      // 批量获取用户最近观看的视频
      map<string,list<PlayHistoryRes>> getGroupPlayHistory(1:list<PlayHistoryReq> reqs),
}
