    #!/bin/bash
# -*- coding: utf-8 -*-
source ${DAEMON_BASE}/host/function/scripts/functions.sh
source ${DAEMON_BASE}/host/function/envs.sh

pushd ${DAEMON_BASE}/host/function/scripts

	function cleanup {
            # Reset the detected device
            resetDeviceJson

			if [ -f res ]; then
					rm -rf res
			fi

			if [ -f baudrate ]; then
				rm -rf baudrate
			fi

            resetDeviceJson
	}

	trap cleanup EXIT
	cleanup
    
    # Synchronize common files and folders (startup scripts, bbb-daemon, rsync script, etc)
    synchronize_common
    
    # Run HardReset script, which is available at all boards
    startup_HardReset

	# The whoami.py script will save in a temporary file which device is connected
    # Run identification script, repeats until a device is found
    echo "Running identification script, repeats until a device is found."
    ./whoami.py

    # Prepare board to its application
	CONN_DEVICE=$(awk NR==1 res)
	BAUDRATE=$(awk NR==1 baudrate)

	if [[ ${CONN_DEVICE} = "${SPIXCONV}" ]]; then
        startup_blinkingLED
        spixconv

	elif [[ ${CONN_DEVICE} = "${PRU_POWER_SUPPLY}" ]]; then
        startup_blinkingLED
        pru_power_supply

	elif [[ ${CONN_DEVICE} = "${COUNTING_PRU}" ]]; then
        startup_blinkingLED
        counting_pru

	elif [[ ${CONN_DEVICE} = "${SERIAL_THERMO}" ]]; then
        startup_blinkingLED
        serial_thermo
        
	elif [ ! -z ${CONN_DEVICE} ] && { [ ${CONN_DEVICE} == "${MBTEMP}" ] || [ $CONN_DEVICE == "${AGILENT4UHV}" ] || [ $CONN_DEVICE == "${MKS937}" ]; }; then
        startup_blinkingLED
        socat_devices
	else
        if [[ ${CONN_DEVICE} = "${NOTTY}" ]]; then
		    echo No matching device has been found. ttyUSB0 is disconnected.
        else
		    echo  Unknown device. Nothing has been done.
        fi
        exit 1
    fi
popd

startup_loop
