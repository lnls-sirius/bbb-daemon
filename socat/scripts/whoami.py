#!/usr/bin/python3
# -*- coding: utf-8 -*-
from serial import Serial
from os import environ

from devices import mbtempChecksum
from persist import persist_info

CODE = environ.get('CODE')
TIMEOUT = 1.
PORT = '/dev/ttyUSB0'
# commands for serial interface
cmds = [
    {
        'device':'mbtemp',
        'baud':115200,
        'msg':'\x10\x00\x01\x00'
    },
    {
        'device': 'agilent4uhv',
        'baud':9600,
        'msg': '?'
    },
    {
        'device':'mks937b',
        'baud':115200,
        'msg':'?'
    }
]

die = False

# main loop
while True:
    for cmd in cmds:
        ser = None
        try:
            ser = Serial(PORT, cmd.get('baud'), timout=TIMEOUT)
	        # mbtemp check
            if cmd.get('device') == 'mbtemp':
                for i in range(1,32):
                    if i < 10:
                        msgm = mbtempChecksum(r'\x0{}'.format(i) + cmd.get('msg'))
                        ser.write(msgm)
                    elif i > 9:
                        msgm = mbtempChecksum(r'\x{}'.format(i) + cmd.get('msg'))
                        ser.write(msgm)

                    if len(ser.read()) != 0:
                        persist_info(cmd.get('device'), cmd.get('baud'))

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

