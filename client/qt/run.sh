#!/bin/bash
 
PARENT_PATH=$(dirname $PWD)
export PYTHONPATH="$(dirname $PARENT_PATH)"
python3 monitor.py
