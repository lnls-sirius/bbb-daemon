from client.qt.comm.commandinterface import CommandNetworkInterface
from common.entity.entities import Sector
from common.entity.metadata import Singleton
import threading


class QtInterfaceController(metaclass=Singleton):
    """
    Qt interface controller class.
    @todo evaluate if this class is needed indeed.
    """

    def __init__(self):
        """
        Initializes the data structures reflecting the Redis db.
        :param server: the server's IP address.
        :param server_port: the server's port.
        """
        self.command_interface = CommandNetworkInterface.get_instance()

        self.sectors = Sector.sectors()

        self.nodes = {}
        self.update_nodes_lock_list = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": [], "unconfigured": []}
            self.update_nodes_lock_list[sector] = threading.Lock()

        self.types = []
        self.typeLock = threading.Lock()

    def switch(self, registered_node, unregistered_node):
        return self.command_interface.switch(registered_node, unregistered_node)

    def reboot(self, registered_node):
        return self.command_interface.reboot(registered_node)

    def get_nodes_from_sector(self, sector, registered=True):
        return self.command_interface.get_nodes_from_sector(sector, registered)

    def fetch_types(self):
        return self.command_interface.fetch_types()

    def append_type(self, new_type):
        return self.command_interface.manage_types(new_type)

    def remove_type(self, type_name):
        self.command_interface.remove_type_by_name(type_name)

    def append_node(self, node):
        return self.command_interface.manage_nodes(node)

    def remove_node_from_sector(self, node):
        return self.command_interface.remove_node_from_sector(node)
