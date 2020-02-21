namespace cpp maitreya
namespace py maitreya

struct Video
{
    1: i64 content_id,
    2: double score,
    3: string strategy,
    4: optional map<string, string> video_info={},
}

struct Req
{
    1: i32 uid_type,
    2: string uid,
    3: string app_id,
    4: i32 channel_id,
    5: i32 start_time,
    6: i32 end_time,
    7: i32 count = 40,
    8: string abtest_parameters='',
    9: optional string impression_id='',
    10: optional map<string, string> context_info={},
    11: optional i64 user_id=0,
}

struct Rsp
{
    1: string status = '',
    2: list<Video> videos,
}

service Maitreya
{
    Rsp get_video_list(1:Req req),
}
