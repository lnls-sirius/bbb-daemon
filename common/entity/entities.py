"""
This module contains all entity classes of the project.
"""

import ast
import ipaddress
import json
import copy


class Command:
    """
    A simple class to wrap command codes.
    """

    PING, REBOOT, EXIT, END, TYPE, APPEND_TYPE, REMOVE_TYPE, NODE, APPEND_NODE, REMOVE_NODE, SWITCH, \
    GET_TYPES, GET_UNREG_NODES_SECTOR, GET_REG_NODES_SECTOR, GET_REG_NODE_BY_IP, OK, FAILURE, SET_IP, SET_HOSTNAME= range(19)

    @staticmethod
    def command_name(command):
        """
        Returns the name of a command.
        :param command: a command id.
        :return: a given command's name.
        """
        for key in Command.__dict__.keys():
            if Command.__dict__[key] == command:
                return key

    @staticmethod
    def is_loggable(command):
        """
        Checks if a given command should appear in logs.
        :param command: a command id.
        :return: True if command should be appear in logs and False, otherwise.
        """
        return command not in [Command.GET_TYPES, Command.GET_UNREG_NODES_SECTOR,
                               Command.GET_REG_NODES_SECTOR, Command.GET_REG_NODE_BY_IP,
                               Command.OK, Command.FAILURE, Command.SET_IP,Command.SET_HOSTNAME]


class SectorNotFoundError(Exception):
    """
    A simple exception class to represent sector errors.
    """
    pass


class Sector:
    """
    A static class providing helper functions to manage sectors.
    """
    SECTORS = [str(i) for i in range(1, 21)] + ["Conectividade", "LINAC", "RF", "Fontes", "Outros"]
    # See https://wiki-sirius.lnls.br/mediawiki/index.php/CON:Sirius_control_system_network#Subnetwork_Division
    SUBNETS = [[ipaddress.ip_network(u'10.128.10.0/25'), ipaddress.ip_network(u'10.128.10.128/25')]] + \
              [ipaddress.ip_network(u'10.128.{}.0/24'.format(i * 10)) for i in range(2, 20)] + \
              [[ipaddress.ip_network(u'10.128.200.0/25'), ipaddress.ip_network(u'10.128.200.128/25')]] + \
              [ipaddress.ip_network(u'10.128.0.0/24'),
               [ipaddress.ip_network(u'10.128.1.0/25'), ipaddress.ip_network(u'10.128.1.128/25')],
               [ipaddress.ip_network(u'10.128.25.0/26'), ipaddress.ip_network(u'10.128.25.64/26'),
                ipaddress.ip_network(u'10.128.25.128/25')],
               [ipaddress.ip_network(u'10.128.75.0/27'), ipaddress.ip_network(u'10.128.75.32/27'),
                ipaddress.ip_network(u'10.128.75.64/27'), ipaddress.ip_network(u'10.128.75.128/27'),
                ipaddress.ip_network(u'10.128.75.160/27')], ipaddress.ip_network(u'0.0.0.0/0')]

    @staticmethod
    def subnets():
        return Sector.SUBNETS

    @staticmethod
    def sectors():
        return Sector.SECTORS

    @staticmethod
    def get_sector_by_ip_address(ip_address=None):
        """
        Returns the sector of a node based on its IP address.
        :param ip_address: the IP address of a host.
        :return: the sector that contains the given IP address.
        :raise SectorNotFoundError: IP address is not contained in any sub-network.
        """
        for idx, subnet in enumerate(Sector.SUBNETS):
            if type(subnet) is list:
                for s in subnet:
                    if ip_address in s.hosts():
                        return Sector.SECTORS[idx]
            elif ip_address in subnet.hosts():
                return Sector.SECTORS[idx]

        return Sector.SECTORS[-1]

    @staticmethod
    def get_default_gateway_of_address(ip_address=None):
        """
        Returns the default gateway of a node based on its IP address.
        :param ip_address: the IP address of a host.
        :return: the default gateway of that host. An ipaddress.IPv4Address object.
        :raise SectorNotFoundError: IP address is not contained in any sub-network.
        """
        for subnet in Sector.SUBNETS:
            if type(subnet) is list:
                for s in subnet:
                    if ip_address in s.hosts():
                        return s.network_address + 1
            elif ip_address in subnet.hosts():
                return subnet.network_address + 1

        return Sector.SUBNETS[-1].network_address + 1

    @staticmethod
    def get_network_address_from_ip_address(ip_address):
        ip_interface = ipaddress.ip_interface(ip_address)
        return ipaddress.ip_network(ip_interface, strict=False)


