namespace cpp profile_kd
namespace py profile_kd
namespace go profile_kd

struct KV {
    1: i64 key,
    2: double weight,
}

struct Content {
    1: i64 cid,
    2: optional list<KV> c_category,
    3: optional list<KV> c_keyword,
    4: optional list<KV> c_topic,
    5: optional i64 c_author_id
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
    45: optional i32 c_pool,
    46: optional i32 c_online_time,
    47: optional i32 c_video_quality,
    48: optional list<KV> c_tags_class,
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
    // getter
    ContentProfileGetRsp get_content_profiles(1:ContentProfileGetReq req),
    UserProfileGetRsp get_user_profiles(1:UserProfileGetReq req),
    // 根据aid取author profile
    AuthorProfileAidGetRsp get_author_aid_profiles(1:AuthorProfileAidGetReq req),
    // 根据cid取author profile
    AuthorProfileCidGetRsp get_author_cid_profiles(1:AuthorProfileCidGetReq req),

    // setter
    ProfilePutRsp put_content_profiles(1:ContentProfilePutReq req),
    ProfilePutRsp put_user_profiles(1:UserProfilePutReq req),
    ProfilePutRsp put_author_profiles(1:AuthorProfilePutReq req),
}


