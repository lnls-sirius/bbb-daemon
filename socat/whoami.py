#!/usr/bin/python3.6
from os import environ
from serial import Serial 
from devices.MBTemp import communicate
import Adafruit_BBIO.GPIO as GPIO

CODE = environ.get('CODE')

if GPIO.input("P8_11") and GPIO.input("P8_12"):
    print('PRU_FONTES' + CODE)
    exit()

port = '/dev/ttyUSB0'
baudrates = Serial.BAUDRATES

''' 
    Iterar pelos possíveis baudrates testando todas as possibilidades
    de comandos. Isso deverá ser repetido até alguém responder.

    Com isso saberemos o baudrate da aplicação e com quem estamos lidando.
    
    Por enquanto isso irá funcionar apenas para FTDI, não dando suporte a aplaicações 
    que fazem uso da interface PRU.
    
    
'''

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
        'msg':[0x01, 0x10, 0x00, 0x01, 0x1], #?
        'device':'mbtemp'
    },
    {
        'baud':9600,
        'msg': '?',
        'device': 'agilent4uhv'
    }
]

die = False
while True:
    for cmd in cmds:
        ser = None
        try:
            res = None
            ser = Serial(port, cmd.get('baud'), timout=0.5)

            if cmd.get('device') == 'mbtemp':
                pass
            elif cmd.get('device') == 'mbtemp':
                pass
                # for addr in range(1,32):
                #     message_to_send = ''
                #     cs = 0
                #     for i in msg:
                #         message_to_send += chr(i)
                #         cs += i
                #     message_to_send += chr((0x100 - (cs % 0x100)) & 0xFF)                    
                #     ser.write()

                res = ser.read()
                if res:
                    print(res)
                    die = True
        except:
            pass
        finally:
            if ser:
                ser.close()
        if die:
            exit()
    pass