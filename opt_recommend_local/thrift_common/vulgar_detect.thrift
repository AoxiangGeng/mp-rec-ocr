namespace cpp vulgar_detect
namespace py vulgar_detect
namespace go vulgar_detect

struct Req{
    1: string image_uri,
    2: string title,
}

struct Rsp{
    1: i32 is_safe,
    2: double image_safe_score,
    3: double image_unsafe_score,
    4: double title_safe_score,
    5: double title_unsafe_score,
    6: string reason,
}
service VulgarDetect {
    Rsp get(1:Req req),
    list<Rsp> gets(1:list<Req> reqs),
}
