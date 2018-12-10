#!/bin/bash
docker run -v /storage/bbb-daemon:/data -p 6379:6379 --name bbb-redis -d redis redis-server --appendonly yes
