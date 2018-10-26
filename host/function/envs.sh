#!/bin/bash
#@todo: Those environment variables are for debugging purposes. They are meant to be set in a more elegant and flexible way.

# Socat Welcome Port
export SOCAT_PORT=4161

# Wich ip/mask that are allowed to connect to socat. It's not important and can be removed if necessary (make sure to edit the init.sh if you choose so).
export SERVER_IP_ADDR=10.0.6.51
export SERVER_MASK=255.255.255.0

# Serial port name to be used
export DEVICE=/dev/ttyUSB0
export PING_CANDIDATES="10.0.6.44 10.0.6.48 10.0.6.51"