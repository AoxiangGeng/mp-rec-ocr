namespace cpp lda
namespace py lda

struct Topic{
    1: i32 topic_id,
    2: double weight,
}

struct ContentInfo{
    1: i64 content_id,
    2: string title,
    3: string desc,
    4: list<Topic> topic_list = [],
}

struct ContentTopicReq{
    1: list<ContentInfo> content_list = [],
}

struct ContentTopicRsp{
    1: list<ContentInfo> content_list = [],
    2: string status,
}

service LdaService{
    ContentTopicRsp get_content_topic(1:ContentTopicReq req)
}
