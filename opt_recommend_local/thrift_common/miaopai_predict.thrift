#!/usr/local/bin/thrift --gen py --gen cpp -r -o .
namespace cpp seraph.miaopai
namespace py seraph.miaopai

struct Req
{
    1: string user,
    2: i32 reg_time = 0,
    3: i32 start_time,
    4: i32 end_time,
    5: i32 count=50,
    6: string req_id,
    7: list<i64> ids,
    8: string abtest_parameters,
    9: bool debug_enable = 0,
    10: string ab_id,
    11: optional string json_context_info,
    12: optional string json_user_info,
    13: optional list<string> json_content_info,
    14: optional list<string> json_author_info,
}

struct SortContent
{
    2: i64 id,
    3: double score,
}

struct Rsp
{
     1: list<SortContent> contents,
     2: string status = '',
     3: optional list<string> features="";
}

service Predict
{
    Rsp predict(1:Req req),
    oneway void drop_predict(1:Req req),
}

