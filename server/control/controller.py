from common.entity.entities import Command, NodeState, Sector, Node, Type
from common.entity.metadata import Singleton
from common.util.git import cloneRepository, checkUrlFunc
from server.network.db import RedisPersistence

import threading
import time


class ServerController(metaclass=Singleton):
    """
    The main class of the server. It controls the server state and the client requests.
    """

    # A host is considered disconnected if the server has not received a ping from it within 5 time intervals.
    MAX_LOST_PING = 5
    # in seconds
    PING_INTERVAL = 5

    def __init__(self, sftp_home_dir: str = '/root/bbb-daemon-repos/'):
        """
        Initializes a controller.
        :param sftp_home_dir: the directory where the projects should be.
        """

        self.sftp_home_dir = sftp_home_dir
        self.db = RedisPersistence.get_instance()

        self.sectors = Sector.sectors()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": [], "unconfigured": []}
            self.updateNodesLockList[sector] = threading.Lock()

        self.scanNodes = True
        self.updateNodesThread = threading.Thread(target=self.scan_nodes_worker)
        self.updateNodesThread.start()

    def fetch_types(self):
        """
        :return: a list containing all types registered in the db.
        """
        return self.db.fetch_types()

    def append_type(self, new_type):
        """
        Appends a new type into the db.
        :param new_type: the new type's instance.
        :return: True is it succeeds and False, otherwise.
        """
        return self.db.append_type(new_type)

    def scan_nodes_worker(self):
        """
        A thread to decrement the counter of each host and update its status accordingly.
        """

        while self.scanNodes:

            for sector in self.sectors:

                self.updateNodesLockList[sector].acquire()
                fetched_nodes = self.fetch_nodes_from_sector(sector)

                # Verify if there is an unregistered node
                for fetched_node in fetched_nodes:

                    try:

                    for configuredNode in self.nodes[sector]["configured"]:
                        if fetched_node.name == configuredNode.name:
                            fetched_node.counter = max(Node.REBOOT_COUNTER_PERIOD - 1, configuredNode.counter - 1)
                            # A host is considered disconnected if its internal counter reaches 0 (connected)
                            #  or REBOOT_COUNTER_PERIOD(rebooting)
                            if (configuredNode.state != NodeState.REBOOTING and fetched_node.counter <= 0) or \
                                    (configuredNode.state == NodeState.REBOOTING and
                                     fetched_node.counter <= Node.REBOOT_COUNTER_PERIOD):
                                fetched_node.update_state(NodeState.DISCONNECTED)
                            else:
                                fetched_node.update_state(configuredNode.state)

                # Updates configured nodes
                self.nodes[sector]["configured"] = fetched_nodes

                # Verify unregistered nodes and remove from the list if they are disconnected
                for unconfigured_node in self.nodes[sector]["unconfigured"]:
                    unconfigured_node.counter = max(0, unconfigured_node.counter - 1)
                    if unconfigured_node.counter == 0:
                        self.nodes[sector]["unconfigured"].remove(unconfigured_node)

                self.updateNodesLockList[sector].release()

            time.sleep(ServerController.PING_INTERVAL)

    def append_node(self, new_node: Node = None):
        """
        Append a new node into the database.
        :param new_node: the node to be appended.
        :return: True or False
        """
        success = self.db.append_node(new_node)

        if success:
            sector = new_node.sector
            self.updateNodesLockList[sector].acquire()

            new_node.counter = ServerController.MAX_LOST_PING

            if new_node in self.nodes[sector]["configured"]:
                index = self.nodes[sector]["configured"].index(new_node)
                self.nodes[sector]["configured"][index].name = new_node.name
                self.nodes[sector]["configured"][index].ipAddress = new_node.ipAddress
            else:
                self.nodes[sector]["configured"].append(new_node)

            # Verify unregistered nodes and remove from the list if they are disconnected
            if new_node in self.nodes[sector]["unconfigured"]:
                index = self.nodes[sector]["unconfigured"].index(new_node)
                if new_node.name == self.nodes[sector]["unconfigured"][index].name and \
                        new_node.ipAddress == self.nodes[sector]["unconfigured"][index].ipAddress:
                    self.nodes[sector]["unconfigured"].remove(new_node)

            self.updateNodesLockList[sector].release()

        return success

    def remove_type(self, t):
        self.db.remove_type_by_name(t)

    def find_type_by_name(self, typeName):
        return self.db.get_type_by_name(typeName)

    def remove_node_from_sector(self, node):
        count = self.db.remove_node_from_sector(node)

        if count > 0:
            sector = node.sector
            self.updateNodesLockList[sector].acquire()
            self.nodes[sector]["configured"] = [i for i in self.nodes[sector]["configured"] if i.name != node.name]
            self.updateNodesLockList[sector].release()

        return count

    def fetch_nodes_from_sector(self, sector=1):
        return self.db.fetch_nodes_from_sector(sector)

    def get_registered_nodes_from_sector(self, sector=1):
        self.updateNodesLockList[sector].acquire()
        nodes = self.nodes[sector]["configured"]
        self.updateNodesLockList[sector].release()
        return nodes

    def get_unregistered_nodes_from_sector(self, sector=1):
        self.updateNodesLockList[sector].acquire()
        nodes = self.nodes[sector]["unconfigured"]
        self.updateNodesLockList[sector].release()
        return nodes

    def get_node_by_addr(self, ip_address: str):
        if ip_address is None:
            return None
        nodes = self.db.fetch_nodes_from_sector(Sector.get_sector_by_ip_address(ip_address))
        for node in nodes:
            if node.ipAddress == ip_address:
                return node
        return None

    def check_ip_available(self, ip=None, name=None):
        if ip is None or name is None:
            return False, "Node name/ip is not defined."

        node = self.db.get_node_by_address(node_address=ip)
        if node is None:
            return True, "No node with the ip {} is registered.".format(ip)
        else:
            if node.name == name:
                return True, "The ip {} is already belong to this node ({})".format(ip, name)
            else:
                return False, "This ip {} is linked to another node ({})".format(ip, node.name)

    def getNode(self, node_name: str = None):
        return self.db.get_node_by_name(node_name)

    def get_configured_node(self, nodeIp, node_sector):
        try:
            node_sector = int(node_sector)
        except:
            pass

        if nodeIp is None or node_sector is None:
            return None

        for node_conf in (self.nodes.get(node_sector, [])).get("configured", []):
            print('Node conf={}'.format(node_conf))
            if node_conf.ipAddress == nodeIp:
                return node_conf

        return None

    def get_unconfigured_node(self, nodeIp, nodeSector):
        try:
            nodeSector = int(nodeSector)
        except:
            pass

        if nodeIp is None or nodeSector is None:
            return None

        for node_uconf in (self.nodes.get(nodeSector, [])).get("unconfigured", []):
            print('Node conf={}'.format(node_uconf))
            if node_uconf.ipAddress == nodeIp:
                return node_uconf

        return None

    def reboot_node(self, registered_node: Node = None, configured=True):

        if registered_node == None:
            pass
        else:
            self.daemon.send_command(command=Command.REBOOT, address=registered_node.ipAddress)

            sector = registered_node.sector

            self.updateNodesLockList[sector].acquire()

            try:
                if configured:
                    index = self.nodes[sector]["configured"].index(registered_node)
                    self.nodes[sector]["configured"][index].update_state(NodeState.REBOOTING)
                else:
                    index = self.nodes[sector]["unconfigured"].index(registered_node)
                    self.nodes[sector]["unconfigured"][index].update_state(NodeState.REBOOTING)
            except:
                pass

            self.updateNodesLockList[sector].release()

    def update_node(self, oldNode: Node = None, newNode: Node = None, oldNodeAddr: str = ''):
        """
            Update the misconfigured node with the  data of the selected configured node !
        Pass the oldNode aka the one with wrong info.
        :param oldNode: The node to be updated and to assume the newNode information.
        :param newNode: Configured node. The source of information
        :return:
        """
        if oldNode:
            oldNodeAddr = oldNode.ipAddress
        self.daemon.send_command(command=Command.SWITCH, address=oldNodeAddr, node=newNode)
        self.reboot_node(oldNode)

    def update_host_counter_by_address(self, address, name, hostType, bbbSha: str = None):

        subnet = int(address.split(".")[2])
        sectorId = int(subnet / 10)
        sector = self.sectors[sectorId]

        self.updateNodesLockList[sector].acquire()

        isHostConnected = False
        misconfiguredHost = False

        for node in self.nodes[sector]["configured"]:

            if node.ipAddress == address:

                node.counter = ServerController.MAX_LOST_PING

                if node.name == name and node.type.name == hostType and node.type.sha == bbbSha:
                    node.update_state(NodeState.CONNECTED)
                    #print('connected {}'.format(node))
                    isHostConnected = True
                else:
                    node.update_state(NodeState.MISCONFIGURED)
                    misconfiguredHost = True
                break

        if not isHostConnected:

            availableType = self.find_type_by_name(hostType)
            if not availableType:
                availableType = Type(name=hostType, description="Unknown type.")

            acknowlegedNode = False

            for unconfigNode in self.nodes[sector]["unconfigured"]:

                if unconfigNode.ipAddress == address:

                    unconfigNode.counter = ServerController.MAX_LOST_PING
                    unconfigNode.name = name
                    unconfigNode.type = availableType

                    if misconfiguredHost:
                        unconfigNode.update_state(NodeState.MISCONFIGURED)
                    else:
                        unconfigNode.update_state(NodeState.CONNECTED)

                    acknowlegedNode = True
                    break

            if not acknowlegedNode:
                newUnconfigNode = Node(name=name, ip=address, state=NodeState.CONNECTED, type_node=availableType,
                                       sector=sector, counter=ServerController.MAX_LOST_PING)
                if misconfiguredHost:
                    newUnconfigNode.update_state(NodeState.MISCONFIGURED)

                self.nodes[sector]["unconfigured"].append(newUnconfigNode)

        self.updateNodesLockList[sector].release()

    def stop_all(self):
        self.scanNodes = False

    def validate_repository(self, rc_path: str = None, git_url: str = None, check_rc_local: bool = False):
        """
        Verify if the repository is valid.
        :param git_url:
        :param check_rc_local defaults to False. If true the exitence of the rc.local file will be checked.
        :return:  :return: (True or False), ("Message")
        """
        return checkUrlFunc(git_url=git_url, rc_local_path=rc_path, check_rc_local=check_rc_local)

    def clone_repository(self, git_url=None, rc_local_path=None):
        """
            Clone the repository from git to the ftp server!
        :return: (True or False) , (message in case of Failure, SHA of the HEAD commit)
        """
        return cloneRepository(git_url=git_url, rc_local_path=rc_local_path, ftp_serv_location=self.sftp_home_dir)
