#!/bin/bash
# -*- coding: utf-8 -*-

systemctl start sirius-bbb-ioc-ps.service

# if [ ! -d "/root/sirius-ioc-as-ps" ]; then
#     mkdir -p /root/sirius-ioc-as-ps
# fi
# DATE=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
# sirius-ioc-as-ps.py --hostname >> /root/sirius-ioc-as-ps/$DATE.log 2>&1 &
