import socket
import threading
import traceback

from common.entity.entities import Command
from common.network.utils import NetUtils

class CommandInterface():

    def __init__(self, serverAddress="localhost", serverPort=6789):

        self.serverAddress = serverAddress
        self.port = serverPort

        self.interfaceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interfaceSocket.settimeout(10)

        self.connectionLock = threading.Lock()
        self.connection = False
        self.connection = self.connect()

    def connect(self):

        if not self.connection:
            self.connectionLock.acquire()
            attempts = 1
            while attempts > 0:
                try:
                    print(self.serverAddress + " " + str(self.port))
                    self.interfaceSocket.connect((self.serverAddress, self.port))
                    print("connection established")
                    self.connectionLock.release()
                    return True
                except socket.error:
                    traceback.print_exc()
                    attempts = attempts - 1

            self.connectionLock.release()
            return False

        return True

    def switch(self, registeredNode, unregisteredNode):

        if not self.connection:
            return False

        self.connectionLock.acquire()

        try:
            NetUtils.sendCommand(self.interfaceSocket, Command.SWITCH)
            NetUtils.sendObject(self.interfaceSocket, registeredNode)
            NetUtils.sendObject(self.interfaceSocket, unregisteredNode)
        except socket.error:
            self.connection = False

        self.connectionLock.release()

    def reboot(self, registeredNode):

        if not self.connection:
            return False

        self.connectionLock.acquire()

        try:
            NetUtils.sendCommand(self.interfaceSocket, Command.REBOOT)
            NetUtils.sendObject(self.interfaceSocket, registeredNode)
        except socket.error:
            self.connection = False

        self.connectionLock.release()

    def appendType(self, newType):

        if not self.connection:
            return False

        self.connectionLock.acquire()

        try:
            NetUtils.sendCommand(self.interfaceSocket, Command.APPEND_TYPE)
            NetUtils.sendCommand(self.interfaceSocket, Command.TYPE)
            NetUtils.sendObject(self.interfaceSocket, newType)
            success = True
        except socket.error:
            self.connection = False
            success = False

        self.connectionLock.release()

        return success

    def removeType(self, typeName):

        if not self.connection:
            return []

        self.connectionLock.acquire()

        try:
            NetUtils.sendCommand(self.interfaceSocket, Command.REMOVE_TYPE)
            NetUtils.sendObject(self.interfaceSocket, typeName)
        except socket.error:
            self.connection = False

        self.connectionLock.release()

    def fetchTypes(self):

        if not self.connection:
            return []

        self.connectionLock.acquire()

        try:
            types = []
            NetUtils.sendCommand(self.interfaceSocket, Command.GET_TYPES)
            command = NetUtils.recvCommand(self.interfaceSocket)
            while command != Command.END:
                if command == Command.TYPE:
                    types.append(NetUtils.recvObject(self.interfaceSocket))

                command = NetUtils.recvCommand(self.interfaceSocket)
        except socket.error:
            types = []
            self.connection = False

        self.connectionLock.release()
        return types

    def getNodesFromSector(self, sector, registered=True):

        if not self.connection:
            return []

        self.connectionLock.acquire()

        try:
            if registered:
                NetUtils.sendCommand(self.interfaceSocket, Command.GET_REG_NODES_SECTOR)
            else:
                NetUtils.sendCommand(self.interfaceSocket, Command.GET_UNREG_NODES_SECTOR)

            NetUtils.sendObject(self.interfaceSocket, sector)

            nodes = []
            command = NetUtils.recvCommand(self.interfaceSocket)
            while command != Command.END:
                if command == Command.NODE:
                    nodes.append(NetUtils.recvObject(self.interfaceSocket))

                command = NetUtils.recvCommand(self.interfaceSocket)
        except socket.error:
            nodes = []
            self.connection = False

        self.connectionLock.release()
        return nodes

    def appendNode(self, node):

        if not self.connection:
            return False

        self.connectionLock.acquire()

        try:
            NetUtils.sendCommand(self.interfaceSocket, Command.APPEND_NODE)
            NetUtils.sendObject(self.interfaceSocket, node)
            success = True
        except socket.error:
            success = False
            self.connection = False

        self.connectionLock.release()

        return success

    def removeNodeFromSector(self, node):

        if not self.connection:
            return False

        self.connectionLock.acquire()

        try:
            NetUtils.sendCommand(self.interfaceSocket, Command.REMOVE_NODE)
            NetUtils.sendCommand(self.interfaceSocket, Command.NODE)
            NetUtils.sendObject(self.interfaceSocket, node)
            success = True
        except socket.error:
            success = False
            self.connection = False

        self.connectionLock.release()
        return success
