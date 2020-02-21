namespace java com.miaopai.ad.ssp.core.rpc.thrift.bo

struct MonitorInfo {
1:list<string> win_notice_url,
2:list<string> impression_tracking_url,
3:list<string> click_tracking_url,
4:list<string> close_tracking_url,
5:list<string> video_start_url,
6:list<string> video_full_screen_url,
7:list<string> video_end_url,
8:list<string> video_start_card_url,
9:list<string> app_download_url,
10:list<string> app_start_download_url,
11:list<string> app_install_url,
12:list<string> app_start_install_url,
13:list<string> app_active_url,
}

struct AdItem {
1: optional i64 creative_id,
2: i32 source,
3: optional string image_url,
4: optional string video_url,
5: optional i32 video_size,
6: optional i32 video_duration,
7: optional string landing_url,
8: optional string download_url,
9: optional string package_name,
10: optional i32 package_size,
11: optional string app_name,
12: optional string app_icon,
13: optional string app_version,
14: optional string creative_title,
15: optional string sponsor_name,
16: optional string sponsor_icon,
17: i32 creative_type,
18: i32 jump_type,
19: optional string schema_url,
20: optional string phone_number,
21: optional i32 start_time,
22: optional i32 end_time,
23: optional string logo_text,
24: optional string logo_icon,
25: optional MonitorInfo monitor_info,
26: optional i64 bid_price,
27: optional list<string> image_array,  #多图素材
28: optional string token,          # token
29: optional i32 ad_width,
30: optional i32 ad_height,
31: optional bool need_encrypt,   #是否需要加密
32: optional i32 protocol, #竞价协议 1-RTB 2-PDB
}

struct Req {
1: optional string os_name,
2: optional string os_version,
3: optional string androidId,
4: optional string imei,
5: optional string mac,
6: optional i32 dpi,
7: optional i32 pos_id,
8: optional i32 count,
9: optional string carrier,
10: optional string network,
11: optional string req_ip,
12: optional string user_agent,
13: optional i32 screen_width,
14: optional i32 screen_height,
15: optional string manufacturer,
16: optional string model,
17: optional string app_version, 
18: optional string area,
19: optional string device_brand,
20: list<i64> impr_ids,
21: optional i32 source,
22: optional double latitude,
23: optional double longitude,
24: optional i32 orientation,
25: optional i32 device_type,
26: optional string package_name,
27: optional i32 app_id,
28: optional i32 ad_width,
29: optional i32 ad_height,
30: optional i32 cpm,
31: optional i32 rom,
32: optional i32 ram,
33: optional string idfa,
34: optional string idfv,
35: optional string openudid,
36: optional string tk,
37: optional i32 platform,
}

struct Rsp {
1: i32 status,
2: string message,
3: list<AdItem> ads,
}



service AdThirdParty {
    Rsp get(1:Req req),
}
