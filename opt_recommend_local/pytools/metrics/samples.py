# -*- coding: utf-8 -*-

import atometrics

# 初始化, 传入配置文件地址
atometrics.init("atometrics.conf")

# 所有的metrics需要新建才能使用
atometrics.newCounter("reqcount")
atometrics.newGauge("cpusage")
atometrics.newTimer("latency")
atometrics.newTimer("latency2")

# tags需要预先定义其可选值列表
atometrics.newTag("host", ["127.0.0.1", "10.10.11.30"])

# Timer用法1
with atometrics.Timer('latency2', tags={"host":"127.0.0.1"}):
    x = "test timer"

# Timer用法2
@atometrics.timing('latency', None, {"host":"127.0.0.1"})
def sampleFunc():
    a = ""
    b = 1

# 实际投递tsdb
atometrics.counterMark("reqcount", 20, None, {"host":"127.0.0.1"})
atometrics.gaugeMark("cpusage", 90, None, {"host":"127.0.0.1"})
sampleFunc()
