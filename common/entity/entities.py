"""
This module contains all entity classes of the project.
"""
import ast
import ipaddress
import json
import copy

PING_KEY_PREFIX = 'Ping:'
MISSING_KEY_PREFIX = 'Missing:'
EXPECTED_KEY_PREFIX = 'Expected:'



PING_NODES = 'Ping:Nodes'
MISSING_NODES  = 'Missing:Nodes'
EXPECTED_NODES = 'Expected:Nodes'

class NewIp():
    def __init__(self, ip, ip_new, ip_network, ip_gateway):
        self.ip = ipaddress.ip_address(ip)
        self.ip_new = ipaddress.ip_address(ip_new)
        self.ip_gateway = ipaddress.ip_address(ip_gateway)
        self.ip_network = ipaddress.ip_network(ip_network)

        if not self.ip_new in self.ip_network:
            raise ValueError('new_ip: The ip {} does not belong to the network {}.'.format(self.ip, self.ip_network))

        if not self.ip_gateway in self.ip_network:
            raise ValueError('gateway: The ip {} does not belong to the network {}.'.format(self.ip_gateway, self.ip_network))

        self.netmask = self.ip_network.netmask

    def __str__(self):
        return 'Original IP: {}. New IP {}. GW {}. Network {}. Mask {}'\
            .format(self.ip, self.ip_new, self.ip_gateway, self.ip_network, self.netmask)

class Command:
    """
    A simple class to wrap command codes.
    """
    PING = 0
    EXIT = 1

    PING, REBOOT, EXIT, END, TYPE, APPEND_TYPE, REMOVE_TYPE, NODE, APPEND_NODE, REMOVE_NODE, SWITCH, \
    GET_TYPES, GET_UNREG_NODES_SECTOR, GET_REG_NODES_SECTOR, GET_REG_NODE_BY_IP, OK, FAILURE, SET_IP, \
    SET_HOSTNAME, NAMESERVERS = range(20)

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
    # SECTORS = [('Sala' + str(i).zfill(2)) for i in range(1, 21)] + ["LTS", "Conectividade", "LINAC", "RF", "Fontes", "Sala de Controle", "Outros"]

    # SUBNETS = [[ipaddress.ip_network(u'10.128.1.0/24'),
    #             ipaddress.ip_network(u'10.128.255.0/24')]] + \
    #           [ipaddress.ip_network(u'10.128.{}.0/24'.format(i)) for i in range(101, 122)] + \
    #           [ipaddress.ip_network(u'10.128.{}.0/24'.format(i)) for i in range(201, 222)] + \
    #           [ipaddress.ip_network(u'10.128.{}.0/24'.format(i)) for i in range(150, 153)]

    SECTORS_DICT = {}

    SECTORS_DICT['LINAC'] = ipaddress.ip_network(u'10.128.1.0/24')

    for i in range(1,21):
        SECTORS_DICT['Sala-{}'.format(str(i).zfill(2))] = ipaddress.ip_network(u'10.128.{}.0/24'.format(i + 100))
    for i in range(1,21):
        SECTORS_DICT['DIG-BPM-Sala-{}'.format(str(i).zfill(2))] =ipaddress.ip_network(u'10.128.{}.0/24'.format(i + 200))

    SECTORS_DICT['LTB'] = ipaddress.ip_network(u'10.128.121.0/24')
    SECTORS_DICT['Conectividade'] = ipaddress.ip_network(u'10.128.122.0/24')
    SECTORS_DICT['Fontes'] = ipaddress.ip_network(u'10.128.123.0/24')
    SECTORS_DICT['RF'] = ipaddress.ip_network(u'10.128.124.0/24')

    SECTORS_DICT['DIG-Outros'] = ipaddress.ip_network(u'10.128.150.0/24')
    SECTORS_DICT['DIG-Cameras'] = ipaddress.ip_network(u'10.128.151.0/24')
    SECTORS_DICT['DIG-Galil'] = ipaddress.ip_network(u'10.128.152.0/24')
    SECTORS_DICT['DIG-Servidores-Dell'] = ipaddress.ip_network(u'10.128.153.0/24')

    SECTORS_DICT['Sala de Controle'] = ipaddress.ip_network(u'10.128.254.0/24')
    SECTORS_DICT['Rede de Servidores'] = ipaddress.ip_network(u'10.128.254.0/24')

    @staticmethod
    def subnets():
        return [str(subnet) for subnet in Sector.SECTORS_DICT.values()]

    @staticmethod
    def get_sectors_dict():
        return Sector.SECTORS_DICT

    @staticmethod
    def sectors():
        return Sector.SECTORS_DICT.keys()

    @staticmethod
    def get_sector_by_ip_address(ip_address=None):
        """
        Returns the sector of a node based on its IP address.
        :param ip_address: the IP address of a host.
        :return: the sector that contains the given IP address.
        :raise SectorNotFoundError: IP address is not contained in any sub-network.
        """
        if type(ip_address) == str:
            ip_address = ipaddress.ip_address(ip_address)

        for sector, ip_network  in Sector.SECTORS_DICT.items():
            if ip_address in ip_network:
                return sector
        return 'Outros'

    @staticmethod
    def get_default_gateway_of_address(ip_address=None):
        """
        Returns the default gateway of a node based on its IP address.
        :param ip_address: the IP address of a host.
        :return: the default gateway of that host. An ipaddress.IPv4Address object.
        :raise SectorNotFoundError: IP address is not contained in any sub-network.
        """
        if type(ip_address) == str:
            ip_address = ipaddress.ip_address(ip_address)

        for sector, ip_network  in Sector.SECTORS_DICT.items():
            if ip_address in ip_network:
                return ip_network.network_address + 1

        raise SectorNotFoundError()

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

    def to_dict(self):
        """
        Returns a set representation of the object.
        :raise NotImplementedError: empty method.
        """
        raise NotImplementedError("Provide an implementation for BaseRedisEntity class")

    def from_dict(self, **kwargs):
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

    def get_ping_key(self):
        """
        :return: returns the node's ping key
        """
        return PING_KEY_PREFIX + self.get_key()

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


