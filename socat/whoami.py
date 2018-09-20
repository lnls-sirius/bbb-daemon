#!/usr/bin/python3
# -*- coding: utf-8 -*-

# modules
from os import environ
from serial import Serial, STOPBITS_TWO, SEVENBITS, PARITY_EVEN
import Adafruit_BBIO.GPIO as GPIO
import sys

CODE = sys.argv[1]

# port for serial interface
port = '/dev/ttyUSB0'

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

thermo_interface = Serial(port = "{}".format(port),
                                 baudrate = 19200,
                                 bytesize = SEVENBITS,
                                 parity = PARITY_EVEN,
                                 stopbits = STOPBITS_TWO,
                                 timeout = 0.5
                                )
thermo = incluirChecksum("\x07" + "01RM1")
thermo_interface.write(thermo)
datathermo = thermo_interface.read(50)
if len(datathermo) != 0:
    print('SERIAL_THERMO' + CODE)
    file = open('device.conf', 'w')
    file.writelines('Thermo_Probe\n19200')
    file.close()
    exit()

# MBTemp Checksum
def mbtempChecksum(entrada):
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = 256 - soma % 256
    return(entrada + "{0:02X}".format(soma))

# commands for serial interface
cmds = [
    {
        'baud' : 115200,
        'msg' : ['TORRE1','TORRE2'],
        'device':'rf-booster-tower'
    },
    {
        'baud' : 115200,
        'msg' :  ['RACK1','RACK2','RACK3','RACK4'],
        'device':'rf-ring-tower'
    },
    {
        'baud':115200,
        'msg':'\x10\x00\x01\x00', 
        'device':'mbtemp'
    },
    {
        'baud':9600,
        'msg': '?',
        'device': 'agilent4uhv'
    }
]

die = False

# main loop
while True:
    for cmd in cmds:
        ser = None
        try:
            res = None
            ser = Serial(port, cmd.get('baud'), timout=0.5)

	    # mbtemp check
            if cmd.get('device') == 'mbtemp':
                for i in range(1,32):
                    if i < 10:
                        msgm=mbtempChecksum(r'\x0{}'.format(i) + cmd.get('msg'))
                        ser.write(msgm)
                    elif i > 9:
                        msgm=mbtempChecksum(r'\x{}'.format(i) + cmd.get('msg'))
                        ser.write(msgm)
                    if len(ser.read()) != 0:
			            # É ISSO !!!!!
                        print('MBTemp')
                        file = open('device.conf', 'w')
                        file.writelines(cmd.get('device') + '\n' + cmd.get('baud'))
                        file.close()
                        exit()
                    pass

            #agilent 4uhv check
            elif cmd.get('device') == 'agilent4uhv':
                pass
            # mks 937 b
            elif cmd.get('device') == 'mks937b':
                pass
                
        except:
            pass
        finally:
            if ser:
                ser.close()
        if die:
            exit()
    pass
