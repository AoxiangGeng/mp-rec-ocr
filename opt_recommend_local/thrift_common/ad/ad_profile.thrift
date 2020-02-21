namespace cpp ad_profile
namespace py ad_profile
namespace go ad_profile

struct KV {
    1: i64 key,
    2: double weight,
}

struct AD {
    1: i32 creative_id,
    2: optional i32 ad_user_id,
    3: optional string title,
    4: optional string image_url,
    5: optional string sponsor_name,
    6: optional i16 industry_catagory,
    7: optional i32 campaign_id,
    8: optional i32 unit_id,
    9: optional i64 bid_price,
    10: optional i16 cost_type,
    11: optional i16 creative_type,
    12: optional i32 create_time,
    13: optional i32 start_time,
    14: optional i32 end_time,
    15: optional i16 product_type,
    16: optional string landing_url,
    17: optional string ext,
    18: optional i64 unit_day_budget,
    19: optional i64 camp_day_budget,
    20: optional string monitor_url,
    21: optional list<KV> area_code,
    22: optional list<KV> device_brand,
    23: optional list<KV> network,
    24: optional list<i64> time_target,
    25: optional i64 balance,
    26: optional i32 impr_num,
    27: optional i32 click_num,
    28: optional i16 status, #2为在线，其他为下线
    29: optional i64 unit_day_cost, # 单元日消耗
    30: optional i64 camp_day_cost, # 计划日消耗
    31: optional i32 unit_impr_num, # 单元总展现
    32: optional i32 unit_click_num, # 单元总点击
    33: optional i32 camp_impr_num, # 计划总展现
    34: optional i32 camp_click_num, # 计划总点击
    35: optional i32 creative_day_impr_num, # 创意当日展现
    36: optional i32 creative_day_click_num, # 创意当日点击
    37: optional string download_url,
    38: optional string sponsor_icon, # 头像url
    39: optional string package_info, # 下载包信息
    40: optional i16 btn_text_key, #创意按钮类型
    41: optional string btn_text_value, #创意按钮内容
    42: optional string video_resource,     #视频信息
    43: optional i32 quantity, #
    44: optional i32 unit_day_impr_num, #单元日展现
    45: optional string ad_title_keyword,     // 广告keyword
}

struct ADGetReq {
    1: list<i32> creative_id_list,
}

struct ADGetRsp {
    1: list<AD> ad_list,
    2: string status,
}

struct ADPutReq {
    1: list<AD> ad_list,
}

struct ADPutRsp {
    1: string status,
    2: i32 count,
}

service ADProfile {
    ADGetRsp get_ad_profiles(1:ADGetReq req),
    ADPutRsp put_ad_profiles(1:ADPutReq req),
}

