import socket
import struct
import threading

from common.entity.entities import Command
from common.entity.metadata import Singleton
from common.network.utils import NetUtils
from server.control.controller import ServerController


class ServerCommandInterface(metaclass=Singleton):

    def __init__(self, comm_interface_port):

        self.controller = ServerController.get_instance()
        self.port = comm_interface_port

        self.interfaceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interfaceSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listening = True
        self.listenThread = threading.Thread(target=self.listen)
        self.listenThread.start()

    def process(self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = NetUtils.recv_command(connection)
                # print(command)

                if command == Command.GET_TYPES:

                    types = self.controller.fetch_types()

                    for t in types:
                        NetUtils.send_command(connection, Command.TYPE)
                        NetUtils.send_object(connection, t)

                    NetUtils.send_command(connection, Command.END)

                elif command == Command.APPEND_TYPE:
                    t = NetUtils.recv_command(connection)
                    print(t)
                    newType = NetUtils.recv_object(connection)
                    self.controller.manage_types(newType)
                    print(newType)

                elif command == Command.REMOVE_TYPE:
                    typeName = NetUtils.recv_object(connection)
                    print(typeName)
                    self.controller.remove_type_by_name(typeName)

                elif command == Command.GET_REG_NODES_SECTOR or command == Command.GET_UNREG_NODES_SECTOR:
                    sector = NetUtils.recv_object(connection)

                    if command == Command.GET_REG_NODES_SECTOR:
                        nodes = self.controller.get_registered_nodes_from_sector(sector)
                    else:
                        nodes = self.controller.get_unregistered_nodes_from_sector(sector)

                    for node in nodes:
                        NetUtils.send_command(connection, Command.NODE)
                        NetUtils.send_object(connection, node)

                    NetUtils.send_command(connection, Command.END)

                elif command == Command.GET_REG_NODE_BY_IP:

                    ip_addr = NetUtils.recv_object(connection)
                    node = self.controller.get_node_by_address(ipAddress=ip_addr)
                    NetUtils.send_command(connection, node)

                elif command == Command.APPEND_NODE:
                    newNode = NetUtils.recv_object(connection)
                    self.controller.manage_nodes(newNode)
                    print('Append Node')

                elif command == Command.REMOVE_NODE:
                    NetUtils.recv_command(connection)
                    self.controller.remove_node_from_sector(NetUtils.recv_object(connection))
                    print('Remove Node')

                elif command == Command.SWITCH:
                    registeredNode = NetUtils.recv_object(connection)
                    unRegisteredNode = NetUtils.recv_object(connection)
                    self.controller.update_node(unRegisteredNode, registeredNode)
                    print("Trocar " + str(registeredNode) + " por " + str(unRegisteredNode))

                elif command == Command.REBOOT:
                    registeredNode = NetUtils.recv_object(connection)
                    self.controller.reboot_node(registeredNode)

                elif command == Command.EXIT:
                    print("Exiting")
                    return

            except Exception as e:
                print("Lost connection with host " + addr[0])
                print("{}".format(e))
                connectionAlive = False

        connection.close()

    def listen(self):
        try:
            self.interfaceSocket.bind(("0.0.0.0", self.port))
            self.interfaceSocket.listen(255)

            while self.listening:
                connection, addr = self.interfaceSocket.accept()
                requestThread = threading.Thread(target=self.process, args=[connection, addr])
                requestThread.start()

            self.interfaceSocket.close()
        except Exception as e:
            print('{}'.format(e))
        print('InterfaceSocket Closed')

    def stopAll(self):
        self.listening = False

        # In order to close the socket and exit from the accept () function, emulate a new connection
        self.shutdownSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.shutdownSocket.connect(("0.0.0.0", self.port))
        self.shutdownSocket.send(struct.pack("!i", Command.EXIT))
        self.shutdownSocket.close()
        print('ShutdownSocket ...')
