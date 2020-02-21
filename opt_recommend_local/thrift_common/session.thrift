#!/usr/local/bin/thrift --gen py --gen cpp -r -o . 
struct Req
{
    1: string user,
    2: optional list<i64> cids,
    3: optional string req_id,
}

struct Rsp
{
    1: string status = 'failed',
    2: string session_feature,
}

service Session
{
    Rsp get_session_feature(1:Req req),
}