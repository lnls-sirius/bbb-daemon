#!/usr/bin/python
import json
from datetime import datetime


def persist_info(device, baud, exit_code=None, details=None):
    """
    This method persist the information about witch device is connected to this sbc.
    The info is stored using the following format:
    device_info = {'device': device, 'baudrate': baud, 'details': details, 'time': str(datetime.now())}
    Where:
    'device' is  the common.entity.entities Type."DEVICE".
    'details' a simple description.
    'time' the string representation os a python time object at the time this information has been defined.
    'baudrate' is the baudrate used for communicate to the connected device.
    """
    if exit_code != None:
        write_info('res', exit_code)
    if type(baud) != int:
        raise TypeError('baud type is incorrect. ', baud)

    write_info('baudrate', str(baud))

    device_info = {'device': device, 'baudrate': baud, 'details': details, 'time': str(datetime.now())}
    print(device_info)

    write_info('/opt/device.json', json.dumps(device_info))
    exit()


def write_info(file_name, data):
    file = open(file_name, 'w+')
    file.writelines(data)
    file.close()
