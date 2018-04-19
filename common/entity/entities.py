""" This module contains all entity classes of the project. """
import threading

class Sector ():

    SECTORS = ["Conectividade"] + [str (i) for i in range(1,21)] + ["LINAC", "RF", "Fontes"]

    @staticmethod
    def sectors ():
        return Sector.SECTORS

class Command ():

    PING, REBOOT, EXIT, END, TYPE, GET_TYPES, APPEND_TYPE, REMOVE_TYPE, NODE, GET_REG_NODES_SECTOR, GET_UNREG_NODES_SECTOR, APPEND_NODE, REMOVE_NODE = range (13)

class NodeState ():
    """ Valid states for any host in the Controls Group network. """

    DISCONNECTED, MISCONFIGURED, CONNECTED, REBOOTING = range (4)

    MISCONFIGURED_COLOR_STACK = [(255, 255, 153), (253, 255, 0), (204, 204, 255), (220, 220, 220)]
    MISCONFIGURED_INDEX = 1

    @staticmethod
    def useColor ():
        NodeState.MISCONFIGURED_INDEX = (NodeState.MISCONFIGURED_INDEX + 1) % len (NodeState.MISCONFIGURED_COLOR_STACK)
        return NodeState.MISCONFIGURED_COLOR_STACK [NodeState.MISCONFIGURED_INDEX]

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

class Node ():
    """
        This class represents a Controls group's host.
        Each host has a symbolic name, a valid IP address, a type and the sector where it is located.
    """

    def __init__ (self, name = "r0n0", ip = "10.128.0.0", state = NodeState.DISCONNECTED, typeNode = None, sector = 1, counter = 0):

        self.name = name
        self.ipAddress = ip
        self.state = state
        self.misconfiguredColor = None
        self.type = typeNode
        self.sector = sector

        self.counter = counter

        # Since we are working in a multi-thread environment, a mutex control is required
        self.stateMutex = threading.Lock()

    # Change the current state of the object. Refer to the Control_Node_State class
    def changeState (self, state):

        self.stateMutex.acquire()

        self.state = state

        self.stateMutex.release()

    # Returns True if the state is Control_Node_State.CONNECTED
    def isConnected (self):

        self.info_mutex.acquire()

        conn = (self.state != NodeState.DISCONNECTED)

        self.info_mutex.release()

        return conn

    # Returns the string representation of the object
    def __str__ (self):

        self.stateMutex.acquire()

        r_str = "Name: %s, IP Address: %s, Current state: %s" \
                % (self.name, self.ipAddress, NodeState.toString (self.state))

        self.stateMutex.release()

        return r_str

    def __dict__ (self):
        return {"name" : self.name, "ip" : self.ipAddress, "state": self.state, "type" : self.type.__dict__ (), "sector" : self.sector}

class Type ():
    """ This class provides a wrapper for host types. """

    def __init__ (self, id = 0, name = "generic", color = (255, 255, 255), description = "A generic host."):

        self.name = name
        self.color = color
        self.description = description

    def __dict__ (self):
        return {"name" : self.name, "color" : self.color, "description" : self.description}

    def __str__ (self):
        return str (self.__dict__())
