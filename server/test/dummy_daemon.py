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

node = Node()
node.type = Type()

node_key, node_info, type_info = node.to_set() 
message  = {'comm':Command.PING,'n': node_info, 't' : type_info[1] }
str_msg = str(message)
chk = NetUtils.checksum(str_msg)
payload = {'chk':chk, 'payload':message}
pack = msgpack.packb(payload, use_bin_type=True)

while True:
    try:
        pingSocket.sendto(pack, ('0.0.0.0', 9876))
        time.sleep(1.)
    except:
        traceback.print_exc()
