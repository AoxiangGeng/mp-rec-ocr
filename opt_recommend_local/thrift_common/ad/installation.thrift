#!/usr/local/bin/thrift --gen cpp  --gen py --gen go

namespace cpp installation
namespace py installation
namespace go installation

struct InstallationItem{
   1: string package_name,  # 包名
   2: string app_name,  # 应用名
   3: i32 typ, # 1为普通应用 2为系统应用
}

struct InstallationIDIten{
   1: i64 package_name,  # 包名
   2: i64 app_name,  # 应用名
   3: i32 typ, # 1为普通应用 2为系统应用
}

service Installation {
    // 写操作，true为成功
    bool put_installation(1: string udid, 
                            2: string fudid,
                            3: list<InstallationItem> iList)

    // 获取全量列表
    // 参数tpy获取对应的应用类型，0为获取全量
    list<InstallationItem> get_installation(1: string udid, 
                                            2: i32 typ)

    // 获取包名列表
    // 参数tpy获取对应的应用类型，0为获取全量
    list<string> get_installation_package_name(1: string udid,
                                            2: i32 typ)

    // 获取应用名列表
    // 参数tpy获取对应的应用类型，0为获取全量
    list<string> get_installation_app_name(1: string udid,
                                            2: i32 typ)

    // 获取全量列表
    // 参数tpy获取对应的应用类型，0为获取全量
    list<InstallationIDIten> get_installation_id(1: string udid, 
                                            2: i32 typ)

    // 获取包名列表
    // 参数tpy获取对应的应用类型，0为获取全量
    list<i64> get_installation_package_name_id(1: string udid,
                                            2: i32 typ)

    // 获取应用名列表
    // 参数tpy获取对应的应用类型，0为获取全量
    list<i64> get_installation_app_name_id(1: string udid,
                                            2: i32 typ)
}