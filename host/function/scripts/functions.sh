#!/bin/bash
# -*- coding: utf-8 -*-

function synchronize_common {
    # Synchronize common files and folders (startup scripts, bbb-daemon, rsync script, etc)
    pushd ${DAEMON_BASE}/host/rsync
        echo "Synchronizing startup scripts"
        ./rsync_beaglebone.sh startup-scripts
    popd
}

function startup_loop {
    echo "Starting infinite loop ..."
    while [ true ]; do
		sleep 2
	done
}

function resetDeviceJson {
    pushd ${DAEMON_BASE}/host/function/scripts/
        ./whoami.py reset
        cat /opt/device.json
    popd
}

function overlay_PRUserial485 {
    echo Initializing PRUserial485 overlay.

    if [ ! -d /root/pru-serial485 ]; then
        echo "ERROR! The folder /root/pru-serial485 doesn\'t exist."
        exit 1
    fi

    if [ ! -f /root/pru-serial485/src/overlay.sh ]; then
        echo "ERROR! The file /root/pru-serial485/src/overlay.sh doesn\'t exist."
        exit 1
    fi

    pushd /root/pru-serial485/src
        ./overlay.sh
    popd
}

function overlay_CountingPRU {
    echo Initializing CountingPRU overlay.

    if [ ! -d /root/counting-pru ]; then
        echo "ERROR! The folder /root/counting-pru doesn\'t exist."
        exit 1
    fi

    if [ ! -f /root/counting-pru/src/DTO_CountingPRU.sh ]; then
        echo "ERROR! The file /root/counting-pru/src/DTO_CountingPRU.sh doesn\'t exist."
        exit 1
    fi

    pushd /root/counting-pru/src
        ./DTO_CountingPRU.sh
    popd
}

function overlay_SPIxCONV {
    echo "Initializing SPIxCONV overlay."

    if [ ! -d /root/SPIxCONV ]; then
        echo "ERROR! The folder /root/SPIxCONV doesn\'t exist."
        exit 1
    fi

    if [ ! -f /root/SPIxCONV/init/SPIxCONV_config-pin.sh ]; then
        echo "ERROR! The file /root/SPIxCONV/init/SPIxCONV_config-pin.sh doesn\'t exist."
        exit 1
    fi

    pushd /root/SPIxCONV/init
    	./SPIxCONV_config-pin.sh
    popd
}

function counting_pru {
    echo "PRUserial485 address != 21 and ttyUSB0 is disconnected. Assuming CountingPRU."
    echo "Synchronizing counting-pru files"

    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh counting-pru
    popd

    overlay_CountingPRU

    echo "Initializing CountingPRU ..."

    if [ ! -d /root/counting-pru ]; then
        echo "ERROR! The folder /root/counting-pru doesn\'t exist."
        exit 1
    fi

    if [ ! -f /root/counting-pru/IOC/SI-CountingPRU_Socket.py ]; then
        echo "ERROR! The file /root/counting-pru/IOC/SI-CountingPRU_Socket.py doesn\'t exist."
        exit 1
    fi

    pushd /root/counting-pru/IOC
        ./SI-CountingPRU_Socket.py
        echo "SI-CountingPRU_Socket.py Terminated !"
    popd
}

function startup_blinkingLED {
    if pgrep "HeartBeat" >/dev/null 2>&1
    then
        echo "HeartBeat Running ..."
    else
        echo "Startup LED blinking..."

        if [ ! -d /root/startup-scripts ]; then
            echo "ERROR! The folder /root/startup-scripts doesn\'t exist."
            exit 1
        fi

        if [ ! -f /root/startup-scripts/HeartBeat.py ]; then
            echo "ERROR! The file /root/startup-scripts/HeartBeat.py doesn\'t exist."
            exit 1
        fi

        pushd /root/startup-scripts
        ./HeartBeat.py &
        popd
    fi
}

function startup_HardReset {
    if pgrep "HardReset" >/dev/null 2>&1
    then
        echo "HardReset Running ..."
    else
        echo "Startup HardReset..."

        if [ ! -d /root/startup-scripts ]; then
            echo "ERROR! The folder /root/startup-scripts doesn\'t exist."
            exit 1
        fi

        if [ ! -f /root/startup-scripts/HardReset.py ]; then
            echo "ERROR! The file /root/startup-scripts/HardReset.py doesn\'t exist."
            exit 1
        fi

        pushd /root/startup-scripts
        ./HardReset.py &
        popd
    fi
}

function spixconv {
    # :1 address:
    echo SPIXCONV detected.
    echo Synchronizing pru-serial485 and spixconv files
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
        ./rsync_beaglebone.sh spixconv
    popd
    overlay_PRUserial485
    overlay_SPIxCONV

    cd /root/SPIxCONV/software/scripts
    ./spixconv_unix_socket.py ${1} --tcp
}

function pru_power_supply {
    echo Rs-485 and PRU switches are on. Assuming PRU Power Supply.
    echo Synchronizing pru-serial485 and ponte-py files.
    pushd ${DAEMON_BASE}/host/rsync
        # Base files: PRU library and ethernet/serial bridge
        ./rsync_beaglebone.sh pru-serial485
        ./rsync_beaglebone.sh ponte-py
        # FAC IOC files and constants
        ./rsync_beaglebone.sh mathphys
        ./rsync_beaglebone.sh dev-packages
        ./rsync_beaglebone.sh machine-applications
        sed -i -e '/sirius/d' /etc/hosts
        sed -i -e '$a\'"#"' sirius-consts server alias' -e '$a\10.128.1.225 sirius-consts.lnls.br' /etc/hosts
    popd
    overlay_PRUserial485
    echo Running Ponte-py at port 4000
    pushd /root/ponte-py
        python-sirius Ponte.py &
    popd
    
    echo Running FAC PS IOC
    if [ ! -d "/root/sirius-ioc-as-ps" ]; then
        mkdir -p /root/sirius-ioc-as-ps
    fi
    DATE=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
#    sirius-ioc-as-ps.py --hostname >> /root/sirius-ioc-as-ps/$DATE.log 2>&1 &
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
    # - Rodar IOC e scripts python
}

function mks {
    echo Synchronizing pru-serial485 files
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
    popd
    overlay_PRUserial485

    ${DAEMON_BASE}/host/function/scripts/tcpSerial.py -serb 1024 -t 0.1
}

function socat_devices {
    echo Synchronizing pru-serial485 files
    pushd ${DAEMON_BASE}/host/rsync
        ./rsync_beaglebone.sh pru-serial485
    popd
    overlay_PRUserial485

    echo  "Starting socat with: socat TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR} FILE:${SOCAT_DEVICE},b${BAUDRATE},rawer"
    socat TCP-LISTEN:${SOCAT_PORT},reuseaddr,fork,nodelay,range=${SERVER_IP_ADDR} FILE:${SOCAT_DEVICE},b${BAUDRATE},rawer
}
