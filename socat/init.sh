#!/bin/bash
export COD='89716324098716459827364598723'

export SOCAT_PORT=4161
export SERVER_IP_ADDR=10.0.6.51
export SERVER_MASK=255.255.255.0
export BAUDRATE=115200
export DEVICE=/dev/ttyUSB0

RE=$( ./whoami.py | grep PRU_FONTES)
echo $RE
if [[ ${RE} =~ "PRU_FONTES${COD}" ]];then
    # Bind using TCP
    socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR}:${SERVER_MASK} FILE:${DEVICE},b${BAUDRATE},rawer
fi