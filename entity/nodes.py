import threading
import redis

class NodeState ():

    DISCONNECTED, CONNECTED, REBOOTING = range (3)

    # String representation of a state
    @staticmethod
    def toString(state):

        if state == NodeState.DISCONNECTED:
            return "Disconnected"

        elif state == NodeState.CONNECTED:
            return "Connected"

        elif state == NodeState.REBOOTING:
            return "Rebooting"

        return "Unknown state"

class Node ():

    def __init__ (self, name = "r0n0", ip = "10.128.0.0", state = NodeState.DISCONNECTED, typeNode = "generic", sector = 1):

        self.name = name
        self.ipAddress = ip
        self.state = state
        self.type = typeNode
        self.sector = sector

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
        return {"name" : self.name, "ip" : self.ipAddress, "type" : self.type, "sector" : self.sector}
