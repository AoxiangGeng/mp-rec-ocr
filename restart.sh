#!/usr/bin/env bash

ps -ef|grep ocr_server.py |grep -v 'grep'|awk '{print $2}'|xargs kill -9
pid=`netstat -pan |grep 10080|awk '{print $NF}'|awk -F"/" '{print $1}'`
kill -9 ${pid}
pid=`netstat -pan |grep 10080|awk '{print $NF}'|awk -F"/" '{print $1}'`
kill -9 ${pid}
sleep 1s
nohup python ocr_server.py 1> out 2>err &
