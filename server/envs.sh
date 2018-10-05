#!/bin/bash
export FLASK_PORT=4850
export PYTHONPATH=$(dirname $PWD)

export REDIS_SERVER_IP="0.0.0.0"
export REDIS_SERVER_PORT="6379"

export LC_ALL=en_US.UTF-8
export LC_LANG=en_US.UTF-8
export LANG=en_US.UTF-8