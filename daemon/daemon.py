from common.entity.entities import Command
from common.network.utils import NetUtils

import mutex
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

    def update (self, newName, newType):
        self.name = newName
        self.name = newType

    def readParameters (self):

        f = open (self.configPath, "r")

        self.name = f.readline ()[:-1]
        print (self.name)
        self.type = f.readline ()[:-1]
        print (self.type)

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
                typeName = NetUtils.recvObject (connection)
                nodeName = NetUtils.recvObject (connection)
                self.bbb.update (nodeName, typeName)

            if command == Command.REBOOT: pass

        self.commandSocket.close ()

    def stop (self):
        self.pinging = False
        self.listening = False

Daemon ()
