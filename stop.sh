#!/usr/bin/env bash

ps -ef|grep recall_als_server.py |grep -v 'grep'|awk '{print $2}'|xargs kill -9
pid=`netstat -pan |grep 10080|awk '{print $NF}'|awk -F"/" '{print $1}'`
kill -9 ${pid}
pid=`netstat -pan |grep 10080|awk '{print $NF}'|awk -F"/" '{print $1}'`
kill -9 ${pid}
