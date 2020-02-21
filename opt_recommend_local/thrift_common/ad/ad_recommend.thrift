namespace cpp ad_recommend
namespace py ad_recommend

struct User{
    1: string uid,
    2: i32 uid_type,
    3: optional i64 user_id=0,
}

struct AdWeight{
    1: i32 creative_id,
    2: double score,
    3: i32 unit_id,
    4: i32 campaign_id,
    5: i32 user_id,
    6: i64 bid_price,
    7: i32 click_num,
    8: i32 impr_num,
    9: i16 cost_type,
    10: i64 app_id,
    11: i16 industry,
    12: i32 imp_frequency,
    13: i16 ad_type,
    14: i16 group_op,
    15: list<i32> groups,
}

// 定向条件
// 1.计费类型 cpc、cpm、cpt
// 2.时间定向
// 3.地域
// 4.手机品牌
// 5.网络环境
// 支持cpc or cpm广告

struct TargetingSolid{
    1: i32 slot_id,
    2: i32 target_id,
}

struct Req{
    1: User user;
    2: i32 count=1000;
    3: list<TargetingSolid> targeting_solids;
    4: optional list<i32> filter_creative_ids;
    5: optional string abtest_parameters;
    6: optional list<i32> filter_unit_ids;
    7: optional list<i32> filter_user_ids;
    8: optional list<i64> filter_app_ids;
    9: optional list<i32> keep_industry_ids;
    10: optional list<i32> filter_industry_ids;
}

struct Rsp{
    1: list< AdWeight > ad_list,
}

service AdRecommend{
    Rsp get(1:Req req),
}
