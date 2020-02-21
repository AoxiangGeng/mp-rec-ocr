namespace cpp antispam
namespace py antispam
namespace go antispam

//用户,和recommend User保持一致
struct User{
    1: string uid,
    2: i32 uid_type,
    3: optional i64 user_id=0,
}
//广告
struct AD{
   1: i32 campaign_id,  //广告计划id
   2: i32 creative_id,  //广告创意id
   3: optional i32 user_id, //广告主id
   4: optional i32 unit_id,  //广告单元id
}
//广告点击操作行为数据
struct Behavior {
    1: i32 click_duraiton,  //点击间隔时间
    2: i32 down_duration,   //点击按下时间间隔
    3: i32 up_duration,     //点击抬起时间间隔
    4: i32 down_pos_x,      //按下横坐标
    5: i32 down_pos_y,      //按下纵坐标
    6: i16 drag_flag,       //是否拖拽(0:无 1:有）
    7: i16 switch_flag,     //是否切换页面（0:无 1:有）
    8: i32 play_duration,   //播放时长，用户看到广告的总时长(毫秒）
    9: i32 display_width,   //广告实际展现长度(单位像素）
    10: i32 display_height, //广告实际展现高度(单位像素)
}

//广告操作数据
struct AdOperation{
    1:User user, //用户
    2:AD ad,  //广告信息
    3:i32 view_time, //曝光时间
    4:i32 click_time, //点击时间
    5:string view_ip,  //展示ip
    6:string click_ip, //点击ip
    7:optional i16 price_type, //计费类型
    8:optional Behavior behavior, //点击操作行为数据
}

//反作弊结果数据
struct AntiSpamResult{
    1:i16 status,  //0:反作弊不通过  1:反作弊正常通过
    2:optional i16 fraud_type, //作弊类型 1、ip黑白名单  2、同一uid扣费异常 3、其他待定
}

//反作弊检查请求参数
struct AntiSpamCheckReq{
    1:list<AdOperation> ad_operate_list,
}

//反作弊检查返回
struct AntiSpamCheckGetRsp{
    1:list<AntiSpamResult> antispam_result_list,
}

service AdAntiSpam {
      //反作弊检查
      AntiSpamCheckGetRsp get_antispam_check(1:AntiSpamCheckReq req),
}

