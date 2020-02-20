#!/bin/bash
#@todo: Those environment variables are for debugging purposes. They are meant to be set in a more elegant and flexible way.
# Socat Welcome Port
export SOCAT_PORT=4161
# Wich ip/mask that are allowed to connect to socat.
export SERVER_IP_ADDR="10.128.255.0/24"
# Serial port name to be used
export SOCAT_DEVICE="/dev/ttyUSB0"

# The whoami.py script will use the following environment variables.
# Do not use spaces!
export DEVICE_JSON="/opt/device.json"
export RES_FILE="/var/tmp/res"
export BAUDRATE_FILE="/var/tmp/baudrate"
export CONN_DEVICE="/dev/ttyUSB0"
export PRU_POWER_SUPPLY='PowerSupply'
export COUNTING_PRU='CountingPRU'
export SERIAL_THERMO='ThermoProbe'
export MBTEMP='MBTemp'
export AGILENT4UHV='Agilent4UHV'
export MKS937B='MKS937b'
export SPIXCONV='SPIxCONV'
export NOTTY='NOTTY'
