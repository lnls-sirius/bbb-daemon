from common.entity.entities import Command, Node, NodeState, Sector, Type
import threading
import time

from network.db import RedisPersistence


class MonitorController():
    MAX_LOST_PING = 5

    def __init__(self, redis_server_ip: str = 'localhost', redis_server_port: int = 6379):

        self.db = RedisPersistence(host=redis_server_ip, port=redis_server_port)

        self.sectors = Sector.sectors()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": [], "unconfigured": []}
            self.updateNodesLockList[sector] = threading.Lock()

        self.updateNodesThread = threading.Thread(target=self.scanNodes)
        self.scanNodes = True

        self.updateNodesThread.start()

    def fetchTypes(self):
        return self.db.fetchTypes()

    def appendType(self, newType):
        return self.db.appendType(newType)

    def scanNodes(self):

        while self.scanNodes:

            for sector in self.sectors:

                self.updateNodesLockList[sector].acquire()
                fetchedNodes = self.fetchNodesFromSector(sector)

                # Verify if there is an unregistered node
                for fetchedNode in fetchedNodes:
                    for configuredNode in self.nodes[sector]["configured"]:
                        if fetchedNode.name == configuredNode.name:
                            fetchedNode.counter = max(-90, configuredNode.counter - 1)
                            # A host is considered disconnected if its internal counter reaches 0 (connected) or -90 (rebooting)
                            if (configuredNode.state != NodeState.REBOOTING and fetchedNode.counter <= 0) or \
                                    (configuredNode.state == NodeState.REBOOTING and fetchedNode.counter <= -90):
                                fetchedNode.state = NodeState.DISCONNECTED
                            else:
                                fetchedNode.state = configuredNode.state

                # Updates configured nodes
                self.nodes[sector]["configured"] = fetchedNodes

                # Verify unregistered nodes and remove from the list if they are disconnected
                for unconfiguredNode in self.nodes[sector]["unconfigured"]:
                    unconfiguredNode.counter = max(0, unconfiguredNode.counter - 1)
                    if unconfiguredNode.counter == 0:
                        self.nodes[sector]["unconfigured"].remove(unconfiguredNode)

                self.updateNodesLockList[sector].release()

            time.sleep(1)

    def appendNode(self, newNode: Node = None):
        success = self.db.appendNode(newNode)

        if success:
            sector = newNode.sector
            self.updateNodesLockList[sector].acquire()

            newNode.counter = MonitorController.MAX_LOST_PING

            if newNode in self.nodes[sector]["configured"]:
                index = self.nodes[sector]["configured"].index(newNode)
                self.nodes[sector]["configured"][index].name = newNode.name
                self.nodes[sector]["configured"][index].ipAddress = newNode.ipAddress
            else:
                self.nodes[sector]["configured"].append(newNode)

            # Verify unregistered nodes and remove from the list if they are disconnected
            if newNode in self.nodes[sector]["unconfigured"]:
                index = self.nodes[sector]["unconfigured"].index(newNode)
                if newNode.name == self.nodes[sector]["unconfigured"][index].name and \
                        newNode.ipAddress == self.nodes[sector]["unconfigured"][index].ipAddress:
                    self.nodes[sector]["unconfigured"].remove(newNode)

            self.updateNodesLockList[sector].release()

        return success

    def removeType(self, t):
        self.db.removeType(t)

    def findTypeByName(self, typeName):
        for t in self.fetchTypes():
            if t.name == typeName:
                return t
        return None

    def removeNodeFromSector(self, node):
        count = self.db.removeNodeFromSector(node)

        if count > 0:
            sector = node.sector
            self.updateNodesLockList[sector].acquire()
            self.nodes[sector]["configured"] = [i for i in self.nodes[sector]["configured"] if i.name != node.name]
            self.updateNodesLockList[sector].release()

        return count

    def fetchNodesFromSector(self, sector=1):
        return self.db.fetchNodesFromSector(sector)

    def getRegisteredNodesFromSector(self, sector=1):
        self.updateNodesLockList[sector].acquire()
        nodes = self.nodes[sector]["configured"]
        self.updateNodesLockList[sector].release()
        return nodes

    def getUnregisteredNodesFromSector(self, sector=1):
        self.updateNodesLockList[sector].acquire()
        nodes = self.nodes[sector]["unconfigured"]
        self.updateNodesLockList[sector].release()
        return nodes

    def rebootNode(self, registeredNode):
        self.daemon.sendCommand(command=Command.REBOOT, address=registeredNode.ipAddress)

        sector = registeredNode.sector

        self.updateNodesLockList[sector].acquire()

        try:
            index = self.nodes[sector]["configured"].index(registeredNode)
            self.nodes[sector]["configured"][index].state = NodeState.REBOOTING
        except:
            pass

        self.updateNodesLockList[sector].release()

    def updateNode(self, oldNode, newNode):
        self.daemon.sendCommand(command=Command.SWITCH, address=oldNode.ipAddress, node=newNode)
        self.rebootNode(oldNode)

    def updateHostCounterByAddress(self, address, name, hostType):

        subnet = int(address.split(".")[2])
        sectorId = int(subnet / 10)
        sector = self.sectors[sectorId]

        self.updateNodesLockList[sector].acquire()

        isHostConnected = False
        misconfiguredHost = False

        for node in self.nodes[sector]["configured"]:

            if node.ipAddress == address:

                node.counter = MonitorController.MAX_LOST_PING

                if node.name == name and node.type.name == hostType:
                    node.state = NodeState.CONNECTED
                    isHostConnected = True
                else:
                    node.state = NodeState.MISCONFIGURED
                    misconfiguredHost = True
                break

        if not isHostConnected:

            availableType = self.findTypeByName(hostType)
            if availableType == None:
                availableType = Type(name=hostType, description="Unknown type.")

            acknowlegedNode = False

            for unconfigNode in self.nodes[sector]["unconfigured"]:

                if unconfigNode.ipAddress == address:

                    unconfigNode.counter = MonitorController.MAX_LOST_PING
                    unconfigNode.name = name
                    unconfigNode.type = availableType

                    if misconfiguredHost:
                        unconfigNode.state = NodeState.MISCONFIGURED
                    else:
                        unconfigNode.state = NodeState.CONNECTED

                    acknowlegedNode = True
                    break

            if not acknowlegedNode:

                newUnconfigNode = Node(name=name, ip=address, state=NodeState.CONNECTED, typeNode=availableType,
                                       sector=sector, counter=MonitorController.MAX_LOST_PING)
                if misconfiguredHost:
                    newUnconfigNode.state = NodeState.MISCONFIGURED

                self.nodes[sector]["unconfigured"].append(newUnconfigNode)

        self.updateNodesLockList[sector].release()

    def stopAll(self):
        self.scanNodes = False
