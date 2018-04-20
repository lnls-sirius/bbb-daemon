from common.entity.entities import Command, Node, NodeState, Type

import pickle
import socket
import struct
import time
import threading
import traceback

class CommandInterface ():

    def __init__ (self, serverAddress = "10.128.0.5", serverPort = 6789):

        self.serverAddress = serverAddress
        self.port = serverPort

        self.interfaceSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.interfaceSocket.settimeout(10)

        self.connectionLock = threading.Lock ()
        self.connection = False
        self.connection = self.connect ()

    def connect (self):

        if not self.connection:
            self.connectionLock.acquire ()
            attempts = 1
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

    def sendData (self, data):
        self.interfaceSocket.send (struct.pack ("!i", len(data)))
        self.interfaceSocket.send (data)

    def recvData (self):
        dataSize = struct.unpack ("!i", self.interfaceSocket.recv(4)) [0]
        return self.interfaceSocket.recv (dataSize)

    def recvNode (self):
        return pickle.loads (self.recvData ())

    def recvType (self):
        return pickle.loads (self.recvData ())

    def appendType (self, newType):

        self.connection = self.connect ()

        if self.connection == False:
            return False

        self.connectionLock.acquire ()

        try:
            self.sendCommand (Command.APPEND_TYPE)
            self.sendData (pickle.dumps (newType))
            success = True
        except socket.error:
            self.connection = None
            success = False
        finally:
            self.interfaceSocket.close ()

        self.connectionLock.release ()

        return success

    def removeType (self, typeName):

        self.connection = self.connect ()

        if self.connection == False:
            return []

        self.connectionLock.acquire ()

        try:
            self.sendCommand (Command.REMOVE_TYPE)
            self.sendData (pickle.dumps(typeName))
        except socket.error:
            self.connection = None

        self.connectionLock.release ()

    def fetchTypes (self):

        self.connection = self.connect ()

        if self.connection == False:
            return []

        self.connectionLock.acquire ()

        try:
            types = []
            self.sendCommand (Command.GET_TYPES)
            command = self.recvCommand ()
            while command != Command.END:
                if command == Command.TYPE:
                    types.append (self.recvType())

                command = self.recvCommand ()
        except socket.error:
            types = []
            self.connection = None

        self.connectionLock.release ()
        return types

    def getNodesFromSector (self, sector, registered = True):

        self.connection = self.connect ()

        if self.connection == False:
            return []

        self.connectionLock.acquire ()

        try:
            if registered:
                self.sendCommand (Command.GET_REG_NODES_SECTOR)
            else:
                self.sendCommand (Command.GET_UNREG_NODES_SECTOR)

            self.sendData (pickle.dumps(sector))

            nodes = []
            command = self.recvCommand ()
            while command != Command.END:
                if command == Command.NODE:
                    nodes.append (self.recvNode())
                command = self.recvCommand ()
        except socket.error:
            nodes = []
            self.connection = None

        self.connectionLock.release ()
        return nodes

    def appendNode (self, node):

        self.connection = self.connect ()

        if self.connection == False:
            return False

        self.connectionLock.acquire ()

        try:
            self.sendCommand (Command.APPEND_NODE)
            self.sendData (pickle.dumps (node))
            success = True
        except socket.error:
            success = False
            self.connection = None

        self.connectionLock.release ()

        return success

    def removeNodeFromSector (self, node):

        self.connection = self.connect ()

        if self.connection == False:
            return False

        self.connectionLock.acquire ()

        try:
            self.sendCommand (Command.REMOVE_NODE)
            self.sendCommand (Command.NODE)
            self.sendData (pickle.dumps (node))
            success = True
        except socket.error:
            success = False
            self.connection = None

        self.connectionLock.release ()
        return success
