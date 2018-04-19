from common.entity.entities import Command, Node, NodeState, Type

import redis
import threading

class RedisPersistence ():

    def __init__ (self, host = 'localhost', port = 6379):

        self.db = redis.StrictRedis (host = host, port = port, db = 0)

        self.typesListMutex = threading.Lock ()
        self.nodesListMutex = threading.Lock ()

    def appendType (self, newType = None):

        typesList = self.fetchTypes ()

        self.typesListMutex.acquire ()

        for index, t in enumerate (typesList):
            if t.name == newType.name:
                self.typesListMutex.release ()
                return self.db.lset ("types", index, str (newType.__dict__ ()))

        success = self.db.lpush ("types", str (newType.__dict__ ()))

        self.typesListMutex.release ()

        return success

    def appendNode (self, newNode) :

        nodes = self.fetchNodesFromSector (newNode.sector)

        self.nodesListMutex.acquire ()

        for index, node in enumerate(nodes):
            if node.name == newNode.name or node.ipAddress == newNode.ipAddress:
                self.nodesListMutex.release ()
                return (index, self.db.lset (newNode.sector, index, str (newNode.__dict__ ())))

        success = self.db.lpush (newNode.sector, str (newNode.__dict__ ()))

        self.nodesListMutex.release ()

        return (-1, success)

    def fetchTypes (self):

        self.typesListMutex.acquire ()

        typesList = []

        for t in self.db.lrange ("types", 0, -1):
            tDict = eval (t)
            typesList.append (Type (name = tDict["name"], \
                                    color = tDict ["color"], \
                                    description = tDict ["description"]))

        self.typesListMutex.release ()

        return typesList

    def removeType (self, typeName):

        typesList = self.fetchTypes ()

        self.typesListMutex.acquire ()

        success = False

        for index, t in enumerate (typesList):
            if t.name == typeName:
                success = self.db.lset ("types", index, "_DELETE_")
                break

        print (self.db.lrem (name = "types", value = "_DELETE_", count = 0))

        self.typesListMutex.release ()

        return False

    def removeNodeFromSector (self, node):

        nodes = self.fetchNodesFromSector (node.sector)

        self.nodesListMutex.acquire ()
        indexes = []

        for index, n in enumerate (nodes):
            if node.name == n.name:
                self.db.lset (node.sector, index, "_DELETE_")
                indexes.append (index)

        count = self.db.lrem (name = node.sector, value = "_DELETE_", count = 0)

        self.nodesListMutex.release ()

        return count, indexes

    def fetchNodesFromSector (self, sector = "1"):

        self.nodesListMutex.acquire ()

        nodesDb = self.db.lrange (sector, 0, -1)
        nodes = []

        for nodeDb in nodesDb:

            nodeDict = eval (nodeDb)
            nodeType = Type (name = nodeDict ["type"]["name"], \
                             color = nodeDict ["type"]["color"], \
                             description = nodeDict ["type"]["description"])

            node = Node (name = nodeDict ["name"], ip = nodeDict ["ip"], \
                         typeNode = nodeType, sector = nodeDict ["sector"])
            nodes.append (node)

        self.nodesListMutex.release ()

        return nodes
