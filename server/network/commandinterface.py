import logging
import socket
import struct
import threading

from common.entity.entities import Command
from common.entity.metadata import Singleton
from common.network.utils import NetUtils
from server.control.controller import ServerController
from server.network.db import DataNotFoundError, DifferentSectorNodeError


class ServerCommandInterface(metaclass=Singleton):
    """
    The server's interface with the clients.
    """

    def __init__(self, comm_interface_port):
        """
        Creates a new instance.
        :param comm_interface_port: the port to be used.
        """

        self.controller = ServerController.get_instance()
        self.port = comm_interface_port

        self.interfaceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interfaceSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.logger = logging.getLogger('ServerCommandInterface')

        self.socket_list = []

        self.listening = True
        self.listenThread = threading.Thread(target=self.listen)
        self.listenThread.start()

    def process(self, connection, client_address):
        """
        Every time a client connects to the server, a new thread is launched to handle the communication.
        Communication protocol rules:
            (i) a client sends a command.
            (ii) if client needs to send one or many nodes or types:
                (ii-a) client sends a command Command.NODE or Command.TYPE.
                (ii-b) client sends a node or type instance.
            (iii) server answers with Command.OK if the command succeeds or
                  Command.FAILURE followed by a message, otherwise.

        :param connection: communication socket
        :param client_address: the client's IP address
        """

        self.logger.info("Initializing communication with client {}".format(client_address))

        connection_alive = True

        while connection_alive and self.listening:

            try:
                # First 4 bytes are the command id
                command = NetUtils.recv_command(connection)

                # Prevent some commands to be printed in order to avoid big log files.
                if Command.is_loggable(command):
                    self.logger.info("Command {} received from {}".format(Command.command_name(command),
                                                                          client_address))

                if command == Command.GET_TYPES:

                    types = self.controller.fetch_types()

                    for t in types:
                        NetUtils.send_command(connection, Command.TYPE)
                        NetUtils.send_object(connection, t)

                    NetUtils.send_command(connection, Command.OK)

                elif command == Command.APPEND_TYPE:
    
                    if NetUtils.recv_command(connection) == Command.TYPE:

                        new_type = NetUtils.recv_object(connection)
                        if self.controller.append_type(new_type):
                            self.logger.info("{} appended or updated successfully".format(new_type))
                            NetUtils.send_command(connection, Command.OK)
                        else:
                            error_message = "{} has not been added or updated.".format(new_type)
                            self.logger.error(error_message)
                            NetUtils.send_command(connection, Command.FAILURE)
                            NetUtils.send_object(connection, error_message)

                elif command == Command.REMOVE_TYPE:

                    if NetUtils.recv_command(connection) == Command.TYPE:

                        type_name = NetUtils.recv_object(connection)
                        removed_count = self.controller.remove_type(type_name)
                        if removed_count > 0:
                            self.logger.info("{} entry(ies) of {} removed.".format(removed_count, type_name))
                            NetUtils.send_command(connection, Command.OK)
                        else:
                            error_message = "No {} entry was removed from database.".format(type_name)
                            self.logger.info(error_message)
                            NetUtils.send_failure(connection, error_message)

                elif command == Command.GET_REG_NODES_SECTOR or command == Command.GET_UNREG_NODES_SECTOR:

                    sector = NetUtils.recv_object(connection)

                    if command == Command.GET_REG_NODES_SECTOR:
                        nodes = self.controller.get_nodes_from_sector(sector)
                    else:
                        nodes = self.controller.get_nodes_from_sector(sector, registered=False)

                    for node in nodes:
                        NetUtils.send_command(connection, Command.NODE)
                        NetUtils.send_object(connection, node)

                    NetUtils.send_command(connection, Command.OK)

                elif command == Command.GET_REG_NODE_BY_IP:

                    ip_address = NetUtils.recv_object(connection)

                    try:
                        node = self.controller.get_node_by_address(ipAddress=ip_address)
                        NetUtils.send_command(connection, Command.NODE)
                        NetUtils.send_object(connection, node)
                        NetUtils.send_command(connection, Command.OK)
                    except DataNotFoundError:
                        error_message = "No node whose IP address is {} has been found.".format(ip_address)
                        self.logger.exception(error_message)
                        NetUtils.send_failure(connection, error_message)

                elif command == Command.APPEND_NODE:

                    if NetUtils.recv_command(connection) == Command.NODE:
                        new_node = NetUtils.recv_object(connection)

                        try:
                            if self.controller.append_node(new_node):
                                NetUtils.send_command(connection, Command.OK)
                                self.logger.info('{} appended or updated successfully'.format(new_node))
                            else:
                                error_message = "{} has not been added or updated.".format(new_node)
                                self.logger.exception(error_message)
                                NetUtils.send_failure(connection, error_message)

                        except DifferentSectorNodeError as error:
                            error_message = str(error)
                            self.logger.exception(error_message)
                            NetUtils.send_failure(connection, error_message)

                elif command == Command.REMOVE_NODE:

                    if NetUtils.recv_command(connection) == Command.NODE:
                        node = NetUtils.recv_object(connection)
                        removed_count = self.controller.remove_node_from_sector(node)

                        if removed_count > 0:
                            self.logger.info("{} entry(ies) of {} removed.".format(removed_count, node))
                            NetUtils.send_command(connection, Command.OK)
                        else:
                            error_message = "No {} entry was removed from database.".format(node)
                            self.logger.info(error_message)
                            NetUtils.send_failure(connection, error_message)

                elif command == Command.SWITCH:

                    registered_node = None
                    un_registered_node = None

                    if NetUtils.recv_command(connection) == Command.NODE:
                        registered_node = NetUtils.recv_object(connection)

                    if NetUtils.recv_command(connection) == Command.NODE:
                        un_registered_node = NetUtils.recv_object(connection)

                    if registered_node is not None and un_registered_node is not None:
                        self.controller.update_node(un_registered_node, registered_node)
                        self.logger.info("Switching node {}'s configuration to {}".format(registered_node,
                                                                                          un_registered_node))
                        NetUtils.send_command(connection, Command.OK)
                    else:
                        error_message = "Error while receiving one of the nodes."
                        self.logger.error(error_message)
                        NetUtils.send_failure(connection, error_message)

                elif command == Command.REBOOT:
                    if NetUtils.recv_command(connection) == Command.NODE:
                        registered_node = NetUtils.recv_object(connection)
                        self.logger.info("Requesting node {} to reboot".format(registered_node))
                        self.controller.reboot_node(registered_node)

                elif command == Command.SET_HOSTNAME:
                    if NetUtils.recv_command(connection) == Command.NODE:
                        registered_node = NetUtils.recv_object(connection)
                        self.logger.info("Requesting node {} to reboot".format(registered_node))
                        self.controller.reboot_node(registered_node)

                elif command == Command.SET_IP:
                    if NetUtils.recv_command(connection) == Command.NODE:
                        registered_node = NetUtils.recv_object(connection)
                        self.logger.info("Requesting node {} to reboot".format(registered_node))
                        self.controller.reboot_node(registered_node)

                elif command == Command.EXIT:
                    self.listening = False

            except (socket.error, struct.error):
                self.logger.exception("Lost connection with host {}.".format(client_address[0]))
                connection_alive = False

        connection.close()

        if connection in self.socket_list:
            self.socket_list.remove(connection)

        self.logger.info("Closing communication with client {}".format(client_address))

    def listen(self):
        """
        Listens to client connections and command requests.
        """

        try:
            self.interfaceSocket.bind(("0.0.0.0", self.port))
            self.interfaceSocket.listen(255)

            while self.listening:
                connection, client_address = self.interfaceSocket.accept()
                self.socket_list.append(connection)
                request_thread = threading.Thread(target=self.process, args=[connection, client_address])
                request_thread.start()

            self.interfaceSocket.close()
        except socket.error:
            self.logger.exception("Error in communication.")

        self.logger.info('Interface for listening commands is closed.')

    def stop_all(self):
        """
        Stops all threads and sockets
        """
        self.listening = False

        self.interfaceSocket.shutdown(socket.SHUT_RDWR)
        for s in self.socket_list:
            s.shutdown(socket.SHUT_RDWR)
