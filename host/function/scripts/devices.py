#!/usr/bin/python-sirius
import logging
import time
import os
import subprocess
import sys
import struct
import Adafruit_BBIO.GPIO as GPIO
from PRUserial485 import PRUserial485_open,PRUserial485_write, PRUserial485_read, PRUserial485_close, PRUserial485_address
from common.function.consts import *
from serial import Serial, STOPBITS_TWO, SEVENBITS, PARITY_EVEN, STOPBITS_ONE, EIGHTBITS, PARITY_NONE
from common.function.persist import persist_info

logger = logging.getLogger('Whoami')


if os.path.exists(PORT):
    ser = Serial(PORT)



if os.path.exists('/root/SPIxCONV/software/scripts'):
    sys.path.append('/root/SPIxCONV/software/scripts')
    import init
    import flash
    import selection

    SPIxCONV = True
else:
    logger.error('/root/SPIxCONV/software/scripts does not exist, SPIxCONV will always be false !')
    SPIxCONV = False



sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../'))
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
    persist_info(Type(code=Type.UNDEFINED).name, 0, 'RESET - Still trying to find out where im connected...')

def counting_pru():
    """
    CountingPRU
    """
    logger.info('Counting PRU')
    if PRUserial485_address() != 21 and not os.path.isfile(PORT):
        persist_info(Type(code=Type.COUNTING_PRU).name, 0, COUNTING_PRU)


def no_tty():
    """
    NO /dev/ttyUSB0
    """
    logger.info('No /dev/ttyUSB0')
    if not os.path.exists(PORT) and PRUserial485_address() == 21:
        persist_info(Type(code=Type.UNDEFINED).name, 115200, NOTTY)


def power_supply_pru():
    """
    PRU Power Supply
    """
    logger.info('PRU Power Supply')
    ps_model_names = {0:"Empty", 1:"FBP", 2:"FBP_DCLINK", 3:"FAC_ACDC", 4:"FAC_DCDC", 5:"FAC_2S_ACDC",
                    6:"FAC_2S_DCDC", 7:"FAC_2P4S_ACDC", 8:"FAC_2P4S_DCDC", 9:"FAP", 10:"FAP_4P", 11:"FAC_DCDC_EMA", 12:"FAP_2P2S_Master", 13:"FAP_2P2S_Slave", 31:"UNDEFINED"}
    if GPIO.input(PIN_FTDI_PRU) == PRU and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        os.system("/root/pru-serial485/src/overlay.sh")
        baud = 6
        PRUserial485_open(baud,b'M')
        devices = []
        ps_model = []
        for ps_addr in range(1, 32):
            msg=[i for i in BSMPChecksum(chr(ps_addr)+"\x10\x00\x01\x00")]
            PRUserial485_write(msg, 200)
            res = PRUserial485_read()
            logger.info('{} res: {}'.format(ps_addr, res))
            if len(res) == 7 and res[1] == "\x11":
                devices.append(ps_addr)
                ps_model = ps_model_names[ord(res[5])%32]    # PS model: res[5] (bits 4..0)
            time.sleep(0.1)
        PRUserial485_close()
        persist_info(Type(code=Type.POWER_SUPPLY).name, 6000000, 'PS model {}. Connected: {}'.format(ps_model, devices))



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
        ser.baudrate = baud
        ser.bytesize = SEVENBITS
        ser.parity = PARITY_EVEN
        ser.stopbits = STOPBITS_TWO
        ser.timeout = TIMEOUT
        msg = thermoIncluirChecksum("\x07" + "01RM1")
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(msg.encode('latin'))
        res = ser.read(50)

        if len(res) != 0:
            persist_info(Type(code=Type.SERIAL_THERMO).name, baud, SERIAL_THERMO)


