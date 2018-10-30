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
<<<<<<< HEAD
=======
	# The comparison is based on the following environment variables. Do not use spaces !
	export PRU_POWER_SUPPLY='PRU_POWER_SUPPLY'
	export COUNTING_PRU='COUNTING_PRU'
	export SERIAL_THERMO='SERIAL_THERMO'
	export MBTEMP='MBTEMP'
	export AGILENT4UHV='AGILENT4UHV'
	export MKS937B='MKS937B'
	export SPIXCONV='SPIXCONV'
	export NOTTY='NOTTY'


>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2
    # Run identification script, repeats until a device is found
    echo "Running identification script, repeats until a device is found."
    ./whoami.py

    # Prepare board to its application
	CONN_DEVICE=$(awk NR==1 res)
	BAUDRATE=$(awk NR==1 baudrate)

	if [[ ${CONN_DEVICE} = "${SPIXCONV}" ]]; then
        startup_blinkingLED
<<<<<<< HEAD
        spixconv

	elif [[ ${CONN_DEVICE} = "${PRU_POWER_SUPPLY}" ]]; then
        startup_blinkingLED
        pru_power_supply
=======
        startup_success

	elif [[ ${CONN_DEVICE} = "${PRU_POWER_SUPPLY}" ]]; then
		echo Rs-485 and PRU switches are on. Assuming PRU Power Supply.
        echo Synchronizing pru-serial485 and ponte-py files.
        pushd ${DAEMON_BASE}/host/rsync
            ./rsync_beaglebone.sh pru-serial485
            ./rsync_beaglebone.sh ponte-py
        popd
        overlay_PRUserial485
        # @todo
        # - Rodar IOC FAC e Ponte.py
        startup_blinkingLED
        startup_success
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2

	elif [[ ${CONN_DEVICE} = "${COUNTING_PRU}" ]]; then
        startup_blinkingLED
<<<<<<< HEAD
        counting_pru
=======
        startup_success
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2

	elif [[ ${CONN_DEVICE} = "${SERIAL_THERMO}" ]]; then
        startup_blinkingLED
<<<<<<< HEAD
        serial_thermo
        
=======
        startup_success

>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2
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
<<<<<<< HEAD

startup_loop
=======
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2
