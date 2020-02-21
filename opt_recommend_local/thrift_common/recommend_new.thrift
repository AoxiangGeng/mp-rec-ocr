namespace cpp recommend
namespace py recommend

struct User{
    1: string uid,
    2: i32 uid_type,
    3: optional i64 user_id=0,
}

struct VideoWeight{
    1: i64 content_id,
    2: double weight,
}

struct Req{
    1: User user;
    2: i32 start_time=0;
    3: i32 end_time=0;
    4: i32 count=1000;
    5: optional i32 channel_id=0;
    6: optional string strategy;
    7: optional string abtest_parameters;
    8: optional map<string,string> info={}
    9: optional list<i64> video_candidate = [];
    10:optional list<i64> impr_gids;
    11:optional list<i64> filter_gids;
    12:optional string context_info_json;
}

struct Rsp{
    1: list< VideoWeight > video_list,
    2: User user,
}

service Recommend{
    Rsp get(1:Req req),
    list<Rsp> gets(1:list<Req> reqs),
}
