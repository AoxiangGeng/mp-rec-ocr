#!/usr/local/bin/thrift --gen py -r -o .
namespace py impression

struct WriteReq
{
    1: i32 uid_type;
    2: string uid;
    3: list<i64> new_impr_video;
    4: i32 channal_id;
}

struct WriteRsp
{
    1: string status = '';
    2: i32 count=0;
}

struct ReadReq
{
    1: i32 uid_type;
    2: string uid;
    3: i32 start_time;
    4: i32 end_time;
    5: optional i32 channel_id=0;
}

struct ReadRsp
{
    1: string status = '';
    2: list<i64> hist_impr_video;
}

service ImpressionService
{
    ReadRsp read_impressions(1: ReadReq req);
    WriteRsp write_impressions(1: WriteReq req);
}
