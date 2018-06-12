import ast
import threading

import redis

from common.entity.entities import Node, Type


class RedisPersistence():

    def __init__(self, host: str, port: int):

        self.db = redis.StrictRedis(host=host, port=port, db=0)

        self.typesListMutex = threading.Lock()
        self.nodesListMutex = threading.Lock()

    def appendType(self, nType: Type = None):
        """
        Append a Type
        :param nType:
        :return:
        """
        if nType is None or nType.name is None or nType.name == "":
            print("Type object isn't fit to be persisted. {}".format(nType))
            return False

        self.typesListMutex.acquire()
        if not self.db.exists(nType.get_key()):
            self.db.lpush("types", nType.get_key())

        key, val = nType.toSet()
        success = self.db.set(key, val)

        self.typesListMutex.release()

        return success

    def appendNode(self, nNode: Node = None):
        """
        Append a Node
        :param nNode:
        :return: True or False
        """
        if nNode is None or nNode.name is None or nNode.name == "":
            print("Node Invalid  {}".format(nNode))
            return False

        self.nodesListMutex.acquire()
        try:
            # Trying to add a node that exists in other sector
            oldNode = self.getNode(nNode.name)
            if oldNode is not None:
                # Node already exists
                if oldNode.sector != nNode.sector:
                    # Node exists on another sector. Abort !
                    self.nodesListMutex.release()
                    return False

                self.db.delete(oldNode.get_key())
                self.db.lrem(name=nNode.sector, value=oldNode.get_key(), count=0)

            if not self.db.exists(nNode.get_key()):
                self.db.lpush(nNode.sector, nNode.get_key())

            k, v = nNode.toSet()
            success = self.db.set(k, v)
            success = self.db.set(nNode.ipAddress, nNode.get_key())

        except Exception as e:
            print("Failed to append node ! {}".format(e))
            success = False
        self.nodesListMutex.release()

        return success

    def fetchTypes(self):
        self.typesListMutex.acquire()
        typesList = []
        try:
            typesDb = self.db.lrange("types", 0, -1)
            if typesDb is not None:
                for tKey in typesDb:
                    tName = Type.get_name_from_key(tKey)
                    aType = self.getType(tName.decode("utf-8"))
                    typesList.append(aType)
        except Exception as e:
            print("{}".format(e))

        self.typesListMutex.release()
        return typesList

    def getNode(self, nodeName: str):
        aNode = None
        try:
            nodeMap = self.db.get(Node.key_prefix + nodeName)

            if nodeMap is not None:
                nM = nodeMap.decode('utf-8')
                nM = ast.literal_eval(nM)
                type = self.getType(nM.get('type', ''))
                aNode = Node(typeNode=type, name=nodeName)
                aNode.fromSet(nodeMap)

        except Exception as e:
            print("{}".format(e))

        return aNode

    def getType(self, typeName: str):
        aType = None
        try:
            aType = Type(name=typeName)
            aType.fromSet(str_dic=self.db.get(aType.get_key()))
        except Exception as e:
            print("{}".format(e))

        return aType

    def fetchNodesFromSector(self, sector="1"):
        self.nodesListMutex.acquire()
        nodes = []

        nodesDb = self.db.lrange(sector, 0, -1)

        for nKey in nodesDb:
            nKey = nKey.decode("utf-8")
            nName = Node.get_name_from_key(nKey)
            nNode = self.getNode(nName)
            if nNode:
                nodes.append(nNode)

        self.nodesListMutex.release()
        return nodes

    def removeType(self, typeName):

        self.typesListMutex.acquire()
        typeName = Type.key_prefix + typeName
        if self.db.exists(typeName):
            self.db.delete(typeName)
            self.db.lrem(name="types", value=typeName, count=0)

        self.typesListMutex.release()

    def removeNodeFromSector(self, node: Node):
        count = 0
        if node is None:
            return count

        self.nodesListMutex.acquire()
        print("Node to be Removed {}".format(node))

        if self.db.exists(node.get_key()):
            self.db.delete(node.get_key())
            self.db.delete(node.ipAddress)
            count = self.db.lrem(name=node.sector, value=node.get_key(), count=0)
        elif self.db.exists(node.ipAddress):
            self.db.delete(node.ipAddress)
            count = self.db.lrem(name=node.sector, value=node.ipAddress, count=0)

        self.nodesListMutex.release()

        return count
