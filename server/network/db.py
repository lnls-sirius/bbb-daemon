import ast
import msgpack
import redis
import threading
import logging

from common.entity.entities import Node, Type, PING_NODES, PING_KEY_PREFIX, EXPECTED_NODES, EXPECTED_KEY_PREFIX
from common.entity.metadata import Singleton

logger = logging.getLogger()

class DifferentSectorNodeError(Exception):
    """
    Exception raised when the user attemps to add a node in sector Y that is already
    included in the database in another sector.
    """
    pass

class DataNotFoundError(Exception):
    """
    Exception raised when the user attempts to fetch a node or a type that does not exist.
    """
    pass


class RedisPersistence(metaclass=Singleton):
    """
    A class to persist data to a Redis DB instance. The database architecture is composed of the following
    lists [key, [...]] and key-value pairs:

    + [sector_id_1, [node_name_1, node_name_3, ...]]
    + [sector_id_2, [node_name_2, node_name_8, ...]]
    + ...
    + [sector_id_y, [node_name_9, ...]]

    + [node_name_1, node_value_1]
    + [node_name_2, node_value_2]
    + ...
    + [node_name_m, node_value_m]
    """

    def __init__(self, host: str, port: int, redis_db = 0):
        """
        Constructor method. Receives host's address and port.
        :param host: Host's address.
        :param port: Host's TCP port.
        """
        self.db = redis.StrictRedis(host=host, port=port, db=redis_db)
        # The following mutexes control the concurrent access to the database. Many clients can
        # request data at the same time.
        # self.typesListMutex = threading.Lock()
        self.nodesListMutex = threading.Lock()
        self.pingNodesListMutex = threading.Lock()
        self.expectedNodesListMutex = threading.RLock()

        logger.info('Connected to redis at %s:%s using db %s' % (host, port, redis_db))


    def update_expected_node_list(self, expected_nodes):
        """
        Receives a dictionary of ip_address and type_code. Add to redis.
        :expected_nodes Dictionary: Dictionary, key(str: ip_address) value(int: Type)
        """
        if expected_nodes:
            with self.expectedNodesListMutex:
                pipeline = self.db.pipeline()
                for ip_address, type_code in expected_nodes.items():
                    pipeline.sadd(EXPECTED_NODES, '{}:{}'.format(EXPECTED_KEY_PREFIX, ip_address))
                    pipeline.set('{}:{}'.format(EXPECTED_KEY_PREFIX, ip_address), type_code)
                pipeline.execute()


    def clear_ping_node_list(self):
        """
        Clear expired nodes from the pingging nodes list.
        """
        self.pingNodesListMutex.acquire()
        ping_nodes = self.db.smembers(PING_NODES)
        if ping_nodes:
            for n_key in ping_nodes:
                if not self.db.exists(n_key):
                    self.db.srem(PING_NODES, n_key)
        self.pingNodesListMutex.release()

    def update_ping_node_list(self, **kwargs):
        """
        Receives a pinging node
        :node Node: A node.
        """
        node = kwargs.get('node', None)
        if node is None or node.name is None or node.name == "":
            raise TypeError("Node given as parameter is None or its name is not valid.")

        self.pingNodesListMutex.acquire()

        k, n = node.to_dict()
        pipeline = self.db.pipeline()
        pipeline.sadd(PING_NODES, node.get_ping_key())
        pipeline.set(node.get_ping_key(), n)
        pipeline.expire(node.get_ping_key(), Node.EXPIRE_TIME)
        pipeline.execute()

        self.pingNodesListMutex.release()

    def get_ping_nodes(self, *args, **kwargs):
        "Get all ping nodes"
        nodes =  []
        for node in self.db.smembers(PING_NODES):
            bin_node = self.db.get(node)
            if bin_node == None:
                continue
            nodes.append(ast.literal_eval(bin_node.decode('utf-8')))
        return nodes

    def get_ping_node(self, **kwargs):
        """
        Get a ping node. Pass a node object.
        :param key: Ping key to look for.
        """
        key = kwargs.get('key', None)
        node = None
        if key:
            self.pingNodesListMutex.acquire()
            # if exists ...
            self.db.sismember(PING_NODES, key)
            content_as_string = self.db.get(key)
            if content_as_string != None:
                res = ast.literal_eval(content_as_string.decode('utf-8'))
                node = Node()
                node.from_dict(res['n'])
                # node.from_dict(res['n'], res['t'])
            self.pingNodesListMutex.release()
        return node

    # def remove_ping_node(self, **kwargs):
    #     # Todo: Remove Ping:Node
    #     pass
    def get_ping_node_keys(self):
        """
        Get all ping nodes.
        """
        return self.db.keys(pattern= PING_KEY_PREFIX + Node.KEY_PREFIX + '*')

    def get_node_keys(self):
        """
        Get all nodes.
        """
        return self.db.keys(pattern=Node.KEY_PREFIX + '*')

    def append_node(self, new_node: Node = None):
        """
        Append a new node to the database, adding it to sector list accordingly.
        :param new_node: the node to be added.
        :return: True if the node was successfully added. False, otherwise.
        :raise DifferentSectorNodeError: the user tries to append a node that is already in another sector.
        :raise TypeError: node given as parameter is None or its name is not valid.
        """
        if new_node is None or new_node.name is None or new_node.name == "":
            raise TypeError("Node given as parameter is None or its name is not valid.")

        self.nodesListMutex.acquire()

        # Trying to add a node that exists in other sector
        try:
            old_node = self.get_node_by_name(new_node.name)
            # node already exists
            if old_node.sector != new_node.sector:
                # node was initially added on another sector.
                self.nodesListMutex.release()
                raise DifferentSectorNodeError("Cannot append node to sector {} if it already belongs to {}"
                                               .format(new_node.sector, old_node.sector))

            # Remove old node
            self.db.delete(old_node.get_key())
            self.db.lrem(name=new_node.sector, value=old_node.get_key(), count=0)

        except DataNotFoundError:
            pass

        if not self.db.exists(new_node.get_key()):
            self.db.lpush(new_node.sector, new_node.get_key())

        node_key, node_value = new_node.to_dict()

        self.db.set(node_key, node_value)
        success = self.db.set(str(new_node.ip_address), new_node.get_key())

        self.nodesListMutex.release()

        return success

    def get_node_by_address(self, node_address=None):
        """
        Searches a node by its IP address.
        :param node_address: the node's ip address.
        :return: None if node was not found or the Node instance, otherwise.
        :raise TypeError: Node given as parameter is None.
        :raise DataNotFoundError: Node instance has not been found.
        """

        if node_address is None:
            raise TypeError("Node given as parameter is None.")

        node_name = self.db.get(str(node_address)).decode('utf-8')

        if node_name is not None:
            if str(node_name).startswith(Node.KEY_PREFIX):
                node_name = node_name[Node.KEY_PREFIX_LEN:]
                return self.get_node_by_name(node_name)

        raise DataNotFoundError("Node whose IP address is {} hasn't been found in the db.".format(node_address))

    def get_node_by_name(self, node_name: str):
        """
        Search a node instance by it's name.
        :param node_name: the node's name to search.
        :return: Node instance whose name is node_name.
        :raise TypeError: Node name given as parameter is None.
        :raise DataNotFoundError: Node instance has not been found.
        """

        if node_name is None:
            raise TypeError("No node name has been given. node_name is None.")

        content_as_string = self.db.get(Node.KEY_PREFIX + node_name)

        if content_as_string is not None:
            content_as_dict = ast.literal_eval(content_as_string.decode('utf-8'))
            if type(content_as_dict) == dict:
                # node_type = self.get_type_by_name(content_as_dict.get('type', ''))
                n = Node()
                n.from_dict(node_dict=content_as_dict)
                # n.from_dict(node_dict=content_as_dict, node_type=node_type)
                return n
            else:
                raise TypeError("Type obtained from redis {} after conversion isn't a dictionary.".format(Node.KEY_PREFIX + node_name))

        raise DataNotFoundError("Node whose name is {} hasn't been found in the db.".format(node_name))

    def fetch_nodes_from_sector(self, sector="1"):
        """
        Returns all nodes from a given sector saved in the database so far.
        :param sector: the sector to select the nodes
        :return: A list containing all nodes in the sector passed as parameter.
        :raise DataNotFoundError: the db query returns None instead of a list.
        """
        pass

    def node_exist(self, **kwargs):
        """
        Check if a node exist.
        :param node: Type Node()
        :param ip_address: Ip address string
        """
        node = kwargs.get('node', None)
        ip_address = kwargs.get('ip_address', None)

        if node:
            return self.db.exists(node.get_key())
        if ip_address:
             return self.db.exists(Node.get_key_static(ip_address))


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
            self.db.delete(str(node.ip_address))
            count = self.db.lrem(name=node.sector, value=node.get_key(), count=0)
        elif self.db.exists(str(node.ip_address)):
            # Remove defunct entries
            self.db.delete(str(node.ip_address))
            count = self.db.lrem(name=node.sector, value=str(node.ip_address), count=0)

        self.nodesListMutex.release()

        return count