class NodeState:
    """
    Valid states for any host in the Controls Group network.
    """

    DISCONNECTED, MIS_CONFIGURED, CONNECTED, REBOOTING = range(4)

    @staticmethod
    def to_string(state):
        """
        :param state: the state to be converted to string.
        :return: string representation of a state.
        """

        if state == NodeState.DISCONNECTED:
            return "Disconnected"

        elif state == NodeState.CONNECTED:
            return "Connected"

        elif state == NodeState.MIS_CONFIGURED:
            return "Mis-configured"

        elif state == NodeState.REBOOTING:
            return "Rebooting"

        return "Unknown state"


class BaseRedisEntity:
    """
    A base abstract class for all entries stored in the Redis db. Classes implementing it should provide at least
    three methods: to_set, from_set and get_key.
    """

    KEY_PREFIX = 'BaseRedisEntity:'
    KEY_PREFIX_LEN = len(KEY_PREFIX)

    def to_set(self):
        """
        Returns a set representation of the object.
        :raise NotImplementedError: empty method.
        """
        raise NotImplementedError("Provide an implementation for BaseRedisEntity class")

    def from_set(self, **kwargs):
        """
        Returns a BaseRedisEntity object from a string representation of dictionary queried from the Redis db.
        :param str_dic: python's string representation of the dictionary.
        :raise NotImplementedError: empty method.
        """
        raise NotImplementedError("Provide an implementation for BaseRedisEntity class")

    def get_key(self):
        """
        Gets the key used on redis.
        :return: id for redis.
        :raise NotImplementedError: empty method.
        """
        raise NotImplementedError("Provide an implementation for BaseRedisEntity class")

    @staticmethod
    def get_name_from_key(key):
        """
        Removes the prefix from the key.
        :param key: A Redis key.
        :return: The key without prefix.
        """
        if len(key) <= BaseRedisEntity.KEY_PREFIX_LEN:
            return ''

        return key[BaseRedisEntity.KEY_PREFIX_LEN:]


class Type(BaseRedisEntity):
    """
    This class provides a wrapper for host types.
    """

    KEY_PREFIX = 'Type:'
    KEY_PREFIX_LEN = len(KEY_PREFIX)

    UNDEFINED, POWER_SUPPLY, COUNTING_PRU, SERIAL_THERMO, MBTEMP, AGILENT4UHV, MKS937B, SPIXCONV = range(8)

    def __init__(self, name="generic", repo_url="A generic URL.", color=[255, 255, 255],
                 description="A generic host.", sha="", code=UNDEFINED):
        """
        Initializes a type instance.
        :param name: a type's name.
        :param repo_url: the repository address with all files needed to execute its function.
        :param color: A color to be used to represent the type in visual clients.
        :param description: A brief description of the type
        :param sha: A way to provide error detection.
        """
        self.name = name
        self.color = color
        self.repoUrl = repo_url
        self.description = description
        self.sha = sha
        self.code = code

    @property
    def name(self):

        if self.code == Type.POWER_SUPPLY:
            return 'Power Supply'
        elif self.code == Type.COUNTING_PRU:
            return 'CountingPRU'
        elif self.code == Type.SERIAL_THERMO:
            return 'Thermo Probe'
        elif self.code == Type.MBTEMP:
            return 'MBTemp'
        elif self.code == Type.AGILENT4UHV:
            return 'Agilent 4UHV'
        elif self.code == Type.MKS937B:
            return 'MKS 937b'
        elif self.code == Type.SPIXCONV:
            return 'SPIxCONV'
        else:
            return 'Undefined'

    @name.setter
    def name(self, value):

        pass

    @staticmethod
    def get_name_from_key(key):
        """
        Returns the prefix from a type's name.
        :param key: a type's id key.
        :return: a type's name without the prefix
        """
        if len(key) <= Type.KEY_PREFIX_LEN:
            return ''

        return key[Type.KEY_PREFIX_LEN:]

    def to_set(self):
        """
        Returns the object representation that will be saved on the Redis db.
        :return: string representation of dict representing a type
        """
        type_dict = copy.deepcopy(self.__dict__)
        return self.get_key(), type_dict

    def get_key(self):
        """
        Returns the name concatenated with the Type prefix. To be used to save instances into a Redis db.
        :return: the name concatenated with the Type prefix.
        """
        return Type.KEY_PREFIX + str(self.name)

    def from_set(self, type_dict):
        """
        Load values from a redis set.
        :param type_dict: dictionary representing a Type.
        :raise TypeError: the dictionary provided is None.
        """
        for key in type_dict:
            setattr(self, key, type_dict[key])

    def __eq__(self, other):
        """
        A way to compare two types.
        :param other: other type instance.
        :return: True if the other's name is equal to the self's name, False otherwise.
        """
        if other is None:
            return False

        if type(other) != type(self):
            return False

        return other.to_set() == self.to_set()

    def __str__(self):
        return str(self.__dict__)


