#!/bin/bash
#@todo: Those environment variables are for debugging purposes. They are meant to be set in a more elegant and flexible way.

# Socat Welcome Port
export SOCAT_PORT=4161
# Wich ip/mask that are allowed to connect to socat. It's not important and can be removed if necessary (make sure to edit the init.sh if you choose so).
export SERVER_IP_ADDR="10.128.255.5/16"
# Serial port name to be used
export SOCAT_DEVICE="/dev/ttyUSB0"

# The whoami.py script will use the following environment variables.
# Do not use spaces!
export CONN_DEVICE="/dev/ttyUSB0"
export PRU_POWER_SUPPLY='PRU_POWER_SUPPLY'
export COUNTING_PRU='COUNTING_PRU'
export SERIAL_THERMO='SERIAL_THERMO'
export MBTEMP='MBTEMP'
export AGILENT4UHV='AGILENT4UHV'
export MKS937B='MKS937B'
export SPIXCONV='SPIXCONV'
export NOTTY='NOTTY'
