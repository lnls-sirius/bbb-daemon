#!/bin/bash
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
    echo Socat not started. No ttyUSB0 detected and PRUserial485_address isn\'t 21.
    echo Initializing Counter PRU ...

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
