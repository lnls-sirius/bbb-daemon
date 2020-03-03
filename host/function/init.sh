#!/bin/bash
# -*- coding: utf-8 -*-
source ${DAEMON_BASE}/host/function/scripts/functions.sh
source ${DAEMON_BASE}/host/function/envs.sh

pushd ${DAEMON_BASE}/host/function/scripts

    function cleanup {
        # Reset the detected device
        resetDeviceJson

        if [ -f ${RES_FILE} ]; then
                rm -rf ${RES_FILE}
        fi

        if [ -f ${BAUDRATE_FILE} ]; then
            rm -rf ${BAUDRATE_FILE}
        fi

        python-sirius -c 'from common.database.redisbbb import RedisDatabase;RedisDatabase("localhost").disable_external_connections()'
    }

    trap cleanup EXIT
    cleanup

    # Apply overlay for SERIALxxCON
    overlay_PRUserial485

    # Synchronize common files and folders (startup scripts, bbb-daemon, rsync script, etc)
    synchronize_common

    # Run HardReset script, which is available at all boards
    startup_HardReset

    # Get Board address
    BOARD_ADDRESS=$(python-sirius -c 'from PRUserial485 import PRUserial485_address;print("{}".format(PRUserial485_address()))')


    # Address 0: COUNTING_PRU
    if [ $BOARD_ADDRESS -eq 0 ]
    then
        echo "BOARD 0"
        # COUNTING_PRU BOARD. NOT TREATED AT THIS MOMENT
        echo "Running identification script, repeats until a device is found."
        ./whoami.py
    fi

    # Address 21: MASTER BOARD
    if [ $BOARD_ADDRESS -eq 21 ]
    then
        echo "BOARD 21"
        ./master_initialization.py

        if [ ! -f ${RES_FILE} ]
        then
            echo "Running identification script, repeats until a device is found."
            ./whoami.py
        fi
    fi

    # Address 25: SLAVE BOARD
    if [ $BOARD_ADDRESS -eq 17 ]
    then
        echo "BOARD 17"
        ./slave_initialization.py
    fi








    while [ ! -f ${RES_FILE} ]; do sleep 1; done
    while [ ! -f ${BAUDRATE_FILE} ]; do sleep 1; done

    # Prepare board to its application
    CONN_DEVICE=$(awk NR==1 ${RES_FILE})
    BAUDRATE=$(awk NR==1 ${BAUDRATE_FILE})


    if [[ ${CONN_DEVICE} = "${SPIXCONV}" ]]; then
        # Using variable BAUDRATE to store the board address
        startup_blinkingLED
        spixconv ${BAUDRATE}

    elif [[ ${CONN_DEVICE} = "${PRU_POWER_SUPPLY}" ]]; then
        startup_blinkingLED
        pru_power_supply

    elif [[ ${CONN_DEVICE} = "${COUNTING_PRU}" ]]; then
        startup_blinkingLED
        counting_pru

    elif [[ ${CONN_DEVICE} = "${SERIAL_THERMO}" ]]; then
        startup_blinkingLED
        serial_thermo

    elif [[ ${CONN_DEVICE} = "${MKS937B}" ]]; then
        startup_blinkingLED
        mks

    elif [[ ${CONN_DEVICE} = "${AGILENT4UHV}" ]]; then
        startup_blinkingLED
        uhv

    elif [[ ${CONN_DEVICE} = "${MBTEMP}" ]]; then
        startup_blinkingLED
        mbtemp

    elif [ ! -z ${CONN_DEVICE} ]; then
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

    # Address 21: MASTER BOARD
    if [ $BOARD_ADDRESS -eq 21 ]
    then
        ./master_monitoring.py

    fi

    # Address 25: SLAVE BOARD
    if [ $BOARD_ADDRESS -eq 17 ]
    then
        ./slave_monitoring.py
    fi

popd
