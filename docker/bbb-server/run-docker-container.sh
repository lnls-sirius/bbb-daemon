#!/bin/sh

docker run -d \
    -p 6789:6789 \
    -p 9876:9876 \
    -p 1026:1026 \
    -p 20:20 \
    -p 21:21 \
    -p 4850:4850 \
    -p 3000-3010:3000-3010 \
    -p 9877:9877/tcp \
    -e REDIS_SERVER_IP=10.0.6.70 \
    -e REDIS_SERVER_PORT=6379 \
    -e BBB_UDP=9876 \
    -e BBB_TCP=9877 \
    -e COM_INTERFACE_TCP=6789 \
    -e WORKERS_NUM=10 \
    -e FLASK_PORT=4850 \
    -e FTP_PORT=21 \
    -e FTP_HOME='/root/bbb-daemon/types_repository/' \
    -v /root/bbb_daemon_ftp:/root/bbb-daemon/types_repository/ \
    --name bbb-serv-cont lnlscon/bbb-daemon-container:latest
