import os
import socket
import sys
import threading
import time

from entity.bbb import BBB
from common.entity.entities import Command
from common.network.utils import NetUtils, checksum

##################################################################
CONFIG_PATH = "/root/bbb-daemon/bbb.cfg"
typeRcLocalPath = "init/rc.local"
RC_LOCAL_DESTINATION_PATH = "/etc/rc.local"

servAddr = "10.0.0.70"
pingPort = 9876
bindPort = 9877

##################################################################
# CLONE_PATH = "../"  # remember to place the forward slash !


class Daemon():

    def __init__(self, serverAddress: str, pingPort: int, bindPort: int):

        self.bbb = BBB(path=CONFIG_PATH)
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
                Command.PING,
                self.bbb.name,
                self.bbb.type,
                self.myIp

            Under development ...
        :return:
        """
        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:
            info = self.bbb.getInfo()
            message = "{}|{}".format(checksum(info), info)
            ## {chk} | {cmd} | {name} | {type} | {ipAddr}
            pingSocket.sendto(message.encode('utf-8'), (self.serverAddress, self.pingPort))
            time.sleep(1)

    def stop(self):
        self.pinging = False
        self.listening = False

    def listen(self):

        commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        commandSocket.bind(("0.0.0.0", self.bindPort))
        commandSocket.listen(1)

        while self.listening:

            connection, addr = commandSocket.accept()

            command = NetUtils.recvCommand(connection)

            if command == Command.SWITCH:
                print("Commando SWITCH")
                # Type ...
                typeName = NetUtils.recvObject(connection)
                typeRepoUrl = NetUtils.recvObject(connection)
                typeRcLocalPath = NetUtils.recvObject(connection)

                # Node
                nodeName = NetUtils.recvObject(connection)

                print(typeName + " " + nodeName + " " + typeRepoUrl + " " + typeRcLocalPath)

                self.bbb.update(newName=nodeName, newType=typeName, newTypeRepoUrl=typeRepoUrl,
                                newTypeRcLocalPath=typeRcLocalPath)

            if command == Command.REBOOT:
                self.pinging = False
                self.bbb.reboot()

        commandSocket.close()

    def stop(self):
        self.pinging = False
        self.listening = False


if __name__ == '__main__':

    print("arg[1]=servAddress arg[2]=pingPort arg[3]=bindPort")
    if len(sys.argv) == 4:
        servAddr = sys.argv[1]
        pingPort = int(sys.argv[2])
        bindPort = int(sys.argv[3])

    if not os.path.exists('/root/bbb-daemon-repos/'):
        os.makedirs('/root/bbb-daemon-repos/')

    print("arg[1]={}\targ[2]={}\targ[3]={}\t".format(servAddr, pingPort, bindPort))
    Daemon(serverAddress=servAddr, pingPort=pingPort, bindPort=bindPort)
