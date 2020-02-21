namespace cpp profile
namespace py profile

struct User {
    1: i32 uid_type,
    2: string uid
}

struct Topic {
    1: i32 topic_id,
    2: double weight,
}

struct UserProfile {
    1: User user,
    2: list<string> keywords,
    3: i64 reg_time,
    4: list<string> follow,
    5: list<Topic> topic_2048,
    6: list<Topic> long_topic_2048,
}

struct GroupProfile {
    1: i64 content_id,
    2: list<string> keywords,
    3: i64 author_id,
    4: i32 duration,
    5: i32 crawl_play_num,
    6: i32 crawl_comment_num,
    7: i32 crawl_digg,
    8: i32 crawl_bury,
    9: i32 crawl_favorite,
    10: string category,
    11: i32 author_level,
    12: i32 digg,
    13: i32 bury,
    14: i32 play_num,
    15: i32 comment_num,
    16: double click_rate,
    17: double avg_play_time,
    18: double favorite,
    19: list<Topic> topic_2048,
}

struct UserProfileGetReq {
    1: list<User> user_list,
}

struct UserProfileGetRsp {
    1: list<UserProfile> user_profile_list,
    2: string status,
}

struct UserProfilePutReq {
    1: list<UserProfile> user_profiles,
}

struct UserProfilePutRsp {
    1: string status,
    2: i32 count
}

struct GroupProfileGetReq {
    1: list<i64> video_list,
}

struct GroupProfileGetRsp {
    1: list<GroupProfile> group_profile_list,
    2: string status,
}

struct GroupProfilePutReq {
    1: list<GroupProfile> group_profile_list,
}

struct GroupProfilePutRsp {
    1: string status,
    2: i32 count
}

service Profile {
    // getter
    UserProfileGetRsp get_user_profiles(1:UserProfileGetReq req),
    GroupProfileGetRsp get_group_profiles(1:GroupProfileGetReq req),

    // setter
    UserProfilePutRsp put_user_profiles(1:UserProfilePutReq req),
    GroupProfilePutRsp put_group_profiles(1:GroupProfilePutReq req),
}

