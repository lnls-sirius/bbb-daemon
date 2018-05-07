from common.entity.entities import Command
from common.network.utils import NetUtils

import os
import socket
import struct
import threading
import time
import traceback

class BBB ():

    CONFIG_PATH = "/root/bbb-daemon/bbb.cfg"

    def __init__ (self, path = CONFIG_PATH):
        self.configPath = path
        self.readParameters ()

    def reboot (self):
        os.system('reboot')

    def update (self, newName, newType):

        self.name = newName

        hostnameFile = open ("/etc/hostname", "w")
        hostnameFile.write (self.name.replace (":", "-"))
        hostnameFile.close ()

        self.type = newType

        typeFile = open (self.configPath, "w")
        typeFile.write (self.type + "\n")
        typeFile.close ()

    def readParameters (self):

        name = os.popen ("hostname", "r").readline () [:-1]

        indexes = [i for i, letter in enumerate (name) if letter == "-"]

        name = list (name)
        if len(indexes) > 2:
            name [indexes[1]] = ":"

        self.name = "".join (name)

        f = open (self.configPath, "r")
        self.type = f.readline ()[:-1]
        f.close ()
        
class Daemon ():

    def __init__ (self, path = "", serverAddress = "10.0.6.65", pingPort = 9876, bindPort = 9877):

        self.serverAddress = serverAddress
        self.pingPort = pingPort
        self.bindPort = bindPort

        self.bbb = BBB ()

        self.pingThread = threading.Thread (target = self.ping)
        self.pinging = True
        self.pingThread.start ()

        self.commandThread = threading.Thread (target = self.listen)
        self.listening = True
        self.commandThread.start ()

    def ping (self):

        pingSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        pingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        pingSocket.settimeout(10)

        connected = False

        while self.pinging:

            try:
                if not connected:
                    pingSocket.connect ((self.serverAddress, self.pingPort))
                    print ("connection established")
                    connected = True

                NetUtils.sendCommand (pingSocket, Command.PING)
                NetUtils.sendObject (pingSocket, self.bbb.name)
                NetUtils.sendObject (pingSocket, self.bbb.type)

            except socket.error:
                print ("error")
                connected = False

            time.sleep (1)

    def stop (self):
        self.pinging = False
        self.listening = False

    def listen (self):

        commandSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        commandSocket.bind (("0.0.0.0", self.bindPort))
        commandSocket.listen (1)

        while self.listening:

            connection, addr = commandSocket.accept ()

            command = NetUtils.recvCommand (connection)

            if command == Command.SWITCH:
                print ("Commando SWITCH")
                typeName = NetUtils.recvObject (connection)
                nodeName = NetUtils.recvObject (connection)

                print (typeName + " " + nodeName)

                self.bbb.update (nodeName, typeName)

            if command == Command.REBOOT:
                self.pinging = False
                self.bbb.reboot ()

        self.commandSocket.close ()

    def stop (self):
        self.pinging = False
        self.listening = False

Daemon ()
