from common.entity.entities import Command, Node, NodeState, Type

import json
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
    def recvData (connection, delimiter = "\n"):

        data = ""
        byte = connection.recv (1).decode("utf-8")
        while byte != "\n":
            data = data + byte
            byte = connection.recv (1).decode("utf-8")

        return data

    @staticmethod
    def recvNode (connection):

        nodeDict = json.loads (CommandInterface.recvData (connection))
        typeDict = nodeDict ["type"]
        return Node (name = nodeDict ["name"], ip = nodeDict ["ip"], state = nodeDict ["state"], sector = nodeDict ["sector"], \
                     typeNode = Type (name = typeDict ["name"], color = typeDict ["color"], description = typeDict ["description"]))

    @staticmethod
    def recvType (connection):
        typeDict = json.loads (CommandInterface.recvData (connection))
        return Type (name = typeDict ["name"], color = typeDict ["color"], description = typeDict ["description"])

    @staticmethod
    def sendCommand (connection, command = Command.EXIT):
        return connection.send (struct.pack ("!i", command))

    @staticmethod
    def sendData (connection, data, delimiter = "\n"):
        return connection.send (bytearray (data + delimiter, encoding = "utf-8"))

    def process (self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = CommandInterface.recvCommand (connection)

                if command == Command.GET_TYPES:
                    types = self.controller.fetchTypes ()

                    for t in types:
                        serializedType = json.dumps (t.__dict__ ())
                        CommandInterface.sendCommand (connection, Command.TYPE)
                        CommandInterface.sendData (connection, serializedType)

                    CommandInterface.sendCommand (connection, Command.END)

                if command == Command.APPEND_TYPE:
                    newType = CommandInterface.recvType (connection)
                    self.controller.appendType (newType)

                if command == Command.REMOVE_TYPE:
                    typeName = CommandInterface.recvData (connection)
                    self.controller.removeType (typeName)

                if command == Command.GET_REG_NODES_SECTOR or command == Command.GET_UNREG_NODES_SECTOR:
                    sector = CommandInterface.recvData (connection)

                    if command == Command.GET_REG_NODES_SECTOR:
                        nodes = self.controller.getRegisteredNodesFromSector (sector)
                    else:
                        nodes = self.controller.getUnregisteredNodesFromSector (sector)

                    for node in nodes:
                        serializedNode = json.dumps (node.__dict__ ())
                        CommandInterface.sendCommand (connection, Command.NODE)
                        CommandInterface.sendData (connection, serializedNode)

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

            except Exception as e:
                print ("Lost connection with host " + addr [0])
                print (e)
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
