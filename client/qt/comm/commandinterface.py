import logging
import socket
import threading

from common.entity.entities import Command, Type, Node
from common.entity.metadata import Singleton
from common.network.utils import NetUtils


class CommandFailureReceivedError(Exception):
    """
    A simple exception to represent command failures.
    """
    pass


class CommandNetworkInterface(metaclass=Singleton):

    """
    A class to implement the communication between client and server.
    """

    def __init__(self, server_address: str, server_port: int):
        """
        Constructor method. Receives server's parameters.
        :param server_address: server's IP address.
        :param server_port: server's listening port.
        """

        self.server_address = server_address
        self.port = server_port

        self.interface_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interface_socket.settimeout(10)

        self.logger = logging.getLogger('CommandNetworkInterface')

        self.connection_lock = threading.Lock()
        self.connection = False
        self.connection = self.connect()

    def release_mutex(self):
        """
        Releases the connection lock.
        """
        self.connection_lock.release()

    def connect(self, attempts=1):
        """
        Attempts to connect to the server.
        :return: True if this client is connected to the server. False, otherwise.
        """

        if not self.connection:
            self.connection_lock.acquire()
            while attempts > 0:
                try:
                    self.logger.info('Attempt #{} to connect to {}:{}'.format(attempts, self.server_address, self.port))
                    self.interface_socket.connect((self.server_address, self.port))
                    self.logger.info("Connection established to {}:{}".format(self.server_address, self.port))
                    self.connection_lock.release()
                    return True
                except socket.error as e:
                    self.logger.exception('Exception while trying to connect to the server')
                    attempts = attempts - 1

            self.connection_lock.release()
            self.logger.error('Could not connect to the server. Number of attempts reached.')
            return False

        return True

    def switch(self, registered_node, unregistered_node):
        """
        Copies the current configuration of a disconnected registered node to a connected unregistered node.
        :param registered_node: Node object representing the registered node.
        :param unregistered_node: Node object representing the registered node.
        :return: False if a socket.error exception is caught and True, otherwise.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """
        self.connection = self.connect()
        if not self.connection:
            return False

        self.connection_lock.acquire()

        success = True

        try:
            NetUtils.send_command(self.interface_socket, Command.SWITCH)

            NetUtils.send_command(self.interface_socket, Command.NODE)
            NetUtils.send_object(self.interface_socket, registered_node)

            NetUtils.send_command(self.interface_socket, Command.NODE)
            NetUtils.send_object(self.interface_socket, unregistered_node)

            if NetUtils.recv_command(self.interface_socket) == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            self.connection = False
            success = False

        self.connection_lock.release()
        return success

    def reboot(self, registered_node):
        """
        Reboots a registered node.
        :param registered_node: Node object representing a connected and registered node.
        :return: False if a socket.error exception is caught and True, otherwise.
        """
        self.connection = self.connect()
        if not self.connection:
            return False

        self.connection_lock.acquire()

        success = True

        try:
            NetUtils.send_command(self.interface_socket, Command.REBOOT)
            NetUtils.send_object(self.interface_socket, registered_node)
        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            self.connection = False
            success = False

        self.connection_lock.release()
        return success

    def append_type(self, new_type: Type):
        """
        Appends a new type into the database.
        :param new_type:  the type to be appended.
        :return: True if no exception has been throw. False otherwise.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """

        self.connection = self.connect()
        if not self.connection:
            return False

        self.connection_lock.acquire()

        success = True

        try:
            NetUtils.send_command(self.interface_socket, Command.APPEND_TYPE)
            NetUtils.send_command(self.interface_socket, Command.TYPE)
            NetUtils.send_object(self.interface_socket, new_type)

            if NetUtils.recv_command(self.interface_socket) == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            self.connection = False
            success = False

        self.connection_lock.release()

        return success

    def remove_type(self, type_name):
        """
        Removes a type from the database.
        :param type_name: the type to be removed.
        :return: True if no exception has been throw. False otherwise.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """

        self.connection = self.connect()
        if not self.connection:
            return False

        self.connection_lock.acquire()

        success = True

        try:
            NetUtils.send_command(self.interface_socket, Command.REMOVE_TYPE)
            NetUtils.send_command(self.interface_socket, Command.TYPE)
            NetUtils.send_object(self.interface_socket, type_name)

            if NetUtils.recv_command(self.interface_socket) == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            self.connection = False
            success = False

        self.connection_lock.release()

        return success

    def fetch_types(self):
        """
        Fetches all types saved in the database.
        :return: a list of Type objects.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """
        self.connection = self.connect()
        if not self.connection:
            return []

        self.connection_lock.acquire()

        types = []

        try:
            NetUtils.send_command(self.interface_socket, Command.GET_TYPES)
            command = NetUtils.recv_command(self.interface_socket)
            while command != Command.OK and command != Command.FAILURE:
                if command == Command.TYPE:
                    types.append(NetUtils.recv_object(self.interface_socket))

                command = NetUtils.recv_command(self.interface_socket)

            if command == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            self.connection = False
            types = []

        self.connection_lock.release()
        return types

    def get_nodes_from_sector(self, sector, registered=True):
        """
        Gets all (registered/unregisted) nodes from a given sector.
        :param sector: the sector to fetch nodes from.
        :param registered: True if the method must return the nodes that were registered by system managers. False
        for the nodes that were dynamically verified.
        :return: a list of Node objects.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """
        self.connection = self.connect()
        if not self.connection:
            return []

        self.connection_lock.acquire()

        try:
            if registered:
                NetUtils.send_command(self.interface_socket, Command.GET_REG_NODES_SECTOR)
            else:
                NetUtils.send_command(self.interface_socket, Command.GET_UNREG_NODES_SECTOR)

            NetUtils.send_object(self.interface_socket, sector)

            nodes = []
            command = NetUtils.recv_command(self.interface_socket)
            while command != Command.OK and command != Command.FAILURE:
                if command == Command.NODE:
                    nodes.append(NetUtils.recv_object(self.interface_socket))

                command = NetUtils.recv_command(self.interface_socket)

            if command == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            nodes = []
            self.connection = False

        self.connection_lock.release()
        return nodes

    def append_node(self, node: Node):
        """
        Append a new node to the database.
        :param node: the Node object to be appended into the database.
        :return: True if no exception has been throw. False otherwise.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """
        self.connection = self.connect()
        if not self.connection:
            return False

        self.connection_lock.acquire()

        success = True

        try:
            NetUtils.send_command(self.interface_socket, Command.APPEND_NODE)
            NetUtils.send_command(self.interface_socket, Command.NODE)
            NetUtils.send_object(self.interface_socket, node)

            if NetUtils.recv_command(self.interface_socket) == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            self.connection = False
            success = False

        self.connection_lock.release()

        return success

    def remove_node_from_sector(self, node: Node):
        """
        Removes a node from a given sector.
        :param node: the node to be removed.
        :return: True if no exception has been throw. False otherwise.
        :raise CommandFailureReceivedError: a Failure command was returned by the server.
        """
        self.connection = self.connect()
        if not self.connection:
            return False

        self.connection_lock.acquire()

        success = True

        try:
            NetUtils.send_command(self.interface_socket, Command.REMOVE_NODE)
            NetUtils.send_command(self.interface_socket, Command.NODE)
            NetUtils.send_object(self.interface_socket, node)

            if NetUtils.recv_command(self.interface_socket) == Command.FAILURE:
                self.connection_lock.release()
                raise CommandFailureReceivedError(NetUtils.recv_object(self.interface_socket))

        except socket.error:
            self.logger.exception('Error while sending commands to the server.')
            success = False
            self.connection = False

        self.connection_lock.release()
        return success
