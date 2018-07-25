from common.entity.entities import Node, Type
from common.entity.metadata import Singleton

import ast
import redis
import threading


class DifferentSectorNodeException(Exception):
    """
    Exception raised when the user attemps to add a node in sector Y that is already
    included in the database in another sector.
    """
    pass


class RedisPersistence(metaclass=Singleton):
    """
    A class to persist data to a Redis DB instance. The database architecture is composed of the following
    lists [key, [...]] and key-value pairs:

    + ['types', [type_key_1, type_key_2, ..., type_key_n]]
    + [type_key_1, type_value_1]
    + [type_key_1, type_value_2]
    + ...
    + [type_key_n, type_value_n]

    + [sector_id_1, [node_name_1, node_name_3, ...]]
    + [sector_id_2, [node_name_2, node_name_8, ...]]
    + ...
    + [sector_id_y, [node_name_9, ...]]

    + [node_name_1, node_value_1]
    + [node_name_2, node_value_2]
    + ...
    + [node_name_m, node_value_m]
    """

    def __init__(self, host: str, port: int):
        """
        Constructor method. Receives host's address and port.
        :param host: Host's address.
        :param port: Host's TCP port.
        """

        self.db = redis.StrictRedis(host=host, port=port, db=0)

        # The following mutexes control the concurrent access to the database. Many clients can
        # request data at the same time.
        self.typesListMutex = threading.Lock()
        self.nodesListMutex = threading.Lock()

    def append_type(self, new_type: Type = None):
        """
        Append a new type to the database, updating its value if it already exists.
        :param new_type: the type to be appended.
        :return: True if the type was successfully added. False, otherwise.
        """

        if new_type is None or new_type.name is None or new_type.name == "":
            print("Type object isn't fit to be persisted. {}".format(new_type))
            return False

        self.typesListMutex.acquire()
        if not self.db.exists(new_type.get_key()):
            self.db.lpush("types", new_type.get_key())

        key, val = new_type.to_set()
        success = self.db.set(key, val)

        self.typesListMutex.release()

        return success

    def append_node(self, new_node: Node = None):
        """
        Append a new node to the database, adding it to sector list accordingly.
        :param new_node: the node to be added.
        :return: True if the node was successfully added. False, otherwise.
        """
        if new_node is None or new_node.name is None or new_node.name == "":
            print("Node Invalid  {}".format(new_node))
            return False

        self.nodesListMutex.acquire()

        # Trying to add a node that exists in other sector
        old_node = self.get_node_by_name(new_node.name)

        if old_node is not None:
            # node already exists
            if old_node.sector != new_node.sector:
                # node was initially added on another sector. Abort !
                self.nodesListMutex.release()
                raise DifferentSectorNodeException("Cannot append node to sector {} if it already belongs to {}"
                                                   .format(new_node.sector, old_node.sector))

            # Remove old node
            self.db.delete(old_node.get_key())
            self.db.lrem(name=new_node.sector, value=old_node.get_key(), count=0)

        if not self.db.exists(new_node.get_key()):
            self.db.lpush(new_node.sector, new_node.get_key())

        node_key, node_value = new_node.to_set()

        self.db.set(node_key, node_value)
        success = self.db.set(new_node.ipAddress, new_node.get_key())

        self.nodesListMutex.release()

        return success

    def get_node_by_address(self, node_address: str = None):
        """
        Searches a node by its IP address.
        :param node_address: the node's ip address.
        :return: None if node was not found or the Node instance, otherwise.
        """

        if node_address is None:
            return None

        node_name = self.db.get(node_address).decode('utf-8')

        if node_name is not None:
            if str(node_name).startswith(Node.key_prefix):
                node_name = node_name[Node.key_prefix_len:]
                return self.get_node_by_name(node_name)

        return None

    def get_node_by_name(self, node_name: str):
        """
        Search a node instance by its name.
        :param node_name: the node's name to search.
        :return: None if node was not found or the Node instance, otherwise.
        """

        ret_node = None
        content_as_string = self.db.get(Node.key_prefix + node_name)

        if content_as_string is not None:
            content_as_dict = ast.literal_eval(content_as_string.decode('utf-8'))
            node_type = self.get_type_by_name(content_as_dict.get('type', ''))

            ret_node = Node(type_node=node_type, name=node_name)
            ret_node.from_set(content_as_string)

        return ret_node

    def get_type_by_name(self, type_name: str):
        """
        Search a type by name.
        :param type_name:  the type's name to search.
        :return: None if the type was not found or the Type object, otherwise.
        """

        if self.db.exists(Type.key_prefix + type_name):
            ret_type = Type(name=type_name)
            ret_type.from_set(str_dic=self.db.get(Type.key_prefix + type_name))
            return ret_type

        return None

    def fetch_types(self):
        """
        Returns all types registered in the database so far.
        :return: A list containing all types in the database.
        """

        self.typesListMutex.acquire()

        ret_list = []

        type_list = self.db.lrange("types", 0, -1)
        if type_list is not None:
            for type_key in type_list:
                type_name = Type.get_name_from_key(type_key)
                if type_name != '':
                    ret_list.append(self.get_type_by_name(type_name.decode("utf-8")))

        self.typesListMutex.release()
        return ret_list

    def fetch_nodes_from_sector(self, sector="1"):
        """
        Returns all node from sector registered in the database so far.
        :param sector: the sector to select the nodes
        :return: A list containing all nodes in the sector passed as parameter'.
        """
        self.nodesListMutex.acquire()
        ret_nodes = []

        nodes_db = self.db.lrange(sector, 0, -1)

        for node_key in nodes_db:
            node_name = Node.get_name_from_key(node_key.decode("utf-8"))
            node = self.get_node_by_name(node_name)
            if node:
                ret_nodes.append(node)

        self.nodesListMutex.release()
        return ret_nodes

    def remove_type_by_name(self, type_name):
        """
        Removes a type from the database.
        :param type_name: the type's name.
        """

        count = 0

        self.typesListMutex.acquire()
        type_name = Type.key_prefix + type_name
        if self.db.exists(type_name):
            self.db.delete(type_name)
            count = self.db.lrem(name="types", value=type_name, count=0)

        self.typesListMutex.release()

        return count

    def remove_node_from_sector(self, node: Node):
        """
        Removes a node from a sector.
        :param node: Node instance to be removed.
        """

        if node is None:
            return 0

        count = 0

        self.nodesListMutex.acquire()

        if self.db.exists(node.get_key()):
            self.db.delete(node.get_key())
            self.db.delete(node.ipAddress)
            count = self.db.lrem(name=node.sector, value=node.get_key(), count=0)
        elif self.db.exists(node.ipAddress):
            # Remove defunct entries
            self.db.delete(node.ipAddress)
            count = self.db.lrem(name=node.sector, value=node.ipAddress, count=0)

        self.nodesListMutex.release()

        return count