def BSMPChecksum(string):
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
        ser.baudrate = baud
        ser.bytesize = EIGHTBITS
        ser.parity = PARITY_NONE
        ser.stopbits = STOPBITS_ONE
        ser.timeout = TIMEOUT
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        devices = []
        for mbt_addr in range(1, 32):
            ser.write(BSMPChecksum(chr(mbt_addr)+"\x10\x00\x01\x00").encode('latin'))
            res = ser.read(10).decode('latin')
            if len(res) == 7 and res[1] == "\x11":
                devices.append(mbt_addr)
        if len(devices):
            persist_info(Type(code=Type.MBTEMP).name, baud, 'MBTemps connected {}'.format(devices))


def mks9376b():
    """
    MKS 937B
    """
    logger.info('MKS 937B')
    if GPIO.input(PIN_FTDI_PRU) == FTDI and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        baud = 115200
        ser.baudrate = baud
        ser.bytesize = EIGHTBITS
        ser.parity = PARITY_NONE
        ser.stopbits = STOPBITS_ONE
        ser.timeout = 0.05
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        devices = []
        for mks_addr in range(1, 255):
            msgm = '\@{0:03d}'.format(mks_addr) + "PR1?;FF"
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(msgm.encode('latin'))
            res = ser.read(20).decode('latin')
            if len(res) != 0:
                devices.append(mks_addr)
        if len(devices):
            persist_info(Type(code=Type.MKS937B).name, baud, 'MKS937Bs connected {}'.format(devices))


def Agilent4UHV_CRC(string):
    counter = 0
    i = 0
    for b in string:
        if i > 0:
            counter ^= ord(b)
        i += 1

    string += chr(int(bin(counter)[2:6], 2)+48)
    string += chr(int(bin(counter)[6:], 2)+48)
    return(string)


def agilent4uhv():
    """
    AGILENT 4UHV
    """
    logger.info('AGILENT 4UHV')
    if GPIO.input(PIN_FTDI_PRU) == FTDI and GPIO.input(PIN_RS232_RS485) == RS485 and PRUserial485_address() == 21:
        baud = 38400
        ser.baudrate = baud
        ser.bytesize = EIGHTBITS
        ser.parity = PARITY_NONE
        ser.stopbits = STOPBITS_ONE
        ser.timeout = 0.6
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        devices = []
        for addr in range(0, 32):
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            pl = ""
            pl += "\x02"
            pl += chr(addr + 128)
            pl += "\x38"
            pl += "\x31"
            pl += "\x30"
            pl += "\x30"
            pl += "\x03"
            ser.write(Agilent4UHV_CRC(pl).encode('latin'))
            res = ser.read(15).decode('latin')
            if len(res) != 0:
                devices.append(addr)
        if len(devices):
            persist_info(Type(code=Type.AGILENT4UHV).name, baud, 'AGILENT4UHV connected {}'.format(devices))

def spixconv():
    """
    SPIxCONV
    """
    logger.info('SPIxCONV')

    if not SPIxCONV:
        return

    subprocess.call('config-pin P9_17 spi_cs', shell=True)   # CS
    subprocess.call('config-pin P9_21 spi', shell=True)      # DO
    subprocess.call('config-pin P9_18 spi', shell=True)      # DI
    subprocess.call('config-pin P9_22 spi_sclk', shell=True) # CLK

    subprocess.call('config-pin P8_37 gpio', shell=True)     # BUSY
    subprocess.call('config-pin P9_24 gpio', shell=True)     # LDAC / CNVST
    subprocess.call('config-pin P9_26 gpio', shell=True)     # RS

    for addr in range(0, 255):
        if flash.ID_read(addr) == 4:
            spi_addr = 8 if flash.address_read(addr) == 0 else flash.address_read(addr)
            logger.info('{}'.format('Addr code',addr,'Selection Board ID', selection.board_ID(addr), 'Flash address', flash.address_read(addr),'SPI Addr',spi_addr))
            persist_info(Type(code=Type.SPIXCONV).name, spi_addr, 'SPIXCONV connected {}'.format(spi_addr))
