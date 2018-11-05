#!/usr/bin/python3
import socket
import time
import pickle
import os   
import json
import msgpack

from common.entity.entities import Command, Node, Type
from common.network.utils import NetUtils
import traceback
pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = {
    'node_dict': {
        'config_time': '2018-11-01 16:05:50.912405',
        'ip_address': '10.0.6.34',
        'sector': 1, 'state': 2,
        'details': 'MBTEMP -  MBTemps connected [5]\tbaudrate=115200', 'counter': 0,
        'type': 'MBTemp',
        'name': 'CON-Patricia',
        'state_string': 'Connected'
    }, 
    'type_dict': {
        'repo_url': 'A generic URL.',
        'code': 4,
        'sha': '',
        'description': 'A generic host.'
    }
}


# node = Node()
# node.type = Type()

# node_key, node_info, type_info = node.to_set() 
# message  = {'comm':Command.PING,'n': node_info, 't' : type_info[1] }
# str_msg = str(message)
# chk = NetUtils.checksum(str_msg)
# payload = {'chk':chk, 'payload':message}
payload = msg
pack = msgpack.packb(payload, use_bin_type=True)

while True:
    try:
        pingSocket.sendto(pack, ('0.0.0.0', 9876))
        time.sleep(1.)
    except:
        traceback.print_exc()

