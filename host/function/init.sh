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

    # Synchronize common files and folders (startup scripts, bbb-daemon, rsync script, etc)
    pushd ../../rsync
        echo Synchronizing startup scripts
        ./rsync_beaglebone.sh startup-scripts
    popd

    # Run HardReset script, which is available at all boards
    startup_HardReset

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

    # Run identification script, repeats until a device is found
    while { [ ! -f res ] && [ ! -f baudrate ]; }; do
        ./whoami.py
        sleep 1
    done


    # Prepare board to its application
	CONN_DEVICE=$(awk NR==1 res)
	BAUDRATE=$(awk NR==1 baudrate)

	if [[ ${CONN_DEVICE} = "${NOTTY}" ]]; then
		echo No matching device has been found. ttyUSB0 is disconnected.
		exit 1

	elif [[ ${CONN_DEVICE} = "${SPIXCONV}" ]]; then
		echo SPIXCONV detected.
        echo Synchronizing pru-serial485 and spixconv files
        pushd ../../rsync
            ./rsync_beaglebone.sh pru-serial485
            ./rsync_beaglebone.sh spixconv
        popd
        overlay_PRUserial485
		overlay_SPIxCONV
        # @todo
        # - Rodar aplicação SPIxCONV
        startup_blinkingLED

	elif [[ ${CONN_DEVICE} = "${PRU_POWER_SUPPLY}" ]]; then
		echo Rs-485 and PRU switches are on. Assuming PRU Power Supply.
        echo Synchronizing pru-serial485 and ponte-py files
        pushd ../../rsync
            ./rsync_beaglebone.sh pru-serial485
            ./rsync_beaglebone.sh ponte-py
        popd
		overlay_PRUserial485
		# @todo
        # - Rodar IOC FAC e Ponte.py
        startup_blinkingLED
		exit 1

	elif [[ ${CONN_DEVICE} = "${COUNTING_PRU}" ]]; then
		echo  PRUserial485 address != 21 and ttyUSB0 is disconnected. Assuming CountingPRU.
        echo Synchronizing counting-pru files
        pushd ../../rsync
            ./rsync_beaglebone.sh counting-pru
        popd
		overlay_CountingPRU
        # @todo
        # - Rodar Socket da Contadora
        counting_pru
        startup_blinkingLED

	elif [[ ${CONN_DEVICE} = "${SERIAL_THERMO}" ]]; then
		echo  Serial Thermo probe detected.
        echo Synchronizing pru-serial485 and serial-thermo files
        pushd ../../rsync
            ./rsync_beaglebone.sh pru-serial485
            ./rsync_beaglebone.sh serial-thermo
        popd
		overlay_PRUserial485
        # @todo
        # - Rodar IOC
        startup_blinkingLED

	elif [ ! -z ${CONN_DEVICE} ] && { [ ${CONN_DEVICE} == "${MBTEMP}" ] || [ $CONN_DEVICE == "${AGILENT4UHV}" ] || [ $CONN_DEVICE == "${MKS937}" ]; }; then
        echo Synchronizing pru-serial485 files
        pushd ../../rsync
            ./rsync_beaglebone.sh pru-serial485
        popd
		overlay_PRUserial485
        startup_blinkingLED
		echo  Starting socat with ${BAUDRATE} baudrate on port ${SOCAT_PORT} and range=${SERVER_IP_ADDR}:${SERVER_MASK}.
		socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR}:${SERVER_MASK} FILE:${CONN_DEVICE},b${BAUDRATE},rawer
	else
		echo  Unknown device. Nothing has been done.
		exit 1
	fi
popd
