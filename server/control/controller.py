from common.entity.definition import MAX_LOST_PING, PING_INTERVAL
from common.entity.entities import Command, NodeState, Sector, Node, Type
from common.entity.metadata import Singleton
from common.util.git import cloneRepository, checkUrlFunc
from server.network.daemoninterface import DaemonHostListener

import logging
import threading
import time


class ServerController(metaclass=Singleton):
    """
    The main class of the server. It controls the server state and the client requests.
    """

    def __init__(self, sftp_home_dir: str = '/root/bbb-daemon-repos/'):
        """
        Initializes a controller.
        :param sftp_home_dir: the directory where the projects should be.
        """
        from server.network.db import RedisPersistence

        self.sftp_home_dir = sftp_home_dir
        self.db = RedisPersistence.get_instance()
        self.sectors = Sector.sectors()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": self.fetch_nodes_from_sector(sector),
                                  "unconfigured": []}
            self.updateNodesLockList[sector] = threading.Lock()

        self.logger = logging.getLogger('ServerController')

        self.scan_nodes = True
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

    def remove_type(self, t):
        """
        Removes a type from the db.
        :param t: Type instance to be removed.
        """
        return self.db.remove_type_by_name(t)

    def find_type_by_name(self, type_name):
        """
        Look up a Type instance by its name.
        :param type_name: a Type's name
        :return: a Type instance or None.
        """
        return self.db.get_type_by_name(type_name)

    def scan_nodes_worker(self):
        """
        It will loop though the ping nodes and update the configured nodes accordingly.
        """

        self.logger.info("Starting node scanning thread.")

        while self.scan_nodes:
            self.db.clear_ping_node_list()
            keys = self.db.get_node_keys()
            if keys:
                for key in keys:
                    print(key) # @todo: dbg
                    ping_node = self.db.get_ping_node(key=key)
                    if ping_node:
                        # @todo: Check if is configured or not! 
                        pass
                    else:
                        # The configured node is disconnected !S
                        
                        pass
                    pass
            # for sector in self.sectors:

            #     self.updateNodesLockList[sector].acquire()
            #     # Verify if there is an unregistered node
            #     for configured_node in self.nodes[sector]["configured"]:

            #         configured_node = self.nodes[sector]["configured"][self.nodes[sector]["configured"].index(configured_node)]
            #         configured_node.counter = max(Node.REBOOT_COUNTER_PERIOD - 1, configured_node.counter - 1)
            #         # A host is considered disconnected if its internal counter reaches 0 (connected)
            #         #  or REBOOT_COUNTER_PERIOD(rebooting)
            #         if (configured_node.state != NodeState.REBOOTING and configured_node.counter <= 0) or \
            #                 (configured_node.state == NodeState.REBOOTING and
            #                  configured_node.counter <= Node.REBOOT_COUNTER_PERIOD):
            #             configured_node.update_state(NodeState.DISCONNECTED)
            #         else:
            #             configured_node.update_state(configured_node.state)

            #     # Verify unregistered nodes and remove from the list if they are disconnected
            #     for unconfigured_node in self.nodes[sector]["unconfigured"]:
            #         unconfigured_node.counter = max(0, unconfigured_node.counter - 1)
            #         if unconfigured_node.counter <= 0:
            #             self.nodes[sector]["unconfigured"].remove(unconfigured_node)

            #     self.updateNodesLockList[sector].release()

            time.sleep(PING_INTERVAL)

        self.logger.info("Closing node scanning thread.")

    def append_node(self, new_node: Node = None):
        """
        Append a new node into the database.
        :param new_node: the node to be appended.
        :return: True or False
        """
        success_db = self.db.append_node(new_node)
        success_local = False

        if success_db:
            sector = new_node.sector
            self.updateNodesLockList[sector].acquire()

            new_node.counter = MAX_LOST_PING

            if new_node in self.nodes[sector]["configured"]:
                # Updates the current instance if the node is already in the db.
                index = self.nodes[sector]["configured"].index(new_node)
                self.nodes[sector]["configured"][index].name = new_node.name
                self.nodes[sector]["configured"][index].ip_address = new_node.ip_address
            else:
                self.nodes[sector]["configured"].append(new_node)

            # Verify unregistered nodes and remove from the list if they are disconnected
            if new_node in self.nodes[sector]["unconfigured"]:
                index = self.nodes[sector]["unconfigured"].index(new_node)
                if new_node.is_strictly_equal(self.nodes[sector]["unconfigured"][index]):
                    self.nodes[sector]["unconfigured"].remove(new_node)

            # Local lists updated successfully.
            success_local = True

            self.updateNodesLockList[sector].release()

        return success_db and success_local

    def remove_node_from_sector(self, node):
        """
        Removes a given node from a sector. The sector information is obtained from the Node instance parameter itself.
        :param node: the node to be removed.
        :return: the number of elements removed.
        """
        count = self.db.remove_node_from_sector(node)

        if count > 0:
            sector = node.sector
            self.updateNodesLockList[sector].acquire()
            if node in self.nodes[sector]["configured"]:
                self.nodes[sector]["configured"].remove(node)
            self.updateNodesLockList[sector].release()

        return count

    def fetch_nodes_from_sector(self, sector=1):
        """
        Fetches the nodes registered in a given sector.
        :param sector: the sector to be used in the queries.
        :return: a list of Node objects.
        """
        return self.db.fetch_nodes_from_sector(sector)

    def get_nodes_from_sector(self, sector=1, registered=True):
        """
        Returns the current state of registered nodes.
        :param sector: the sector to be used.
        :param registered: access either the registered node list or the un-registered list.
        :return: a list of Node objects.
        """
        self.updateNodesLockList[sector].acquire()
        nodes = self.nodes[sector]["configured"] if registered else self.nodes[sector]["unconfigured"]
        self.updateNodesLockList[sector].release()
        return nodes

    def get_node_by_address(self, ip_address, registered=True):
        """
        Returns the node with a given IP address.
        :param ip_address: the IP address to be used to search the node list.
        :param registered: access either the registered node list or the un-registered list.
        :return: the node with the IP address or None if such node is not found.
        :raise DataNotFoundError: Node object is not in the searched list.
        """
        from server.network.db import DataNotFoundError

        nodes = self.get_nodes_from_sector(Sector.get_sector_by_ip_address(ip_address), registered=registered)

        if ip_address in nodes:
            return nodes.index(ip_address)

        return DataNotFoundError("Node whose IP address is {} not found in sector {}".format(
            ip_address, Sector.get_sector_by_ip_address(ip_address)))
    
    def get_node_by_name(self, node_name):
        """
        Return a node by it's name.
        :param node_name: Name to look for.
        :return: the node or None.
        """
        return self.db.get_node_by_name(node_name)

    def is_ip_address_available(self, ip_address=None):
        return not (ip_address in self.get_node_by_address(ip_address=ip_address))

    def reboot_node(self, node: Node = None):
        """
        Reboots a given node.
        :param node: a Node instance object.
        """
        DaemonHostListener.get_instance().send_command(command=Command.REBOOT, address=node.ip_address)

        sector = node.sector

        self.updateNodesLockList[sector].acquire()

        if node in self.nodes[sector]["configured"]:
            index = self.nodes[sector]["configured"].index(node)
            self.nodes[sector]["configured"][index].update_state(NodeState.REBOOTING)
        elif node in self.nodes[sector]["unconfigured"]:
            index = self.nodes[sector]["unconfigured"].index(node)
            self.nodes[sector]["unconfigured"][index].update_state(NodeState.REBOOTING)

        self.updateNodesLockList[sector].release()

    # def update_ping_node(self, **kwargs):
    #     """
    #     Update the ping list.
    #     :param node: The node
    #     """
    #     self.db.
    #     pass

    def update_node(self, old_node: Node = None, new_node: Node = None):
        """
        Updates the mis-configured node with the data of the selected configured node.
        :param old_node: The node to be updated and to be assigned the new_node's configuration.
        :param new_node: A connected and unregistered node to serve as the source of the new configuration.
        """
        DaemonHostListener.get_instance().send_command(command=Command.SWITCH,
                                                address=old_node.ip_address, node=new_node)
        self.reboot_node(old_node)

    def update_ping_hosts(self, **kwargs): 
        """
        Updates a given node's counter.
        :param node_dict: Node dictionary representation.
        :param type_dict: Typé dictionary representation.
        """ 
        node_dict = kwargs.get('node_dict', None)
        type_dict = kwargs.get('type_dict', None)
        
        # if not node_dict:
        #     return
        
        t = Type()
        t.from_set(type_dict)

        node = Node()
        node.from_set(node_dict, t)
        self.db.update_ping_node_list(node = node)

        # sector = Sector.get_sector_by_ip_address(node.ip_address)

        # self.updateNodesLockList[sector].acquire()

        # is_host_connected = False
        # conflicted_host = False

        # if node.get_key() in self.nodes[sector]["configured"]:

        #     old_node = self.nodes[sector]["configured"][node.get_key()]
        #     old_node.counter = MAX_LOST_PING

        #     if node.name == old_node.name and node.type  == t:
        #         node.update_state(NodeState.CONNECTED)
        #         is_host_connected = True
        #     else:
        #         node.update_state(NodeState.MIS_CONFIGURED)
        #         conflicted_host = True

        # if not is_host_connected:

        #     available_type = self.find_type_by_name(host_type)

        #     if not available_type:
        #         available_type = Type(name=host_type, description="Unknown type.")

        #     if address in self.nodes[sector]["unconfigured"]:

        #         un_configured_node = self.nodes[sector]["unconfigured"][self.nodes[sector]["unconfigured"].index(address)]
        #         un_configured_node.counter = MAX_LOST_PING
        #         un_configured_node.name = name
        #         un_configured_node.type = available_type

        #         if conflicted_host:
        #             un_configured_node.update_state(NodeState.MIS_CONFIGURED)
        #         else:
        #             un_configured_node.update_state(NodeState.CONNECTED)

        #     else:
        #         new_unconfigured_node = Node(name=name, ip_address=address, state=NodeState.CONNECTED, type_node=available_type,
        #                                      sector=sector, counter=MAX_LOST_PING)
        #         if conflicted_host:
        #             new_unconfigured_node.update_state(NodeState.MIS_CONFIGURED)

        #         self.nodes[sector]["unconfigured"].append(new_unconfigured_node)

        # self.updateNodesLockList[sector].release()

    def stop_all(self):
        """
        Stops all scanning threads.
        """
        self.scan_nodes = False

    def check_ip_available(self, ip=None, name=None):
        """
        Check if a specific ip is available.
        :param ip: ip to be checked.
        :param name: node name.
        :return (bool: True/False, str: A simple text)
        @todo: this method deserver some love.
        """
        
        if ip is None or name is None:
            raise ValueError("Node name/ip is not defined.")

        node = self.db.get_node_by_address(node_address=ip)

        if node is None:
            return True, "No node with the ip {} is registered.".format(ip)
        else:
            if node.name == name:
                return True, "The ip {} is already belong to this node ({})".format(ip, name)

        raise ValueError("This ip {} is linked to another node ({})".format(ip, node.name))

    def validate_repository(self, rc_path: str = None, git_url: str = None, check_rc_local: bool = False):
        """
        Verify if the repository is valid.
        :param git_url:
        :param check_rc_local defaults to False. If true the existence of the rc.local file will be checked.
        :return: (True or False), ("Message")
        """
        return checkUrlFunc(git_url=git_url, rc_local_path=rc_path, check_rc_local=check_rc_local)

    def clone_repository(self, git_url=None, rc_local_path=None):
        """
        Clone the repository from git to the ftp server.
        :return: (True or False) , (message in case of Failure, SHA of the HEAD commit)
        """
        return cloneRepository(git_url=git_url, rc_local_path=rc_local_path, ftp_serv_location=self.sftp_home_dir)
