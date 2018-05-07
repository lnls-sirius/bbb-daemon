#!/bin/bash

export PYTHONPATH="$(dirname $PWD)"
# echo $PYTHONPATH
python3 daemon.py
