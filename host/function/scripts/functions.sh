#!/bin/bash
# -*- coding: utf-8 -*-
<<<<<<< HEAD
function synchronize_common {
    # Synchronize common files and folders (startup scripts, bbb-daemon, rsync script, etc)
    pushd ${DAEMON_BASE}/host/rsync
        echo Synchronizing startup scripts
        ./rsync_beaglebone.sh startup-scripts
    popd
}

function startup_loop {
    echo "Starting infinite loop ..."
    while [ true ]; do 
		sleep 2
	done
=======
function startup_success {
    while [[ true ]]; do
        sleep 2
        echo 'w8'
    done
    echo bye
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2
}

function resetDeviceJson {
    pushd ${DAEMON_BASE}/host/function/scripts/
        ./initial.py
        cat /opt/device.json
    popd
}

function overlay_PRUserial485 {
    echo Initializing PRUserial485 overlay.

    if [ ! -d /root/pru-serial485 ]; then
        echo ERROR! The folder /root/pru-serial485 doesn\'t exist.
        exit 1
    fi

    if [ ! -f /root/pru-serial485/src/overlay.sh ]; then
        echo ERROR! The file /root/pru-serial485/src/overlay.sh doesn\'t exist.
        exit 1
    fi

    pushd /root/pru-serial485/src
    ./overlay.sh
    popd
}

function overlay_CountingPRU {
    echo Initializing CountingPRU overlay.

    if [ ! -d /root/counting-pru ]; then
        echo ERROR! The folder /root/counting-pru doesn\'t exist.
        exit 1
    fi

    if [ ! -f /root/counting-pru/src/DTO_CountingPRU.sh ]; then
        echo ERROR! The file /root/counting-pru/src/DTO_CountingPRU.sh doesn\'t exist.
        exit 1
    fi

    pushd /root/counting-pru/src
    ./DTO_CountingPRU.sh
    popd
}

function overlay_SPIxCONV {
    echo Initializing SPIxCONV overlay.

    if [ ! -d /root/SPIxCONV ]; then
        echo ERROR! The folder /root/SPIxCONV doesn\'t exist.
        exit 1
    fi

    if [ ! -f /root/SPIxCONV/init/SPIxCONV_config-pin.sh ]; then
        echo ERROR! The file /root/SPIxCONV/init/SPIxCONV_config-pin.sh doesn\'t exist.
        exit 1
    fi

    pushd /root/SPIxCONV/init
    ./SPIxCONV_config-pin.sh
    popd
}

function counting_pru {
    echo  PRUserial485 address != 21 and ttyUSB0 is disconnected. Assuming CountingPRU.
    echo Synchronizing counting-pru files
    
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh counting-pru
    popd
    
    overlay_CountingPRU
    # @todo
    # - Rodar Socket da Contadora
    echo Socat not started. No ttyUSB0 detected and PRUserial485_address isn\'t 21.
    echo Initializing CountingPRU ...

    if [ ! -d /root/counting-pru ]; then
        echo ERROR! The folder /root/counting-pru doesn\'t exist.
        exit 1
    fi

    if [ ! -f /root/counting-pru/IOC/SI-CountingPRU_Socket.py ]; then
        echo ERROR! The file /root/counting-pru/IOC/SI-CountingPRU_Socket.py doesn\'t exist.
        exit 1
    fi

    pushd /root/counting-pru/IOC
        ./SI-CountingPRU_Socket.py
        echo SI-CountingPRU_Socket.py Terminated !
    popd
}

function startup_blinkingLED {
    echo Startup LED blinking...

    if [ ! -d /root/startup-scripts ]; then
        echo ERROR! The folder /root/startup-scripts doesn\'t exist.
        exit 1
    fi

    if [ ! -f /root/startup-scripts/HeartBeat.py ]; then
        echo ERROR! The file /root/startup-scripts/HeartBeat.py doesn\'t exist.
        exit 1
    fi

    pushd /root/startup-scripts
    ./HeartBeat.py &
    popd
}

function startup_HardReset {
    echo Startup HardReset...

    if [ ! -d /root/startup-scripts ]; then
        echo ERROR! The folder /root/startup-scripts doesn\'t exist.
        exit 1
    fi

    if [ ! -f /root/startup-scripts/HardReset.py ]; then
        echo ERROR! The file /root/startup-scripts/HardReset.py doesn\'t exist.
        exit 1
    fi

    pushd /root/startup-scripts
    ./HardReset.py &
    popd
}

function spixconv {
    echo SPIXCONV detected.
    echo Synchronizing pru-serial485 and spixconv files
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
        ./rsync_beaglebone.sh spixconv
    popd
    overlay_PRUserial485
    overlay_SPIxCONV
    # @todo
    # - Rodar aplicação SPIxCONV
}

function pru_power_supply {
    echo Rs-485 and PRU switches are on. Assuming PRU Power Supply.
    echo Synchronizing pru-serial485 and ponte-py files.
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
        ./rsync_beaglebone.sh ponte-py
    popd
    overlay_PRUserial485
    # @todo
    # - Rodar IOC FAC e Ponte.py
}

function serial_thermo {
    echo  Serial Thermo probe detected.
    echo Synchronizing pru-serial485 and serial-thermo files
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
        ./rsync_beaglebone.sh serial-thermo
    popd
    overlay_PRUserial485
    # @todo
    # - Rodar IOC 
}

function socat_devices {
    echo Synchronizing pru-serial485 files
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
    popd
    overlay_PRUserial485
    
    echo  Starting socat with ${BAUDRATE} baudrate on port ${SOCAT_PORT} and range=${SERVER_IP_ADDR}:${SERVER_MASK}.
    socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay FILE:${CONN_DEVICE},b${BAUDRATE},rawer
}