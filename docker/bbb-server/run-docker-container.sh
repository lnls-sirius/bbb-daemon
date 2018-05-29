#!/bin/sh
docker run -d  -p 6789:6789 -p 9876:9876 --name bbb-serv-cont lnlscon/bbb-daemon-container:latest

