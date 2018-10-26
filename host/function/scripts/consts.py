#!/usr/bin/python
from os import environ

DAEMON_BASE = environ.get('DAEMON_BASE', '/root/bbb-daemon')
FILE_FOLDER = DAEMON_BASE + '/host/function/scripts/'

DEVICE_JSON = environ.get('DEVICE_JSON', '/opt/device.json')

PRU_POWER_SUPPLY = environ.get('PRU_POWER_SUPPLY')
COUNTING_PRU = environ.get('COUNTING_PRU')
SERIAL_THERMO = environ.get('SERIAL_THERMO')
MBTEMP = environ.get('MBTEMP')
AGILENT4UHV = environ.get('AGILENT4UHV')
MKS937B = environ.get('MKS937B')
SPIXCONV = environ.get('SPIXCONV')
NOTTY = environ.get('NOTTY')

TIMEOUT = .1
PORT = '/dev/ttyUSB0'
