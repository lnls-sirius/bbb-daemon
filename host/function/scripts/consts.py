#!/usr/bin/python
from os import environ

PRU_FONTES = environ.get('PRU_FONTES')
PRU_CONTADORA = environ.get('PRU_CONTADORA')
SERIAL_THERMO = environ.get('SERIAL_THERMO')
MBTEMP = environ.get('MBTEMP')
AGILENT4UHV = environ.get('AGILENT4UHV')
MKS937B = environ.get('MKS937B')
SPIXCON = environ.get('SPIXCON')
NOTTY = environ.get('NOTTY')

TIMEOUT = .1
PORT = '/dev/ttyUSB0'
