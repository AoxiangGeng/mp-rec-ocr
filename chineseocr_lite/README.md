# 环境
- pytorch  1.2.0 
- python3
- linux

# PSENET 编译
``` Bash
！cd psenet/pse
！rm -rf pse.so 
！make 

# 依赖
sudo pip3 install -r requirements.txt

# 运行
修改主目录下model.py文件中的图片保存路径--work_path，然后运行 python3 model.py 即可打印出识别结果
及对应的文本框位置信息

#可能遇到的问题
--ImportError: libSM.so.6: cannot open shared object file
！sudo apt-get install -y libsm6 libxext6

--pse.so编译失败
可尝试将gcc升级至5.4.0以上版本