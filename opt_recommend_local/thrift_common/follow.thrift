namespace cpp fol
namespace php fol

struct User{
    // Comment at: 2017-11-10
    // client请求的时候需要把udid和user_id都发送过来
    // server端返回的时候，只需要把user_id填充上即可
    // udid就代表设备id，但是user_id的含义需要根据uid_type
    // 来判断。判断逻辑在client/server端都是一样的。
    // 目前uid_type还没有使用, 只是为了方便后面扩展
    1: string udid,
    2: optional i32 uid_type = 0,
    3: optional i64 user_id = 0,
}

struct Req{
    1: User user,
    // 希望返回多少结果
    2: i32 num,
    // 已经关注的波波号列表
    3: list < User > exist_list,
    // 通过指定expose_filter, 可以实现连续多次请求的结果不重复。
    // 方便下游针对不同场景更灵活的控制
    4: optional bool expose_filter = true,
    5: optional string abtest_parameters,
    6: optional i32 channel_id = 0,
    // 用于区分不同请求，0是推荐页，频道页，1是关注后推荐相似用户
    7: optional i32 pos_id = 0,
    // 标取哪些用户的相似视频
    8: optional list < User > target_list,
}

enum RspStatus {
    OK,
    INVALID_USER,   // udid不合法，目前只是判断长度是否合理; 或者user_id为负数
    INVALID_PARAM,  // 参数不合法，如num为负数或0
    SHORT_RESULT,   // 返回结果不足Req.num个。但是大于0, 具体多少个可以通过Creater_list.size判断
    NO_RESULT,      // 返回结果为空
}
struct Rsp{
    1: list< User > Creater_list,
    2: optional RspStatus status = RspStatus.OK,
}

service Follow{
    Rsp get(1:Req req),
    list<Rsp> gets(1:list<Req> reqs),
}

service FollowChecker {
    i32 get(1:User user),
}

