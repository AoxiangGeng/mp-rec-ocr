#!encoding=utf-8
import fcntl
import logging
import socket
import struct


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


# print get_ip_address('lo')

# server
host = ['127.0.0.1']
port = ['10080']

log_level = logging.ERROR
console_log_level = logging.ERROR
scribe_log_level = logging.ERROR
log_file = 'text_server.py.log'
log_category = '.'
localIP = get_ip_address('eth0')
print localIP

log_format = '%%(asctime)s %s %%(thread)d %%(levelname)-5s %%(message)s' % localIP
server_thread_num = 8
prometheus_port = 8080
debug = False

enable_debuginfo = False

user_feature_file="/root/service/als_data/user_feature"
content_feature_file="/root/service/als_data/content_feature"
