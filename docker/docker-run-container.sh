#!/bin/sh
#docker run -d -p 6379:6379 -p 6789:6789 --name bbb-serv-cont lnlscon/bbb-daemon-container:bbb-server
docker run -d  -p 6789:6789 --name bbb-serv-cont lnlscon/bbb-daemon-container:bbb-server