class Node(BaseRedisEntity):
    """
    This class represents a Controls group's host. Each host has a symbolic name, a valid IP address, a type
    and the sector where it is located.
    """
    KEY_PREFIX = 'Node:'
    KEY_PREFIX_LEN = len(KEY_PREFIX)
    REBOOT_COUNTER_PERIOD = -90

    def __init__(self, name="r0n0", ip_address="10.128.0.0", state=NodeState.DISCONNECTED, type_node=None, sector=1,
                 counter=0, pv_prefixes=[], rc_local_path='', details='', config_time=''):
        """
        Initializes a node instance.
        :param name: a node's name.
        :param ip: string representation of a node's ip address.
        :param state: current node's state.
        :param type_node: current node's type.
        :param sector: current node's sector.
        :param counter: heart beat count.
        :param pv_prefixes: deprecated - a BBB will not provide PVs.
        :param rc_local_path: rc.local location in the project.
        :param details: details provided by the host
        :param config_time: when the host found it's configuration
        :param device: device informed by the host
        """

        self.name = name
        self.ip_address = ip_address
        self.state = state
        self.state_string = NodeState.to_string(state)
        self.type = type_node
        self.sector = sector
        self.pvPrefix = pv_prefixes
        self.counter = counter
        self.rcLocalPath = rc_local_path

        self.details = details
        self.config_time = config_time

    # @property
    # def state_string(self):
    #      """
    #      String representation of state
    #      """
    #      return NodeState.to_string(self.state)

    def update_state(self, state):
        """
        Updates the current node's state.
        :param state: new node state.
        :return:
        """
        self.state = state
        self.state_string = NodeState.to_string(state)

    @staticmethod
    def get_prefix_string(pref):
        """
        Array to String !
        :return:
        """
        pref_str = ''
        if pref:
            for a_str in pref:
                pref_str += a_str + '\n'

        if pref_str.endswith('\r\n'):
            pref_str = pref_str[:-2]
        elif pref_str.endswith('\n') or pref_str.endswith('\r'):
            pref_str = pref_str[:-1]
        return pref_str

    @staticmethod
    def get_prefix_array(pref):
        """
        String to array!
        :param pref:
        :return:
        """
        pref_array = []
        if pref:
            pref = pref.replace(' ', '')
            for a_str in pref.split('\r\n'):
                pref_array.append(a_str)

        return set(pref_array)

    @staticmethod
    def get_name_from_key(key):
        """
        Removes prefix from key and returns the name.
        :param key:
        :return: the node's name without prefix.
        """
        if len(key) <= Node.KEY_PREFIX_LEN:
            return ''
        return key[Node.KEY_PREFIX_LEN:]

    def to_set(self):
        """
        Returns a node's dictionary representation.
        :return: node's key with prefix, the node's dictionary representation and the type of the node.
        """
        node_dict = copy.deepcopy(self.__dict__)
        type_dict = None
        if node_dict['type'] is not None:
            node_dict['type'] = self.type.name
            type_dict = self.type.to_set()

        return self.get_key(), node_dict, type_dict

    def get_key(self):
        """
        :return: returns the node's key with prefix
        """
        return (Node.KEY_PREFIX + str(self.name)).replace(' ', '')

    def from_set(self, node_dict, node_type):
        """
        Load the values from a redis set.
        :param node_dict: dictionary representing the node object according to the pattern defined
        in the method get_set() from the Node object.
        :param node_type: the type object or dictionary that this node shall contain.
        :raise TypeError: the dictionary provided is None.
        """
        for key in node_dict:

            if key == 'type':
                if node_dict[key] is not None:
                    print(type(Type))
                    print(type(node_type))
                    if type(node_type) == dict:
                        new_type = Type()
                        new_type.from_set(node_type)
                        node_dict[key] = new_type
                    elif type(node_type) == Type:
                        node_dict[key] = node_type
                    else:
                        node_dict[key] = None

            setattr(self, key, node_dict[key])

    def is_connected(self):
        """
        :return: True if the state is NodeState.CONNECTED. False, otherwise.
        """
        return self.state != NodeState.DISCONNECTED

    def __eq__(self, other):
        """
        Overrides == operator. Compares two Node objects.
        :param other: a other node instance.
        :return: True if the other instance has the same name or IP address.
        """
        if type(other) is not Node:

            if type(other) is ipaddress.IPv4Address:
                return self.ip_address == other

            if type(other) is str:
                return self.name == other

            return False

        return self.name == other.name or self.ip_address == other.ip_address

    def is_strictly_equal(self, other):
        """
        Checks if both name and IP address are equal on both object.
        :param other: a other node instance.
        :return: True if the other instance has the same name and IP address.
        """

        if type(other) is not Node.__class__:
            return False

        return self.name == other.name and self.ip_address == other.ipAddress

    def __str__(self):
        """
        :return: the string representation of the object
        """
        return "Name: %s, IP Address: %s, Current state: %s" % (
            self.name, self.ip_address, NodeState.to_string(self.state))
