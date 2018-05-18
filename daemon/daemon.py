import os
import socket
import threading
import time
import os

from common.entity.entities import Command
from common.network.utils import NetUtils

import git
from shutil import copy


class BBB():
    CONFIG_PATH = "/root/bbb-daemon/bbb.cfg"
    typeRcLocalPath = "init/rc.local"
    RC_LOCAL_DESTINATION_PATH = "/etc/rc.local"
    CLONE_PATH = "../"  # remember to place the forward slash !

    def __init__(self, path=CONFIG_PATH):
        self.configPath = path
        self.readParameters()

    def reboot(self):
        os.system('reboot')

    def update_rclocal(self):
        if type is not None:
            git.Git(self.CLONE_PATH).clone(self.typeRepoUrl)
            repo_name = self.typeRepoUrl.split('/')[-1].split('.')[0]
            print("Cloned repository {} at {}/{}".format(self.typeRepoUrl, os.getcwd(), repo_name))
            copy(self.CLONE_PATH + repo_name + '/' + self.RC_LOCAL_ORIGIN_PATH, self.RC_LOCAL_DESTINATION_PATH)
            print("Copied file {} to {}".format(repo_name + '/' + self.RC_LOCAL_ORIGIN_PATH,
                                                self.RC_LOCAL_DESTINATION_PATH))
        else:
            print("Not repo URL defined.")

    def update(self, newName, newType, typeRepoUrl, typeRcLocalPath):
        try:
            if newName is not None:
                self.name = newName

                hostnameFile = open("/etc/hostname", "w")
                hostnameFile.write(self.name.replace(":", "-"))
                hostnameFile.close()
            if newType is not None:
                self.type = newType
                typeFile = open(self.configPath, "w+")
                typeFile.write(self.type + "\n")
                typeFile.close()

            if typeRcLocalPath is not None:
                self.typeRcLocalPath = typeRepoUrl
                self.update_rclocal()
                pass

        except FileNotFoundError:
            print("Configuration files not found.")
            pass

    def readParameters(self):
        try:
            name = os.popen("hostname", "r").readline()[:-1]
            indexes = [i for i, letter in enumerate(name) if letter == "-"]
            name = list(name)
            if len(indexes) > 2:
                name[indexes[1]] = ":"

            self.name = "".join(name)
        except FileNotFoundError:
            self.name = "error-hostname-not-found"

        try:
            f = open(self.configPath, "r")
            self.type = f.readline()[:-1]
            f.close()
        except FileNotFoundError:
            self.type = "error-configPath-not-found"


class Daemon():

    def __init__(self, path="", serverAddress="10.0.6.70", pingPort=9876, bindPort=9877):

        self.serverAddress = serverAddress
        self.pingPort = pingPort

        self.bbb = BBB()

        self.pingThread = threading.Thread(target=self.ping)
        self.pinging = True
        self.pingThread.start()

        self.commandThread = threading.Thread(target=self.listen)
        self.listening = True
        self.commandThread.start()

    def ping(self):

        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        pingSocket.settimeout(10)

        connected = False

        while self.pinging:

            try:
                if not connected:
                    pingSocket.connect((self.serverAddress, self.pingPort))
                    print("connection established")
                    connected = True

                NetUtils.sendCommand(pingSocket, Command.PING)
                NetUtils.sendObject(pingSocket, self.bbb.name)
                NetUtils.sendObject(pingSocket, self.bbb.type)

            except socket.error:
                print("error")
                connected = False

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

                print(typeName + " " + nodeName + typeRepoUrl)

                self.bbb.update(nodeName, typeName, typeRepoUrl, typeRcLocalPath)

            if command == Command.REBOOT:
                self.pinging = False
                self.bbb.reboot()

        self.commandSocket.close()

    def stop(self):
        self.pinging = False
        self.listening = False


Daemon()
