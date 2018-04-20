from common.entity.entities import Command, Node, NodeState, Type

import pickle
import socket
import struct
import threading

class CommandInterface ():

    def __init__ (self, serverBindPort = 6789, controller = None):

        self.controller = controller

        self.port = serverBindPort

        self.interfaceSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.interfaceSocket.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listenThread = threading.Thread (target = self.listen)
        self.listening = True
        self.listenThread.start ()

    @staticmethod
    def recvCommand (connection):
        return struct.unpack ("!i", connection.recv(4)) [0]

    @staticmethod
    def recvData (connection):
        dataSize = struct.unpack ("!i", connection.recv(4)) [0]
        return connection.recv (dataSize)

    @staticmethod
    def recvNode (connection):
        return pickle.loads (CommandInterface.recvData (connection))

    @staticmethod
    def recvType (connection):
        return pickle.loads (CommandInterface.recvData (connection))

    @staticmethod
    def sendCommand (connection, command = Command.EXIT):
        return connection.send (struct.pack ("!i", command))

    @staticmethod
    def sendData (connection, data):
        connection.send (struct.pack ("!i", len(data)))
        connection.send (data)

    def process (self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = CommandInterface.recvCommand (connection)

                if command == Command.GET_TYPES:

                    types = self.controller.fetchTypes ()

                    for t in types:
                        CommandInterface.sendCommand (connection, Command.TYPE)
                        CommandInterface.sendData (connection, pickle.dumps (t))

                    CommandInterface.sendCommand (connection, Command.END)

                if command == Command.APPEND_TYPE:
                    newType = CommandInterface.recvType (connection)
                    self.controller.appendType (newType)

                if command == Command.REMOVE_TYPE:
                    typeName = pickle.loads (CommandInterface.recvData (connection))
                    print (typeName)
                    self.controller.removeType (typeName)

                if command == Command.GET_REG_NODES_SECTOR or command == Command.GET_UNREG_NODES_SECTOR:
                    sector = pickle.loads (CommandInterface.recvData (connection))

                    if command == Command.GET_REG_NODES_SECTOR:
                        nodes = self.controller.getRegisteredNodesFromSector (sector)
                    else:
                        nodes = self.controller.getUnregisteredNodesFromSector (sector)

                    for node in nodes:
                        CommandInterface.sendCommand (connection, Command.NODE)
                        CommandInterface.sendData (connection, pickle.dumps (node))

                    CommandInterface.sendCommand (connection, Command.END)

                if command == Command.APPEND_NODE:
                    newNode = CommandInterface.recvNode (connection)
                    self.controller.appendNode (newNode)

                if command == Command.REMOVE_NODE:
                    CommandInterface.recvCommand (connection)
                    self.controller.removeNodeFromSector (CommandInterface.recvNode (connection))

                if command == Command.EXIT:
                    print ("Exiting")
                    return

            except socket.error:
                print ("Lost connection with host " + addr [0])
                connectionAlive = False

        connection.close ()

    def listen (self):

        self.interfaceSocket.bind (("0.0.0.0", self.port))
        self.interfaceSocket.listen (255)

        while self.listening:

            connection, addr = self.interfaceSocket.accept ()
            print ("dasdas23123123123")
            requestThread = threading.Thread (target = self.process, args = [connection, addr])
            requestThread.start ()

        self.interfaceSocket.close ()

    def stopAll (self):

        self.listening = False

        # In order to close the socket and exit from the accept () function, emulate a new connection
        self.shutdownSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.shutdownSocket.connect (("0.0.0.0", self.port))
        self.shutdownSocket.send (struct.pack ("!i", Command.EXIT))
        self.shutdownSocket.close ()
