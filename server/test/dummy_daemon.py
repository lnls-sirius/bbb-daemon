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
 
def get_message(node):
    node_key, node_info = node.to_dict() 
    message  = {'comm':Command.PING,'n': node_info  } 
    chk = NetUtils.checksum(str(message))
    payload = {'chk':chk, 'payload':message} 
    pack = msgpack.packb(payload, use_bin_type=True)
    return pack

while True:
    try:
        pingSocket.sendto(get_message(Node(name='1', ip_address='10.128.0.0')), ('0.0.0.0', 9876))
        pingSocket.sendto(get_message(Node(name='2', ip_address='10.128.0.20')), ('0.0.0.0', 9876))
        pingSocket.sendto(get_message(Node(name='3', ip_address='10.128.0.30')), ('0.0.0.0', 9876))
        pingSocket.sendto(get_message(Node(name='4', ip_address='10.128.0.40')), ('0.0.0.0', 9876))
        pingSocket.sendto(get_message(Node(name='5', ip_address='10.128.0.50')), ('0.0.0.0', 9876))
        pingSocket.sendto(get_message(Node(name='6', ip_address='10.128.0.60')), ('0.0.0.0', 9876))
        time.sleep(1.)
    except:
        traceback.print_exc()

