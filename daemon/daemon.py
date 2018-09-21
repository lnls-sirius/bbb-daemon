#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import socket
import threading
import time

from os import environ

from bbb import BBB
from common.entity.entities import Command
from common.network.utils import NetUtils, checksum

CONFIG_PATH = environ.get('CONFIG_PATH', '/root/bbb-daemon/bbb.bin')
TYPE_RC_LOCAL_PATH = environ.get('TYPE_RC_LOCAL_PATH', 'init/rc.local')
RC_LOCAL_DESTINATION_PATH = environ.get('RC_LOCAL_DESTINATION_PATH', '/etc/rc.local')
FTP_SERVER_PORT = int(environ.get('FTP_SERVER_PORT',1026))
 
FTP_DESTINATION_FOLDER = environ.get('FTP_DESTINATION_FOLDER', '/root')
servAddr = environ.get('SERVER_APP_IP','10.0.6.44')
pingPort = environ.get('BBB_UDP_PORT', 9876)
bindPort = environ.get('BBB_TCP_PORT', 9877)

PING_CANDIDATES = ['10.0.6.44', '10.0.6.48', '10.0.6.51']

if not servAddr in PING_CANDIDATES:
    PING_CANDIDATES.append(servAddr)

print('CONFIG_PATH',CONFIG_PATH)
print('TYPE_RC_LOCAL_PATH',TYPE_RC_LOCAL_PATH)
print('RC_LOCAL_DESTINATION_PATH',RC_LOCAL_DESTINATION_PATH)
print('FTP_SERVER_PORT',FTP_SERVER_PORT)
print('FTP_DESTINATION_FOLDER',FTP_DESTINATION_FOLDER)
print('SERVER_APP_IP',servAddr)
print('BBB_UDP_PORT',pingPort)
print('BBB_TCP_PORT',bindPort)
print('PING_CANDIDATES',PING_CANDIDATES)


class Daemon():
    def __init__(self, serverAddress: str, pingPort: int, bindPort: int, ftpDestinationFolder: str):
        self.ftpDestinationFolder = ftpDestinationFolder

        self.bbb = BBB(path=CONFIG_PATH, rc_local_dest_path=RC_LOCAL_DESTINATION_PATH, sftp_port=FTP_SERVER_PORT,
                       sfp_server_addr=servAddr, ftp_destination_folder=self.ftpDestinationFolder)
        self.serverAddress = serverAddress
        self.pingPort = pingPort
        self.bindPort = bindPort

        self.pingThread = threading.Thread(target=self.ping_udp)
        self.pinging = True
        self.pingThread.start()

        self.commandThread = threading.Thread(target=self.listen)
        self.listening = True
        self.commandThread.start()

    def ping_udp(self):
        """
        Sends the current parameters set on the bbb to the server so it can monitor if it's configured or not.
        Command.PING,
        self.bbb.name,
            self.bbb.type,
            self.myIp,
            @todo: rc.config,  pv.prefix
            Under development ...
        :return:
        """
        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:
            try:
                info = self.bbb.getInfo()
                message = "{}|{}".format(checksum(info), info)
                for addr in PING_CANDIDATES:
                    pingSocket.sendto(message.encode('utf-8'), (addr, self.pingPort))
                time.sleep(1)
            except :
                pass

    def stop(self):
        self.pinging = False
        self.listening = False

    def listen(self):
        """
            Listen to commands from the server.
        :return:
        """
        commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        commandSocket.bind(("0.0.0.0", self.bindPort))
        commandSocket.listen(1)

        while self.listening:

            connection, addr = commandSocket.accept()

            command = NetUtils.recvCommand(connection)

            if command == Command.SWITCH:
                print("Command SWITCH")
                # Don't change this order !
                node = NetUtils.recvObject(connection)
                self.bbb.update(node)
                print("bbb updated ! Rebooting now !")
                self.pinging = False
                self.bbb.reboot()

            if command == Command.REBOOT:
                self.pinging = False
                self.bbb.reboot()

        commandSocket.close()

if __name__ == '__main__':
    
    if not FTP_DESTINATION_FOLDER.endswith('/'):
        FTP_DESTINATION_FOLDER = FTP_DESTINATION_FOLDER + '/'

    if not os.path.exists(FTP_DESTINATION_FOLDER):
        os.makedirs(FTP_DESTINATION_FOLDER)

    Daemon(serverAddress=servAddr, pingPort=pingPort, bindPort=bindPort, ftpDestinationFolder=FTP_DESTINATION_FOLDER)