class Type():
    """
    This class provides a wrapper for host types.
    """

    KEY_PREFIX = 'Type:'
    KEY_PREFIX_LEN = len(KEY_PREFIX)

    NUM_TYPES = 8
    UNDEFINED, POWER_SUPPLY, COUNTING_PRU, SERIAL_THERMO, MBTEMP, AGILENT4UHV, MKS937B, SPIXCONV = range(NUM_TYPES)
    TYPES = []

    @staticmethod
    def from_code(type_code):
        if type(type_code) == str:
            type_code = int(type_code)

        if type_code not in range(Type.NUM_TYPES):
            raise ValueError("type_code {} invalid.".format(type_code))

        return Type(code=type_code)

    def __init__(self, **kwargs):
        """
        Initializes a type instance.
        :param name: a type's name.
        """
        self.code = kwargs.get('code', Type.UNDEFINED)

    @property
    def description(self):
        if self.code == Type.POWER_SUPPLY:
            return 'Desc: Power Supply'
        elif self.code == Type.COUNTING_PRU:
            return 'Desc: CountingPRU'
        elif self.code == Type.SERIAL_THERMO:
            return 'Desc: Thermo Probe'
        elif self.code == Type.MBTEMP:
            return 'Desc: MBTemp'
        elif self.code == Type.AGILENT4UHV:
            return 'Desc: Agilent 4UHV'
        elif self.code == Type.MKS937B:
            return 'Desc: MKS 937b'
        elif self.code == Type.SPIXCONV:
            return 'Desc: SPIxCONV'
        else:
            return 'Desc: Undefined'

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

    @description.setter
    def description(self, value):
        pass

    def __eq__(self, other):
        """
        A way to compare two types.
        :param other: other type instance.
        :return: True if the code is equal.
        """
        if other is None:
            return False

        return other.code == self.code

    def __str__(self):
        return '{}\t{}'.format(type(self), str(self.__dict__))

    def to_dict(self):
        return {'name':self.name, 'description':self.description}

    @staticmethod
    def get_types():
        d = {}
        for _t in Type.TYPES:
            d[_t.code] = _t.to_dict()
        return d

for n in range(Type.NUM_TYPES):
    Type.TYPES.append(Type(code=n))

