""" This module contains all entity classes of the project. """
import ast


class BaseRedisEntity():
    key_prefix = 'prefix_'
    key_prefix_len = len(key_prefix)

    def toSet(self):
        pass

    def fromSet(self, str_dic):
        pass

    def get_key(self):
        pass

    @staticmethod
    def get_name_from_key(key: str):
        if len(key) <= Node.key_prefix_len:
            return ''
        return key[Node.key_prefix_len:]


class Sector():
    SECTORS = ["Conectividade"] + [str(i) for i in range(1, 21)] + ["LINAC", "RF", "Fontes"]

    @staticmethod
    def sectors():
        return Sector.SECTORS


class Command():
    PING, REBOOT, EXIT, END, TYPE, GET_TYPES, APPEND_TYPE, REMOVE_TYPE, NODE, GET_REG_NODES_SECTOR, GET_UNREG_NODES_SECTOR, APPEND_NODE, REMOVE_NODE, SWITCH = range(
        14)


class NodeState():
    """ Valid states for any host in the Controls Group network. """

    DISCONNECTED, MISCONFIGURED, CONNECTED, REBOOTING = range(4)

    MISCONFIGURED_COLOR_STACK = [(255, 255, 153), (253, 255, 0), (204, 204, 255), (220, 220, 220)]
    MISCONFIGURED_INDEX = 1

    @staticmethod
    def useColor():
        NodeState.MISCONFIGURED_INDEX = (NodeState.MISCONFIGURED_INDEX + 1) % len(NodeState.MISCONFIGURED_COLOR_STACK)
        return NodeState.MISCONFIGURED_COLOR_STACK[NodeState.MISCONFIGURED_INDEX]

    # String representation of a state
    @staticmethod
    def toString(state):

        if state == NodeState.DISCONNECTED:
            return "Disconnected"

        elif state == NodeState.CONNECTED:
            return "Connected"

        elif state == NodeState.MISCONFIGURED:
            return "Misconfigured"

        elif state == NodeState.REBOOTING:
            return "Rebooting"

        return "Unknown state"


class Node(BaseRedisEntity):
    """
        This class represents a Controls group's host.
        Each host has a symbolic name, a valid IP address, a type and the sector where it is located.
    """
    key_prefix = 'node_'
    key_prefix_len = len(key_prefix)

    def __init__(self, name="r0n0", ip="10.128.0.0", state=NodeState.DISCONNECTED, typeNode=None, sector=1, counter=0,
                 pvPrefix=[]):

        self.name = name
        self.ipAddress = ip
        self.state = state
        self.state_string = NodeState.toString(state)
        self.misconfiguredColor = None
        self.type = typeNode
        self.sector = sector
        self.pvPrefix = pvPrefix
        self.counter = counter

    @staticmethod
    def get_name_from_key(key: str):
        if len(key) <= Node.key_prefix_len:
            return ''
        return key[Node.key_prefix_len:]

    def set_prefix(self):
        pass

    def toSet(self):
        key = self.get_key()
        nodeInfo = {"ipAddress": self.ipAddress, "sector": self.sector, "prefix": self.pvPrefix}
        if self.type is None:
            nodeInfo["type"] = None
        else:
            nodeInfo['type'] = self.type.name
        content = str(nodeInfo)
        return key, content

    def get_key(self):
        return (Node.key_prefix + self.name).replace(' ', '')

    def fromSet(self, str_dic):
        """
            Load the values from a redis set.
        :param str_dic:
        :return:
        """
        if str_dic is None:
            return

        dic_obj = str_dic.decode('utf-8')
        if type(dic_obj) is str:
            dic_obj = ast.literal_eval(dic_obj)

        if type(dic_obj) is dict:
            self.ipAddress = dic_obj.get("ipAddress", '')
            self.pvPrefix = dic_obj.get("prefix", [])
            self.sector = dic_obj.get("sector", self.sector)

    # Change the current state of the object. Refer to the Control_Node_State class
    def changeState(self, state):
        self.state = state
        self.state_string = NodeState.toString(state)

    # Returns True if the state is Control_Node_State.CONNECTED
    def isConnected(self):
        return (self.state != NodeState.DISCONNECTED)

    def __eq__(self, other):
        if other is None:
            return False

        return self.name == other.name or self.ipAddress == other.ipAddress

    # Returns the string representation of the object
    def __str__(self):
        return "Name: %s, IP Address: %s, Current state: %s" % (
            self.name, self.ipAddress, NodeState.toString(self.state))


class Type(BaseRedisEntity):
    """ This class provides a wrapper for host types. """
    key_prefix = 'type_'
    key_prefix_len = len(key_prefix)

    def __init__(self, name="generic", repoUrl="A generic URL.", rcLocalPath="init/rc.local", color=(255, 255, 255),
                 description="A generic host.", sha: str = ""):
        self.name = name
        self.color = color
        self.repoUrl = repoUrl
        self.description = description
        self.rcLocalPath = rcLocalPath
        self.sha = sha

    @staticmethod
    def get_name_from_key(key: str):
        if len(key) <= Type.key_prefix_len:
            return ''
        return key[Type.key_prefix_len:]

    def toSet(self):
        key = self.get_key()
        content = str({k: vars(self)[k] for k in ("description", "color", "repoUrl", "rcLocalPath", "sha")})
        return key, content

    def get_key(self):
        return Type.key_prefix + self.name

    def fromSet(self, str_dic):
        """
            Load the values from a redis set.
        :param str_dic:
        :return:
        """
        if str_dic is None:
            return

        dic_obj = str_dic.decode('utf-8')
        if type(dic_obj) is str:
            dic_obj = ast.literal_eval(dic_obj)

        if type(dic_obj) is dict:
            self.color = dic_obj.get('color', '')
            self.repoUrl = dic_obj.get('repoUrl', '')
            self.rcLocalPath = dic_obj.get('rcLocalPath', 'init/rc.local')
            self.description = dic_obj.get("description", '')
            self.sha = dic_obj.get("sha", '')

    def __eq__(self, other):
        if other is None:
            return False

        if type(other) == str:
            return self.name == other

        return self.name == other.name

    def __str__(self):
        return str(self.__dict__)
