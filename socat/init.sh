#!/bin/bash
# -*- coding: utf-8 -*-

CODE="89719862km6a324098716459827364see598asdf723"

export SOCAT_PORT=4161
export SERVER_IP_ADDR=10.0.6.51
export SERVER_MASK=255.255.255.0
export BAUDRATE=115200
export DEVICE=/dev/ttyUSB0

RE=$( ./whoami.py ${CODE} | grep PRU_FONTES)
if [[ ! ${RE} =~ "PRU_FONTES${COD}"|"SERIAL_THERMO${COD}" ]];then
	# Bind using TCP
	socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR}:${SERVER_MASK} FILE:${DEVICE},b${BAUDRATE},rawer
else
	echo  Socat not started. Rs-485 and PRU switches are on.
fi
