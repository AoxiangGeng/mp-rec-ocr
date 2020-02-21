namespace cpp adbroker
namespace py adbroker

#pos_id定义
#pos_id = 0,波波开屏广告位
#pos_id = 1,波波feeds页广告位
#pos_id = 2,波波相关广告位
#pos_id = 3,活动广告位
#pos_id = 4,分享页面
struct Req
{
    1: i32 uid_type,                   # 登录类型，填14
    2: string uid,                     # udid
    3: i32 app_id = 0,                 # 1-波波 2-秒拍
    4: i32 pos_id = 0,                 # 广告位id
    5: i32 count = 1,                  # 请求广告数量
    6: string abtest_parameters = '',  # ab参数
    7: string abtest_ids = '',         # 多个abid
    8: i32 channel_id = 0,             # 频道id
    9: optional i64 user_id = 0,       # 登录用户id
    10:optional i32 refresh_time = 0,  # app启动后的刷新次数，从1开始
    11:string req_ip = "",             # 客户端请求ip
    12:string area = "",               # 地域信息
    13:string device_brand = "",       # 手机品牌
    14:string network = "",            # 设备网络
    15:string device_info = "",        # 设备信息  参考波波app公共字段，设备信息是定向必须的
    16:i32    video_num = 8,           # 视频数量
    17:i32 platform = 0,               # 平台 0 波波， 1看点
}

struct Rsp
{
    1: string status = '',
    2: list<string> ads,
}

service AdbrokerService
{
    Rsp get_ad_list(1:Req req),
}
