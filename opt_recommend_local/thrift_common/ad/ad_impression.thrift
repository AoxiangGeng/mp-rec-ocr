#!/usr/local/bin/thrift --gen cpp  --gen py --gen go

namespace cpp ad_impression
namespace py ad_impression
namespace go ad_impression

struct ImpressionItem{
   1: i32 campaign_id,  # 广告计划id
   2: i32 creative_id,  # 广告创意id
   3: optional i32 user_id, # 广告主id
   4: optional i32 unit_id,  # 广告单元id
   5: optional i32 timestamp,   # 展现时间s
   6: optional i32 source,      #广告来源
   7: optional i16 pos_id,      #广告位id
}

service AdsImpression {
      // getter
      # 获取用户最近展现广告，详细
      list<ImpressionItem> get_ads_impression(
                           1: string udid, 2: i32 count=10000,
                           3: i32 start_time=0, 4: i32 end_time=0),

      # 写用户广告展现，true为成功写入，其他为异常
      bool put_ads_impressions(1: string udid, 2: list<ImpressionItem> imprs)
}
