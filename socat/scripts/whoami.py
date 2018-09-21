#!/usr/bin/python
# -*- coding: utf-8 -*-
from serial import Serial
from os import environ
from persist import persist_info

from consts import *

from devices import  mbtemp

# commands for serial interface
cmds = [
    {
        'device':'mbtemp',
        'baud':115200 
    },
    {
        'device': 'agilent4uhv',
        'baud':9600 
    },
    {
        'device':'mks937b',
        'baud':115200 
    }
]

for cmd in cmds:
    ser = None 
    try:
        # mbtemp check
        if cmd.get('device') == 'mbtemp':
            ser = Serial(PORT, cmd.get('baud'), timeout=TIMEOUT)
            try: 
                mbtemp(cmd, ser)
            except Exception as e:
                print('{}'.format(e))
            ser.close()

        #agilent 4uhv check
        elif cmd.get('device') == 'agilent4uhv':
            pass

        # mks 937 b
        elif cmd.get('device') == 'mks937b':
            ser = Serial(port=PORT, baudrate=cmd.get('baud'), timeout=TIMEOUT)
            for i in range (1, 254):
                try:
                    msgm = '\@{0:03d}'.format(i) + "PR1?;FF"
                    ser.write(msgm)
                    res = ser.read()
                    if len(res) != 0:  
                        persist_info(cmd.get('device'), cmd.get('baud'), MKS937B, 'First MKS937b at addr {}'.format(i))
                except Exception as e:
                    print('{}'.format(e))
            ser.close()
            
    except Exception as e:
        print('{}'.format(e))

