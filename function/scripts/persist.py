#!/usr/bin/python
from os import environ
import json
from datetime import datetime

def persist_info(device, baud, exit_code=None, details=None):
    if exit_code != None:
        write_info('res', exit_code)
    if type(baud) != int:
        raise TypeError('baud type is incorrect. ', baud)
    if type(device) != str:
        raise TypeError('device type in incorrect. ', device)

    write_info('baudrate', str(baud))

    device_info = {'device': device, 'baudrate': baud, 'details':details, 'time':str(datetime.now())}
    print(device_info)

    write_info('/opt/device.json', json.dumps(device_info)) 
    exit()

def write_info(file_name, data):
    file = open(file_name, 'w+')
    file.writelines(data)
    file.close() 