#!/usr/bin/python3
import socket
import time
import pickle
import os   
import json

from common.entity.entities import Command, Node, Type
from common.network.utils import NetUtils
import traceback
pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

node = Node()
node.type = Type()

node_key, node_info, type_info = node.to_set() 
message  = json.dumps({'command':Command.PING,'node': node_info, 'type' : type_info })

while True:
    try:
        payload = "{}|{}".format(NetUtils.checksum(message), message)
        pingSocket.sendto(message.encode('utf-8'), ('0.0.0.0', 9876))
        time.sleep(1.)
    except:
        traceback.print_exc()
