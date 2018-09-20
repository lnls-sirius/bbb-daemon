#!/usr/bin/python3

def persist_info(device, baud, exit_code = None):
    if exit_code != None:
        print(exit_code)
    if type(baud) != int:
        raise TypeError('baud type is incorrect. ', baud)
    if type(device) != str:
        raise TypeError('device type in incorrect. ', device)

    file = open('device.conf', 'w+')
    file.writelines(device + ';' + baud)
    file.close()
    exit()
    