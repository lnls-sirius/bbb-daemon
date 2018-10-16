#!/bin/bash
# -*- coding: utf-8 -*-
source scripts/functions.sh
source envs.sh

pushd scripts

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

	# The whoami.py script will save in a temporary file which device is connected
	# The comparison is based on the following environment variables. Do not use spaces !
	export PRU_POWER_SUPPLY='PRU_POWER_SUPPLY'
	export COUNTING_PRU='COUNTING_PRU'
	export SERIAL_THERMO='SERIAL_THERMO'
	export MBTEMP='MBTEMP'
	export AGILENT4UHV='AGILENT4UHV'
	export MKS937B='MKS937B'
	export SPIXCONV='SPIXCONV'
	export NOTTY='NOTTY'

	# Added the root folder to pythonpath in order to gain access to the commons/ scripts folder
	export PYTHONPATH=${PWD}/../../../

    # Synchronize common files and folders (startup scripts, bbb-daemon, rsync script, etc)
    # @todo
    # - Atualizar arquivos gerais

    # Run identification script
    ./whoami.py

    # Prepare board to its application
	CONN_DEVICE=$(awk NR==1 res)
	BAUDRATE=$(awk NR==1 baudrate)

	if [[ ${CONN_DEVICE} = "${NOTTY}" ]]; then
		echo No matching device has been found. ttyUSB0 is disconnected.
		exit 1
	fi

	if [[ ${CONN_DEVICE} = "${SPIXCONV}" ]]; then
		echo SPIXCONV detected.
        overlay_PRUserial485
		overlay_SPIxCONV
        # @todo
        # - Atualizar arquivos da SPIXCONV
        # - Rodar aplicação SPIxCONV
	fi

	if [[ ${CONN_DEVICE} = "${PRU_POWER_SUPPLY}" ]]; then
		echo Rs-485 and PRU switches are on. Assuming PRU Power Supply.
		overlay_PRUserial485
		# @todo
        # - Atualizar arquivos PRUserial485 e Ponte.py
        # - Rodar IOC FAC
		exit 1
	fi

	if [[ ${CONN_DEVICE} = "${COUNTING_PRU}" ]]; then
		echo  PRUserial485 address != 21 and ttyUSB0 is disconnected. Assuming PRU Counter.
		overlay_CountingPRU
        # @todo
        # - Atualizar arquivos da Contadora
        # - Rodar Socket da Contadora
        counting_pru
    fi

	if [[ ${CONN_DEVICE} = "${SERIAL_THERMO}" ]]; then
		echo  Serial Thermo probe detected.
		overlay_PRUserial485
        # @todo
        # - Atualizar arquivos da Sonda Thermo
        # - Rodar IOC
	fi

	if [ ! -z ${CONN_DEVICE} ] && { [ ${CONN_DEVICE} == "${MBTEMP}" ] || [ $CONN_DEVICE == "${AGILENT4UHV}" ] || [ $CONN_DEVICE == "${MKS937}" ]; }; then
		overlay_PRUserial485
		echo  Starting socat with ${BAUDRATE} baudrate on port ${SOCAT_PORT} and range=${SERVER_IP_ADDR}:${SERVER_MASK}.
		socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR}:${SERVER_MASK} FILE:${CONN_DEVICE},b${BAUDRATE},rawer
	else
		echo  Socat not started. Nothig has been found. Will try again later.
		exit 1
	fi
popd
