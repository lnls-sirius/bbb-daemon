#!/usr/bin/python
import logging
import time
from os import environ, path
from serial import Serial, STOPBITS_TWO, SEVENBITS, PARITY_EVEN
import Adafruit_BBIO.GPIO as GPIO
from PRUserial485 import PRUserial485_address

from persist import persist_info
from consts import *
from common.entity.entities import Type

PIN_FTDI_PRU = "P8_11"      # 0: FTDI / 1: PRU
FTDI = 0
PRU = 1

PIN_RS232_RS485 = "P8_12"   # 0: RS232 / 1: RS485
RS232 = 0
RS485 = 1

GPIO.setup(PIN_FTDI_PRU, GPIO.IN)
GPIO.setup(PIN_RS232_RS485, GPIO.IN)

logger = logging.getLogger('Whoami')

def reset():
    """
    Reset device.json content.
    """
    persist_info(0, 0, 'RESET', 'Still trying to find out where i\'m connected...')

def counting_pru():
    """
    CountingPRU
    """
    logger.info('Counting PRU')
    if PRUserial485_address() != 21 and not path.isfile(PORT):
        persist_info(Type.COUNTING_PRU, 0, COUNTING_PRU)


def no_tty():
    """
    NO /dev/ttyUSB0
    """
    logger.info('No /dev/ttyUSB0')
    if not path.exists(PORT) and PRUserial485_address() == 21:
        persist_info(Type.UNDEFINED, 115200, NOTTY)


def power_supply_pru():
    """
    PRU Power Supply
    """
    logger.info('PRU Power Supply')
    if GPIO.input(PIN_FTDI_PRU) == PRU and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        persist_info(Type.POWER_SUPPLY, 6000000, PRU_POWER_SUPPLY)


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
    logger.info('Thermo probes')
    if GPIO.input(PIN_FTDI_PRU) == FTDI and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        baud = 19200
        ser = Serial(port=PORT,
                     baudrate=baud,
                     bytesize=SEVENBITS,
                     parity=PARITY_EVEN,
                     stopbits=STOPBITS_TWO,
                     timeout=TIMEOUT)
        msg = thermoIncluirChecksum("\x07" + "01RM1")
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(msg.encode('utf-8'))
        res = ser.read(50)

        if len(res) != 0:
            persist_info(Type.SERIAL_THERMO, baud, SERIAL_THERMO)


def MBTempChecksum(string):
    counter = 0
    i = 0
    while (i < len(string)):
        counter += ord(string[i])
        i += 1
    counter = (counter & 0xFF)
    counter = (256 - counter) & 0xFF
    return(string + chr(counter))


def mbtemp():
    """
    MBTemp
    """
    logger.info('MBTemp')
    if GPIO.input(PIN_FTDI_PRU) == FTDI and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        baud = 115200
        ser = Serial(PORT, baud, timeout=TIMEOUT)
        devices = []
        for mbt_addr in range(1, 32):
            ser.write(MBTempChecksum(chr(mbt_addr)+"\x10\x00\x01\x00"))
            res = ser.read(10)
            if len(res) == 7 and res[1] == "\x11":
                devices.append(mbt_addr)
        ser.close()
        if len(devices):
            persist_info(Type.MBTEMP, baud, MBTEMP, 'MBTemps connected {}'.format(devices))


def mks9376b():
    """
    MKS 937B
    """
    logger.info('MKS 937B')
    if GPIO.input(PIN_FTDI_PRU) == FTDI and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        baud = 115200
        ser = Serial(port=PORT, baudrate=baud, timeout=TIMEOUT)
        devices = []
        for mks_addr in range(1, 255):
            msgm = '\@{0:03d}'.format(mks_addr) + "PR1?;FF"
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(msgm)
            res = ser.read()
            if len(res) != 0:
                devices.append(mks_addr)
        ser.close()
        if len(devices):
            persist_info(Type.MKS937B, baud, MKS937B, 'MKS937Bs connected {}'.format(devices))


def Agilent4UHV_CRC(string):
    counter = 0
    i = 0
    for b in string:
        if i > 0:
            counter ^= b
        i += 1

    string.append(int(bin(counter)[6:], 2))
    string.append(int(bin(counter)[2:6], 2))
    return(string)


def agilent4uhv():
    """
    AGILENT 4UHV
    """
    logger.info('AGILENT 4UHV')
    if GPIO.input(PIN_FTDI_PRU) == FTDI and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        baud = 38400
        ser = Serial(port=PORT, baudrate=baud, timeout=.2)
        devices = []
        for addr in range(0, 32):
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            pl = bytearray()
            pl.append(0x02)
            pl.append(addr  + 128)
            pl.append(0x38)
            pl.append(0x31)
            pl.append(0x30)
            pl.append(0x30)
            pl.append(0x03)
            ser.write(Agilent4UHV_CRC(pl))
            res = ser.read(15)
            if len(res) != 0:
                devices.append(addr)
        ser.close()
        if len(devices):
            persist_info(Type.AGILENT4UHV, baud, AGILENT4UHV, 'AGILENT4UHV connected {}'.format(devices))

def spixconv():
    """
    SPIxCONV
    """
    logger.info('SPIxCONV')
    '''
    if PRUserial485_address() == 21:
        #persist_info(Type.SPIXCONV, baud, SPIXCONV, 'SPIXCONV connected {}'.format(devices))
    '''
    pass
