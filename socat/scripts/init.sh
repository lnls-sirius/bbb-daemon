#!/bin/bash
# -*- coding: utf-8 -*-
function cleanup {      
        if [ -f res ]; then
                rm -rf res
        fi

		if [ -f baudrate ]; then
			rm -rf baudrate
		fi
}
trap cleanup EXIT
cleanup

export PRU_FONTES=$(echo -n PRU_FONTES | md5sum | awk '{ print $1 }')
export PRU_CONTADORA=$(echo -n PRU_CONTADORA | md5sum | awk '{ print $1 }')
export SERIAL_THERMO=$(echo -n SERIAL_THERMO | md5sum | awk '{ print $1 }')
export MBTEMP=$(echo -n MBTEMP | md5sum | awk '{ print $1 }')
export AGILENT4UHV=$(echo -n AGILENT4UHV | md5sum | awk '{ print $1 }')
export MKS937B=$(echo -n MKS937B | md5sum | awk '{ print $1 }')
export NOTTY=$(echo -n NOTTY | md5sum | awk '{ print $1 }')

export SOCAT_PORT=4161
export SERVER_IP_ADDR=10.0.6.51
export SERVER_MASK=255.255.255.0
export DEVICE=/dev/ttyUSB0

./whoami.py 
RE=$(awk NR==1 res) 
BAUDRATE=$(awk NR==1 baudrate)

if [[ ${RE} = "${PRU_FONTES}" ]]; then
	echo  Socat not started. Rs-485 and PRU switches are on.
	# @todo: Overlay Placa serial
	exit 1
fi

if [[ ${RE} = "${PRU_CONTADORA}" ]]; then
	# todo: Overlay e Lançar  SI-CountingPRU_Socket.py 
	echo  Socat not started. No ttyUSB0 detected and PRUserial485_address isn\'t 21.
	exit 1
fi

if [[ ${RE} = "${SERIAL_THERMO}" ]]; then
	# @todo: Overlay Placa serial
	echo  Socat not started. Serial Thermo probe detected.
	exit 1
fi

if [[ ${RE} = "${NOTTY}" ]]; then
	echo  Socat not started. No ttyUSB0 has been found.
	exit 1
fi

if [[ ${RE} =~ "${MBTEMP}"|"${AGILENT4UHV}"|"${MKS937}" ]]; then
	# Bind using socat 
	# @todo: Overlay Placa serial
	echo  Starting socat with ${BAUDRATE} baudrate on port ${SOCAT_PORT} and range=${SERVER_IP_ADDR}:${SERVER_MASK}.
	socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR}:${SERVER_MASK} FILE:${DEVICE},b${BAUDRATE},rawer
else
	echo  Socat not started. Nothig has been found. Will try again later. 
	exit 1
fi
