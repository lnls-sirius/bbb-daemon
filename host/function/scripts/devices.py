#!/usr/bin/python
from os import environ, path
from serial import Serial, STOPBITS_TWO, SEVENBITS, PARITY_EVEN

import Adafruit_BBIO.GPIO as GPIO
from PRUserial485 import PRUserial485_address

from persist import persist_info
from consts import *
from common.entity.entities import Type


def counter_pru():
    """
    Counter PRU
    """
    if PRUserial485_address() != 21 and not path.isfile(PORT):
        persist_info(Type.COUNTER_PRU, 115200, PRU_CONTADORA)


def no_tty():
    """
    NO /dev/tttyUSB0
    """
    if not path.exists(PORT) and PRUserial485_address() == 21:
        persist_info(Type.UNDEFINED, 115200, NOTTY)


def power_suppply_pru():
    """
    PRU Power Supply 
    """
    GPIO.setup("P8_11", GPIO.IN)
    GPIO.setup("P8_12", GPIO.IN)

    if GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 1:
        persist_info(Type.POWER_SUPPLY, 115200, PRU_FONTES)


def thermoIncluirChecksum(entrada):
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = soma % 256
    return (entrada + "{0:02X}".format(soma) + "\x03")


def thermo_probe():
    """
    Thermo probes
    """
    baud = 19200
    ser = Serial(port=PORT,
                 baudrate=baud,
                 bytesize=SEVENBITS,
                 parity=PARITY_EVEN,
                 stopbits=STOPBITS_TWO,
                 timeout=TIMEOUT)
    msg = thermoIncluirChecksum("\x07" + "01RM1")
    ser.write(msg.encode('utf-8'))
    res = ser.read(50)

    if len(res) != 0:
        persist_info(Type.SERIAL_THERMO, baud, SERIAL_THERMO)


def mbtempChecksum(entrada):
    print('{}'.format(entrada))
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = 256 - soma % 256
    return "0x%x" % soma


def mbtemp():
    """
    MBTemp
    """
    baud = 115200
    ser = Serial(PORT, baud, timeout=TIMEOUT)
    try:
        mbt_addr = 0
        for msg in MBTEMP_CONSTS:
            mbt_addr += 1
            ser.write(msg)
            res = ser.read()
            if len(res) != 0:
                persist_info(Type.MBTEMP, baud, MBTEMP, 'MBTemp Addr {}'.format(mbt_addr))
    except Exception as e:
        print('{}'.format(e))
    ser.close()


def mks9376b():
    baud = 115200
    ser = Serial(port=PORT, baudrate=baud, timeout=TIMEOUT)
    for i in range(1, 254):
        try:
            msgm = '\@{0:03d}'.format(i) + "PR1?;FF"
            ser.write(msgm)
            res = ser.read()
            if len(res) != 0:
                persist_info(Type.MKS937B, baud, MKS937B, 'First MKS937b at addr {}'.format(i))
        except Exception as e:
            print('{}'.format(e))
    ser.close()


def agilent4uhv():
    """
    AGILENT 4UHV
    """
    pass


def spixcon():
    """
    SPIxCON
    """
    pass
