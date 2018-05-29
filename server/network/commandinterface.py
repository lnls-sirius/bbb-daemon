import socket
import threading

from common.entity.entities import Command
from common.network.utils import NetUtils
from control.controller import MonitorController


class CommandInterface():

    def __init__(self, comInterfacePort=6789, controller: MonitorController = None):

        self.controller = controller
        self.port = comInterfacePort

        self.interfaceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interfaceSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listenThread = threading.Thread(target=self.listen)
        self.listening = True
        self.listenThread.start()

    def process(self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = NetUtils.recvCommand(connection)
                #print(command)

                if command == Command.GET_TYPES:

                    types = self.controller.fetchTypes()

                    for t in types:
                        NetUtils.sendCommand(connection, Command.TYPE)
                        NetUtils.sendObject(connection, t)

                    NetUtils.sendCommand(connection, Command.END)

                if command == Command.APPEND_TYPE:
                    t = NetUtils.recvCommand(connection)
                    print(t)
                    newType = NetUtils.recvObject(connection)
                    self.controller.appendType(newType)
                    print(newType)

                if command == Command.REMOVE_TYPE:
                    typeName = NetUtils.recvObject(connection)
                    print(typeName)
                    self.controller.removeType(typeName)

                if command == Command.GET_REG_NODES_SECTOR or command == Command.GET_UNREG_NODES_SECTOR:
                    sector = NetUtils.recvObject(connection)

                    if command == Command.GET_REG_NODES_SECTOR:
                        nodes = self.controller.getRegisteredNodesFromSector(sector)
                    else:
                        nodes = self.controller.getUnregisteredNodesFromSector(sector)

                    for node in nodes:
                        NetUtils.sendCommand(connection, Command.NODE)
                        NetUtils.sendObject(connection, node)

                    NetUtils.sendCommand(connection, Command.END)

                if command == Command.APPEND_NODE:
                    newNode = NetUtils.recvObject(connection)
                    self.controller.appendNode(newNode)

                if command == Command.REMOVE_NODE:
                    NetUtils.recvCommand(connection)
                    self.controller.removeNodeFromSector(NetUtils.recvObject(connection))

                if command == Command.SWITCH:
                    registeredNode = NetUtils.recvObject(connection)
                    unRegisteredNode = NetUtils.recvObject(connection)
                    self.controller.updateNode(unRegisteredNode, registeredNode)
                    print("Trocar " + str(registeredNode) + " por " + str(unRegisteredNode))

                if command == Command.REBOOT:
                    registeredNode = NetUtils.recvObject(connection)
                    self.controller.rebootNode(registeredNode)

                if command == Command.EXIT:
                    print("Exiting")
                    return

            except Exception as e:
                print("Lost connection with host " + addr[0])
                #print("{}".format(e))
                connectionAlive = False

        connection.close()

    def listen(self):

        self.interfaceSocket.bind(("0.0.0.0", self.port))
        self.interfaceSocket.listen(255)

        while self.listening:
            connection, addr = self.interfaceSocket.accept()
            requestThread = threading.Thread(target=self.process, args=[connection, addr])
            requestThread.start()

        self.interfaceSocket.close()

    def stopAll(self):
        self.listening = False

        # In order to close the socket and exit from the accept () function, emulate a new connection
        self.shutdownSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.shutdownSocket.connect(("0.0.0.0", self.port))
        NetUtils.sendCommand(self.shutdownSocket, Command.EXIT)
        self.shutdownSocket.close()
