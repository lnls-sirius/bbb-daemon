from common.entity.entities import Command, NodeState, Sector, Node, Type
from common.util.git import cloneRepository, checkUrlFunc

import threading
import time

from network.db import RedisPersistence


class MonitorController():
    monitor_controller = None
    MAX_LOST_PING = 5

    def __init__(self, redis_server_ip: str, redis_server_port: int, sftp_home_dir: str = '/root/bbb-daemon-repos/'):

        self.sftp_home_dir = sftp_home_dir
        self.db = RedisPersistence(host=redis_server_ip, port=redis_server_port)

        self.sectors = Sector.sectors()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": [], "unconfigured": []}
            self.updateNodesLockList[sector] = threading.Lock()

        self.scanNodes = True
        self.updateNodesThread = threading.Thread(target=self.scanNodesWorker)
        self.updateNodesThread.start()

    def fetchTypes(self):
        return self.db.fetchTypes()

    def appendType(self, newType):
        return self.db.appendType(newType)

    def scanNodesWorker(self):

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
                                fetchedNode.changeState(NodeState.DISCONNECTED)
                            else:
                                fetchedNode.changeState(configuredNode.state)

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
        """

        :param newNode:
        :return: True or False
        """
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
        return self.db.getType(typeName)

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

    def getNodeByAddr(self, ipAddress: str, sector):
        if ipAddress is None or sector is None:
            return None
        nodes = self.db.fetchNodesFromSector(sector)
        for node in nodes:
            if node.ipAddress == ipAddress:
                return node
        return None

    def checkIpAvailable(self, ip=None,
                         name=None):
        if ip is None or name is None:
            return False, "Node name/ip is not defined."

        node = self.db.getNodeByAddr(node_addr=ip)
        if node is None:
            return True, "No node with the ip {} is registered.".format(ip)
        else:
            if node.name == name:
                return True, "The ip {} is already belong to this node ({})".format(ip, name)
            else:
                return False, "This ip {} is linked to another node ({})".format(ip, node.name)

    def getNode(self, node_name: str = None):
        return self.db.getNode(node_name)

    def getConfiguredNode(self, nodeIp, nodeSector):
        try:
            nodeSector = int(nodeSector)
        except:
            pass

        if nodeIp is None or nodeSector is None:
            return None

        for node_conf in (self.nodes.get(nodeSector, [])).get("configured", []):
            print('Nconf'.format(node_conf))
            if node_conf.ipAddress == nodeIp:
                return node_conf

        return None

    def rebootNode(self, registeredNode):
        if registeredNode == None:
            pass
        else:
            self.daemon.sendCommand(command=Command.REBOOT, address=registeredNode.ipAddress)

            sector = registeredNode.sector

            self.updateNodesLockList[sector].acquire()

            try:
                index = self.nodes[sector]["configured"].index(registeredNode)
                self.nodes[sector]["configured"][index].changeState(NodeState.REBOOTING)
            except:
                pass

            self.updateNodesLockList[sector].release()

    def updateNode(self, oldNode: Node = None, newNode: Node = None, oldNodeAddr: str = ''):
        """
            Update the misconfigured node with the  data of the selected configured node !
        Pass the oldNode aka the one with wrong info.
        :param oldNode: The node to be updated and to assume the newNode information.
        :param newNode: Configured node. The source of information
        :return:
        """
        if oldNode:
            oldNodeAddr = oldNode.ipAddress
        self.daemon.sendCommand(command=Command.SWITCH, address=oldNodeAddr, node=newNode)
        self.rebootNode(oldNode)

    def updateHostCounterByAddress(self, address, name, hostType, bbbSha: str = None):

        subnet = int(address.split(".")[2])
        sectorId = int(subnet / 10)
        sector = self.sectors[sectorId]

        self.updateNodesLockList[sector].acquire()

        isHostConnected = False
        misconfiguredHost = False

        for node in self.nodes[sector]["configured"]:

            if node.ipAddress == address:

                node.counter = MonitorController.MAX_LOST_PING

                if node.name == name and node.type.name == hostType and node.type.sha == bbbSha:
                    node.changeState(NodeState.CONNECTED)
                    print('connected {}'.format(node))
                    isHostConnected = True
                else:
                    node.changeState(NodeState.MISCONFIGURED)
                    misconfiguredHost = True
                break

        if not isHostConnected:

            availableType = self.findTypeByName(hostType)
            if not availableType:
                availableType = Type(name=hostType, description="Unknown type.")

            acknowlegedNode = False

            for unconfigNode in self.nodes[sector]["unconfigured"]:

                if unconfigNode.ipAddress == address:

                    unconfigNode.counter = MonitorController.MAX_LOST_PING
                    unconfigNode.name = name
                    unconfigNode.type = availableType

                    if misconfiguredHost:
                        unconfigNode.changeState(NodeState.MISCONFIGURED)
                    else:
                        unconfigNode.changeState(NodeState.CONNECTED)

                    acknowlegedNode = True
                    break

            if not acknowlegedNode:
                newUnconfigNode = Node(name=name, ip=address, state=NodeState.CONNECTED, typeNode=availableType,
                                       sector=sector, counter=MonitorController.MAX_LOST_PING)
                if misconfiguredHost:
                    newUnconfigNode.changeState(NodeState.MISCONFIGURED)

                self.nodes[sector]["unconfigured"].append(newUnconfigNode)

        self.updateNodesLockList[sector].release()

    def stopAll(self):
        self.scanNodes = False

    def validateRepository(self, rc_path: str = None, git_url: str = None, check_rc_local: bool = False):
        """
            Verify if the repository is valid.
        :param git_url:
        :param check_rc_local defaults to False. If true the exitence of the rc.local file will be checked.
        :return:  :return: (True or False), ("Message")
        """
        return checkUrlFunc(git_url=git_url, rc_local_path=rc_path, check_rc_local=check_rc_local)

    def cloneRepository(self, git_url=None, rc_local_path=None):
        """
            Clone the repository from git to the ftp server!
        :return: (True or False) , (message in case of Failure, SHA of the HEAD commit)
        """
        return cloneRepository(git_url=git_url, rc_local_path=rc_local_path, ftp_serv_location=self.sftp_home_dir)