class ConfiguredNode:
    expected_configured_nodes = {}
    expected_configured_nodes_dict = []

    @staticmethod
    def refresh_expected_configured_nodes_dict():
        """
        Refresh the content of configured nodes dict!
        """
        for node in ConfiguredNode.expected_configured_nodes.values():
            ConfiguredNode.expected_configured_nodes_dict.append(node.to_dict())

    @staticmethod
    def load_expected_device_list(path):
        with open(path, 'r') as f:
            for line in f:
                ip, network, type_code = line.split(' ')
                ConfiguredNode.expected_configured_nodes[ip] = ConfiguredNode(ip_address=ip, ip_network=network, type_code=type_code)
        ConfiguredNode.refresh_expected_configured_nodes_dict()

    def __init__(self,  ip_address, ip_network ,type_code):
        self.ip_address = ipaddress.ip_address(ip_address)
        self.ip_network = ipaddress.ip_network(ip_network)
        self.type_code = type_code

    def to_dict(self):
        return {
            'ip_address': self.ip_address.__str__(),
            'ip_network': self.ip_network.__str__(),
            **Type.from_code(self.type_code).to_dict()
        }

class Node(BaseRedisEntity):
    """
    This class represents a Controls group's host. Each host has a symbolic name, a valid IP address, a type
    and the sector where it is located.
    """
    EXPIRE_TIME = 5

    KEY_PREFIX = 'Node:'
    KEY_PREFIX_LEN = len(KEY_PREFIX)
    REBOOT_COUNTER_PERIOD = -90

    def __init__(self, **kwargs):
        """
        Initializes a node instance.
        :param name: a node's name.
        :param ip: string representation of a node's ip address.
        :param state: current node's state.
        :param type_node: current node's type.
        :param sector: current node's sector.
        :param counter: heart beat count.
        :param details: details provided by the host
        :param config_time: when the host found it's configuration
        """

        self.name = kwargs.get('name', 'Node-With-No-Name')
        self.ip_address = kwargs.get('ip_address', '10.128.0.0')
        self.state = kwargs.get('state', NodeState.DISCONNECTED)
        self.state_string = NodeState.to_string(self.state)
        self.type = kwargs.get('type_node', Type(code=Type.UNDEFINED))
        self.sector = kwargs.get('sector', 1)
        self.counter = kwargs.get('counter', 0)

        self.details = kwargs.get('details', '')
        self.config_time = kwargs.get('config_time', '')

    def update_state(self, state):
        """
        Updates the current node's state.
        :param state: new node state.
        :return:
        """
        self.state = state
        self.state_string = NodeState.to_string(state)

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

    def to_dict(self):
        """
        Returns a node's dictionary representation.
        :return: node's key with prefix, the node's dictionary representation and the type of the node.
        """
        node_dict = copy.deepcopy(self.__dict__)
        if node_dict['type'] is not None:
            node_dict['type'] = self.type.code
        else:
            node_dict['type'] = Type(code=Type.UNDEFINED)
        return self.get_key(), node_dict

    @staticmethod
    def get_key_static(ip_address):
        return (Node.KEY_PREFIX + str(ip_address)).replace(' ', '')

    def get_key(self):
        """
        :return: returns the node's key with prefix
        """
        return (Node.KEY_PREFIX + str(self.ip_address)).replace(' ', '')

    def from_dict(self, node_dict , **kwargs):
        """
        Load the values from a redis set.
        :param node_dict: dictionary representing the node object according to the pattern defined
        in the method get_set() from the Node object.
        :raise TypeError: the dictionary provided is None.
        """
        for key in node_dict:
            if key == 'type':
                _type = node_dict[key]
                if _type is not None:
                    if type(_type) != Type:
                        node_dict[key] = Type(code = int(_type))
                    else:
                        node_dict[key] = _type
                else:
                    node_dict[key] = Type(code=Type.UNDEFINED)

            setattr(self, key, node_dict[key])

    def is_connected(self):
        """
        :return: True if the state is NodeState.CONNECTED. False, otherwise.
        """
        return self.state != NodeState.DISCONNECTED

    def __str__(self):
        """
        :return: the string representation of the object
        """
        return '{}\t{}'.format(type(self), str(self.__dict__))
