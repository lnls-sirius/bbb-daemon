#!/bin/sh

docker run -d \
-p 6789:6789 -p 9876:9876 -p 1026:1026 -p 4850:4850 -p 9877:9877/tcp \
-e REDIS_SERVER_IP=0.0.0.0 \
-e REDIS_SERVER_PORT=6379 \
-e BBB_UDP=9876 \
-e BBB_TCP=9877 \
-e COM_INTERFACE_TCP=6789 \
-e WORKERS_NUM=10 \
-e FLASK_PORT=4850 \
-e FTP_PORT=1026 \
-e FTP_HOME='/root/bbb-daemon/types_repository/' \
--name bbb-serv-cont lnlscon/bbb-daemon-container:latest
