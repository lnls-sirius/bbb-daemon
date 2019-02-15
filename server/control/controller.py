from common.entity.definition import MAX_LOST_PING, PING_INTERVAL
from common.entity.entities import Command, NodeState, Sector, Node, Type, ConfiguredNode
from common.entity.metadata import Singleton
from common.util.git import cloneRepository, checkUrlFunc
from common.network.utils import get_valid_address
from server.network.daemoninterface import DaemonHostListener

import logging
import threading
import time
import os
import sys
import ipaddress

device_list_path = sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../device-list'))
ip_type_dict = {}
ip_set = set()
missing_ips = set()

with open(device_list_path, 'r') as f:
    for line in f:
        ip, network, type_code = line.split(' ')
        ip_type_dict['ip'] = ConfiguredNode(ip_address=ip, ip_network=network, type_code=type_code)
        ip_set.add(ip)

class ServerController(metaclass=Singleton):
    """
    The main class of the server. It controls the server state and the client requests.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes a controller.
        """
        from server.network.db import RedisPersistence

        self.db = RedisPersistence.get_instance()
        self.sectors = Sector.sectors()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": self.fetch_nodes_from_sector(sector),
                                  "unconfigured": []}
            self.updateNodesLockList[sector] = threading.Lock()
        self.missing_ips_lock = threading.RLock()
        self.logger = logging.getLogger()
        # self.logger = logging.getLogger('ServerController')

        self.scan_nodes = True
        self.updateNodesThread = threading.Thread(target=self.scan_nodes_worker)
        self.updateNodesThread.start()

        self.db.update_expected_node_list(expected_nodes=ip_type_dict)

    def get_types(self):
        return Type.get_types()

    def get_sectors_dict(self):
        return Sector.get_sectors_dict()

    def find_type_by_name(self, type_name):
        """
        Look up a Type instance by its name.
        :param type_name: a Type's name
        :return: a Type instance or None.
        """
        if type_name == None:
            return Type(code=Type.UNDEFINED)
        for _type in Type.TYPES:
            if type_name.upper() in _type.name.upper():
                return _type
        return None
        # return self.db.get_type_by_name(type_name)

    def update_ping_hosts(self, **kwargs):
        """
        Updates a given node's counter.
        :param node_dict: Node dictionary representation.
        :param ip: IpAddress.
        """
        node_dict = kwargs.get('node_dict', None)
        ip_address = kwargs.get('ip', None)

        node = Node()
        node.from_dict(node_dict)

        self.db.update_ping_node_list(node=node)

        if ip_address == None:
            return

        if type(ip_address) == str:
            ip_address = ipaddress.ip_address(ip_address)

        with self.missing_ips_lock:
            match = []
            # Check if this ip is at the same network as one of the missing ones
            for missing_ip in missing_ips:
                if ip_address in ip_type_dict[missing_ip].ip_network:
                    # Check the type received and the expected
                    if node.type.code == ip_type_dict[missing_ip].type_code:
                        match.append(ip_address)
            
            # Find the lowest match
            # Set the new ip
            

            # Remove the missing ip from redis and from the missing ip list
            pass

    def scan_nodes_worker(self):
        """
        It will loop though the ping nodes and update the configured nodes accordingly.
        """
        global missing_ips

        self.logger.info("Starting node scanning thread.")

        while self.scan_nodes:
            self.db.clear_ping_node_list()

            nodes = self.db.get_ping_nodes()
            keys = self.db.get_node_keys()

            with self.missing_ips_lock:
                missing_ips = ip_set - set(keys)

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

    def set_hostname(self, **kwargs):
        """
        Set the node hostname. Can raise an exception.
        :param ip: Target Ip.
        :param hostname: New Hostname.
        """
        DaemonHostListener.get_instance().send_command(command=Command.SET_HOSTNAME, address=kwargs['ip'], hostname=kwargs['hostname'])

    def set_ip(self, ip, ip_new, gateway = None, mask : str = None, network : ipaddress.ip_network = None):
        """
        Set the node hostname. Can raise an exception.
        :param ip: Target Ip.
        :param ip_new: New IP.
        :param mask: Mask.
        :param network: Network.
        :param gateway: Gateway.
        """
        if mask == None and network == None:
            raise ValueError('No network mask information.')
        if gateway == None and network == None:
            raise ValueError('No gateway information.')
        if ip == None:
            raise ValueError('No target ip.')
        if ip_new == None:
            raise ValueError('No new ip.')

        if gateway == None:
            gateway = network.network_address + 1
        if mask == None and network != None:
            mask = network.netmask

        DaemonHostListener.get_instance().send_command(
            command=Command.SET_IP,
            address=get_valid_address(ip),
            ip_new=get_valid_address(ip_new),
            mask=get_valid_address(mask))

    def reboot_node(self, **kwargs):
        """
        Reboots a given node.
        :param node: a Node instance object.
        """
        DaemonHostListener.get_instance().send_command(command=Command.REBOOT, address=kwargs['ip'])

    def update_node(self, old_node: Node = None, new_node: Node = None):
        """
        Updates the mis-configured node with the data of the selected configured node.
        :param old_node: The node to be updated and to be assigned the new_node's configuration.
        :param new_node: A connected and unregistered node to serve as the source of the new configuration.
        """
        DaemonHostListener.get_instance().send_command(command=Command.SWITCH,
                                                address=old_node.ip_address, node=new_node)
        self.reboot_node(old_node)

    def get_ping_nodes(self):
        return self.db.get_ping_nodes()


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
                return True, "The {} already belong to this node ({})".format(ip, name)

        raise ValueError("This ip {} is linked to another node ({})".format(ip, node.name))