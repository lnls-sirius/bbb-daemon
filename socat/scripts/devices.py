#!/usr/bin/python3
from os import environ
from serial import Serial, STOPBITS_TWO, SEVENBITS, PARITY_EVEN
import Adafruit_BBIO.GPIO as GPIO

from whoami import CODE, PORT, TIMEOUT
from persist import persist_info
 
# PRU unit
GPIO.setup("P8_11", GPIO.IN)
GPIO.setup("P8_12", GPIO.IN)
if GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 1:
    print('PRU_FONTES' + CODE)
    file = open('device.conf', 'w')
    file.writelines('PRU_FONTES\nPRU')
    file.close()
    exit()


# Thermo probes
def incluirChecksum(entrada):
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = soma % 256
    return(entrada + "{0:02X}".format(soma) + "\x03")

thermo_interface = Serial(port = "{}".format(PORT),
                                 baudrate = 19200,
                                 bytesize = SEVENBITS,
                                 parity = PARITY_EVEN,
                                 stopbits = STOPBITS_TWO,
                                 timeout = TIMEOUT
                                )
thermo = incluirChecksum("\x07" + "01RM1")
thermo_interface.write(thermo)
datathermo = thermo_interface.read(50)

if len(datathermo) != 0:
    persist_info('Thermo_Probe', 19200, 'SERIAL_THERMO' + CODE)

# MBTemp Checksum
def mbtempChecksum(entrada):
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = 256 - soma % 256
    return(entrada + "{0:02X}".format(soma))