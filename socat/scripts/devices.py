#!/usr/bin/python
from os import environ, path
from serial import Serial, STOPBITS_TWO, SEVENBITS, PARITY_EVEN
# import Adafruit_BBIO.GPIO as GPIO
from persist import persist_info
# from PRUserial485 import PRUserial485_address
from consts import *


# Counter
# if PRUserial485_address() != 21 and not path.isfile(PORT):
    # persist_info('PRU_CONTADORA', '115200', PRU_CONTADORA )

if not path.exists(PORT):
    persist_info('NO_TTY_USB0', 115200, NOTTY )

# PRU unit
# GPIO.setup("P8_11", GPIO.IN)
# GPIO.setup("P8_12", GPIO.IN)

# if GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 1:
    # persist_info('PRU_FONTES', 'PRU', PRU_FONTES )

# Thermo probes
def incluirChecksum(entrada):
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = soma % 256
    return(entrada + "{0:02X}".format(soma) + "\x03")

# thermo_interface = Serial(port = "{}".format(PORT),
#                                  baudrate = 19200,
#                                  bytesize = SEVENBITS,
#                                  parity = PARITY_EVEN,
#                                  stopbits = STOPBITS_TWO,
#                                  timeout = TIMEOUT
#                                 )
# thermo = incluirChecksum("\x07" + "01RM1")
# thermo_interface.write(thermo.encode('utf-8'))
# datathermo = thermo_interface.read(50)

# if len(datathermo) != 0:
#     persist_info('Thermo_Probe', 19200, SERIAL_THERMO)

# MBTemp Checksum
def mbtempChecksum(entrada):
    print('{}'.format(entrada))
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = 256 - soma % 256
    return "0x%x"%soma
 
def mbtemp(cmd, ser):
    mbt_addr = 0
    for msg in MBTEMP_CONSTS:
        mbt_addr += 1
        ser.write(msg) 
        res = ser.read()
        if len(res) != 0: 
            persist_info(cmd.get('device'), cmd.get('baud'), MBTEMP, 'MBTemp Addr {}'.format(mbt_addr))
