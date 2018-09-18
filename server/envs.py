#!/usr/bin/python3
from os import environ

REDIS_SERVER_IP = environ.get('REDIS_SERVER_IP', '0.0.0.0')
REDIS_SERVER_PORT = int(environ.get('REDIS_SERVER_PORT', 6379))

BBB_UDP = int(environ.get('BBB_UDP', 9876))
BBB_TCP = int(environ.get('BBB_TCP', 9877))

COM_INTERFACE_TCP = int(environ.get('COM_INTERFACE_TCP', 6789))
WORKERS_NUM = int(environ.get('WORKERS_NUM', 10))
WEB_CLIENT_SERVER_PORT = int(environ.get('FLASK_PORT', 4850))
FTP_SERVER_PORT = int(environ.get('FTP_SERVER_PORT', 21))
FTP_HOME_DIR = environ.get(
    'FTP_HOME', '/root/bbb-daemon/types_repository/')

 