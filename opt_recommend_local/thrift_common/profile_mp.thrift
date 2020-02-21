namespace cpp profile_mp
namespace py profile_mp
namespace go profile_mp

struct KV {
    1: i64 key,
    2: double weight,
}

// 广告

struct AD {
    1: i32 creative_id,                         // "素材"id
    2: optional i32 ad_user_id,                 // "广告主"id
    3: optional string title,                   // 广告标题
    4: optional string image_url,               // 广告图片url
    5: optional string sponsor_name,            // 广告赞助商名称
    6: optional i16 industry_catagory,          // 行业分类
    7: optional i32 campaign_id,                // "推广计划"id
    8: optional i32 unit_id,                    // "广告单元"id
    9: optional i64 bid_price,                  // 广告出价
    10: optional i16 cost_type,                 // 扣费类型
    11: optional i16 creative_type,             // 创意类型
    12: optional i32 create_time,               // 广告创建时间
    13: optional i32 start_time,                // 广告开始时间
    14: optional i32 end_time,                  // 广告结束时间
    15: optional i16 product_type,              // 推广商品类型
    16: optional string landing_url,            // 落地页 地址
    17: optional string ext,                    // 扩展字段json
    18: optional i64 unit_day_budget,           // 广告单元 日预算
    19: optional i64 camp_day_budget,           // 推广计划 日预算
    20: optional string monitor_url,            // 第三方检测 地址
    21: optional list<KV> area_code,            // 地域定向
    22: optional list<KV> device_brand,         // 设备品牌定向
    23: optional list<KV> network,              // 网络定向
    24: optional list<i64> time_target,         // 投放时段定向
    25: optional i64 balance,                   // 账户余额
    26: optional i32 impr_num,                  // 展示次数
    27: optional i32 click_num,                 // 点击次数
    28: optional i16 status,                    // 广告上下线等状态
    29: optional i64 unit_day_cost,             // 广告单元 日花费
    30: optional i64 camp_day_cost,             // 推广计划 日花费
    31: optional i32 unit_impr_num,             // 广告单元 展示次数
    32: optional i32 unit_click_num,            // 广告单元 点击次数
    33: optional i32 camp_impr_num,             // 推广计划 展示次数
    34: optional i32 camp_click_num,            // 推广计划 点击次数
    35: optional i32 creative_day_impr_num,     // 创意 当日展现
    36: optional i32 creative_day_click_num,    // 创意 当日点击
    37: optional string download_url,           // 下载地址
    38: optional string sponsor_icon,           // 头像url
    39: optional string package_info,           // 下载包信息
    40: optional i16 btn_text_key,              // 创意按钮类型
    41: optional string btn_text_value,         // 创意按钮内容
    42: optional string video_resource,         // 视频信息
    43: optional i32 quantity,                  // 保量
    44: optional i32 unit_day_impr_num,         // 单元日展现
    45: optional string ad_title_keyword,       // 广告keyword
    46: optional i16 position,                  // 广告位
    47: optional string brush,                  // 刷次
    48: optional string schema_url,             // schema_url
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
struct Content {
    1: i64 cid,
    2: optional list<KV> c_category,
    3: optional list<KV> c_keyword,
    4: optional list<KV> c_topic,
    5: optional i64 c_author_id,
    6: optional i32 c_create_time,
    7: optional i32 c_duration,
    8: optional i32 c_down_num,
    9: optional i32 c_digg_num,
    10: optional i32 c_bury_num,
    11: optional i32 c_play_num,
    12: optional i32 c_comment_num,
    13: optional i32 c_favorate_num,
    14: optional i32 c_share_btn_num,
    15: optional i32 c_share_platform_num,
    16: optional i32 c_share_ok_num,
    17: optional i32 c_crawl_digg_num,
    18: optional i32 c_crawl_bury_num,
    19: optional i32 c_crawl_play_num,
    20: optional i32 c_crawl_comment_num,
    21: optional i32 c_crawl_favorate_num,
    22: optional i32 c_crawl_share_num,
    23: optional i32 c_cover_image,
    24: optional i32 c_title_len,
    25: optional i32 c_title_reo,
    26: optional i32 c_total_impr,
    27: optional i32 c_total_playtime,
    28: optional i32 c_title_regular,
    29: optional i32 c_title_semantic,
    30: optional i32 c_cover_content,
    31: optional i32 c_cover_resolution,
    32: optional i32 c_cover_cont_ads,
    33: optional i32 c_cover_vul,
    34: optional i32 c_video_watermark,
    35: optional i32 c_video_cont_ads,
    36: optional i32 c_video_original,
    37: optional i32 c_video_exclusive,
    38: optional i32 c_video_content_safe,
    39: optional i32 c_usertag,
    40: optional i32 c_enable,
    41: optional list<KV> c_usertags,
    42: optional i32 c_dislike_count,
    43: optional i32 c_shoot_type,
    44: optional list<KV> c_recommend_label,
    45: optional list<KV> c_enable_product,
    46: optional i32 c_total_show_time,
    47: optional i32 c_video_quality,
    48: optional i32 c_video_vul,
    49: optional i32 c_media_type,
    50: optional map<string,string> c_extend_info,
    51: optional list<KV> c_card_type,
    52: optional i32 c_pic_num,
    53: optional i32 c_article_length,
    54: optional i32 c_pic_down_num,
    55: optional double c_total_view_percent, 
    56: optional i32 c_feed_play_num,
    57: optional i32 c_total_feedplaytime,
    58: optional string c_rmd_location,
    59: optional string c_description,
}

struct User {
    1: string uid,
    2: optional i32 u_age,
    3: optional i32 u_gender,
    4: optional i32 u_area,
    5: optional list<KV> u_keyword,
    6: optional list<KV> u_follow,
    7: optional list<KV> u_video_topic,
    8: optional list<KV> u_cluster,
    9: optional list<KV> u_category,
    10: optional list<KV> u_search_keyword,
    11: optional i32 u_reg,
    12: optional list<KV> u_installed_apps,
    13: optional list<KV> u_dislike_authors,
    14: optional list<KV> u_dislike_keywords,
    15: optional list<KV> u_apps_category,
    16: optional i32 u_model_price,
    17: optional list<KV> u_dislike_category,
    18: optional i32 u_redpacket,
    19: optional list<KV> u_l_keyword,
    20: optional list<KV> u_l_video_topic,
    21: optional list<KV> u_l_category,
    22: optional map<i32,i32> u_redpacket_map,
    23: optional string u_device_platform,
    24: optional string u_device_brand,
    25: optional list<KV> u_active_time,
    26: optional i32 u_area_id,
    27: optional i32 u_app_id,
    28: optional list<KV> u_first_catg,
}

struct Author {
    1: i64 aid,
    2: optional i32 a_level,
    3: optional i32 a_fans,
    4: optional i32 a_category,
    5: optional i32 a_video_num,
    6: optional i32 a_video_play_num,
    7: optional i32 a_video_total_impr,
    8: optional i32 a_video_total_playtime,
    9: optional i32 a_video_fans_play_num,
    10: optional i32 a_video_fans_impr_num,
    11: optional i32 a_video_comment_num,
    12: optional i32 a_video_digg_num,
    13: optional i32 a_video_share_num,
    14: optional i32 a_star,
    15: optional i32 a_rec_hold,
}

struct CidAuthor {
    1: i64 cid,
    2: Author author,
}

struct ContentProfileGetReq {
    1: list<i64> cid_list,
}

struct ContentProfileGetRsp {
    1: list<Content> content_list,
    2: string status,
}

struct UserProfileGetReq {
    1: list<string> uid_list,
}

struct UserProfileGetRsp {
    1: list<User> user_list,
    2: string status,
}

struct AuthorProfileAidGetReq {
    1: list<i64> aid_list,
}

struct AuthorProfileAidGetRsp {
    1: list<Author> author_list,
    2: string status,
}

struct AuthorProfileCidGetReq {
    1: list<i64> cid_list,
}

struct AuthorProfileCidGetRsp {
    1: list<CidAuthor> c_author_list,
    2: string status,
}

struct ContentProfilePutReq {
    1: list<Content> content_list,
}

struct UserProfilePutReq {
    1: list<User> user_list,
}

struct AuthorProfilePutReq {
    1: list<Author> author_list,
}

struct ProfilePutRsp {
    1: string status,
    2: i32 count,
}

service Profile {
    // get
    ContentProfileGetRsp get_content_profiles(1:ContentProfileGetReq req),
    ContentProfileGetRsp get_content_profiles_nocache(1:ContentProfileGetReq req),
    UserProfileGetRsp get_user_profiles(1:UserProfileGetReq req),
    AuthorProfileAidGetRsp get_author_aid_profiles(1:AuthorProfileAidGetReq req),
    AuthorProfileCidGetRsp get_author_cid_profiles(1:AuthorProfileCidGetReq req),

    // put
    ProfilePutRsp put_content_profiles(1:ContentProfilePutReq req, 2:map<string,string> c),
    ProfilePutRsp put_user_profiles(1:UserProfilePutReq req, 2:map<string,string> c),
    ProfilePutRsp put_author_profiles(1:AuthorProfilePutReq req, 2:map<string,string> c),

    /* 
        1: profileTyp必须填写 只能填 "user","content","author", 否则无法写入
        2: data(二维map) 填写 id -> map(字段,值)  id不要包含redis前缀(如"user:")
        3: c 填写调用方服务名, key必须包含字段"name",且"name"不为空
    */
    ProfilePutRsp put_profiles(1:string profileTyp, 2:map<string,map<string,string>> data, 3:map<string,string> c),

    map<i64,bool> profile_author_exist(1:list<i64> req),

    ADGetRsp get_ad_profiles(1:ADGetReq req),
    ADPutRsp put_ad_profiles(1:ADPutReq req),

    //以下函数内部使用，调用方不用理会
    void notify_put(1:string profileTyp, 2:map<string,map<string,string>> data),
    void notify_ad_cache(1:ADPutReq req),
    ContentProfileGetRsp get_content_profiles_random(1:i32 count),
}

