#!/usr/bin/python3
import socket
import time
import os   
import json

from common.entity.entities import Command
from common.network.utils import NetUtils, checksum

pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

info = {
    'command':Command.PING,
    'name':'self.node.name',
    'hostType':'self.nods.type.name',
    'bbbIpAddr':'10.0.6.45',
    'device':'self.node.device',
    'details':'self.node.details',
    'configTime':'self.node.configTime',
    'bbbSha':'self.node.type.sha'
} 
info =  json.dumps(info)
while True:
    try:
        message = "{}|{}".format(checksum(info), info)
        pingSocket.sendto(message.encode('utf-8'), ('0.0.0.0', 9876))
        print(message)
        time.sleep(1)
    except Exception as e:
        print(e) 
        pass
