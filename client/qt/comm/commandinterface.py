from common.entity.entities import Command, Node, NodeState, Type

import json
import socket
import struct
import threading
import traceback

class CommandInterface ():

    def __init__ (self, serverAddress = "10.128.0.5", serverPort = 6789):

        self.serverAddress = serverAddress
        self.port = serverPort

        self.interfaceSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

        self.connectionLock = threading.Lock ()
        self.connection = False
        self.connection = self.connect ()

    def connect (self):

        if not self.connection:
            self.connectionLock.acquire ()
            attempts = 5
            while attempts > 0:
                try:
                    print (self.serverAddress + " " + str(self.port))
                    self.interfaceSocket.connect ((self.serverAddress, self.port))
                    print ("connection established")
                    self.connectionLock.release ()
                    return True
                except Exception as e:
                    traceback.print_exc()
                    attempts = attempts - 1

            self.connectionLock.release ()
            return False

        return True

    def sendCommand (self, command = Command.EXIT):
        self.interfaceSocket.send (struct.pack ("!i", command))

    def recvCommand (self):
        return struct.unpack ("!i", self.interfaceSocket.recv(4)) [0]

    def sendData (self, data, delimiter = "\n"):
        return self.interfaceSocket.send (bytearray (data + delimiter, encoding = "utf-8"))

    def recvData (self, delimiter = "\n"):

        data = ""
        byte = self.interfaceSocket.recv (1).decode("utf-8")
        while byte != "\n":
            data = data + byte
            byte = self.interfaceSocket.recv (1).decode("utf-8")

        return data

    def recvNode (self):

        nodeDict = json.loads (self.recvData ())
        typeDict = nodeDict ["type"]
        return Node (name = nodeDict ["name"], ip = nodeDict ["ip"], state = nodeDict ["state"], sector = nodeDict ["sector"], \
                     typeNode = Type (name = typeDict ["name"], color = typeDict ["color"], description = typeDict ["description"]))

    def recvType (self):

        typeDict = json.loads (self.recvData ())
        return Type (name = typeDict ["name"], color = typeDict ["color"], description = typeDict ["description"])

    def appendType (self, newType):

        self.connection = self.connect ()

        if self.connection == False:
            return False

        self.connectionLock.acquire ()

        self.sendCommand (Command.APPEND_TYPE)
        self.sendData (json.dumps (newType.__dict__()))

        self.connectionLock.release ()

        return True

    def removeType (self, typeName):

        self.connection = self.connect ()

        if self.connection == False:
            return []

        self.connectionLock.acquire ()

        self.sendCommand (Command.REMOVE_TYPE)
        self.sendData (typeName)

        self.connectionLock.release ()

    def fetchTypes (self):

        self.connection = self.connect ()

        if self.connection == False:
            return []

        self.connectionLock.acquire ()

        self.sendCommand (Command.GET_TYPES)

        types = []
        command = self.recvCommand ()
        while command != Command.END:
            if command == Command.TYPE:
                types.append (self.recvType())

            command = self.recvCommand ()

        self.connectionLock.release ()
        return types

    def getNodesFromSector (self, sector, registered = True):

        self.connection = self.connect ()

        if self.connection == False:
            return []

        self.connectionLock.acquire ()

        if registered:
            self.sendCommand (Command.GET_REG_NODES_SECTOR)
        else:
            self.sendCommand (Command.GET_UNREG_NODES_SECTOR)

        self.sendData (sector)

        nodes = []
        command = self.recvCommand ()
        while command != Command.END:
            if command == Command.NODE:
                nodes.append (self.recvNode())
            command = self.recvCommand ()

        self.connectionLock.release ()
        return nodes

    def appendNode (self, node):

        self.connection = self.connect ()

        if self.connection == False:
            return False

        self.connectionLock.acquire ()

        self.sendCommand (Command.APPEND_NODE)
        self.sendData (json.dumps (node.__dict__()))

        self.connectionLock.release ()

        return True


    def removeNodeFromSector (self, node):

        self.connection = self.connect ()

        if self.connection == False:
            return False

        self.connectionLock.acquire ()

        self.sendCommand (Command.REMOVE_NODE)
        self.sendCommand (Command.NODE)
        self.sendData (json.dumps (node.__dict__()))

        self.connectionLock.release ()
        return True
