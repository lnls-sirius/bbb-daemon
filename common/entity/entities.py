""" This module contains all entity classes of the project. """


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


class Node():
    """
        This class represents a Controls group's host.
        Each host has a symbolic name, a valid IP address, a type and the sector where it is located.
    """

    def __init__(self, name="r0n0", ip="10.128.0.0", state=NodeState.DISCONNECTED, typeNode=None, sector=1, counter=0,
                 pvPrefix=""):
        self.name = name
        self.ipAddress = ip
        self.state = state
        self.misconfiguredColor = None
        self.type = typeNode
        self.sector = sector
        self.pvPrefix = pvPrefix

        self.counter = counter

    # Change the current state of the object. Refer to the Control_Node_State class
    def changeState(self, state):
        self.state = state

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


class Type():
    """ This class provides a wrapper for host types. """

    def __init__(self, name="generic", repoUrl="A generic URL.", rcLocalPath="init/rc.local", color=(255, 255, 255),
                 description="A generic host."):

        self.name = name
        self.color = color
        self.repoUrl = repoUrl
        self.description = description
        self.rcLocalPath = rcLocalPath

    def __eq__(self, other):
        if other is None:
            return False

        if type(other) == str:
            return self.name == other

        return self.name == other.name

    def __str__(self):
        return str(self.__dict__)
