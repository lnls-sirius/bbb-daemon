from common.entity.entities import Command, Node, NodeState, Type

import redis
import threading

class RedisPersistence ():

    def __init__ (self, host = 'localhost', port = 6379):

        self.db = redis.StrictRedis (host = host, port = port, db = 0)

        self.typesListMutex = threading.Lock ()
        self.nodesListMutex = threading.Lock ()

    def appendType (self, nType = None):

        self.typesListMutex.acquire ()

        if not self.db.exists (nType.name):
            self.db.lpush ("types", nType.name)

        success = self.db.set (nType.name, str ({k: vars (nType)[k] for k in ("description", "color")}))

        self.typesListMutex.release ()

        return success

    def appendNode (self, nNode = None) :

        self.nodesListMutex.acquire ()

        # Trying to add a node that exists in other sector
        if self.db.exists (nNode.name):
            node = eval (self.db.get (nNode.name))
            if nNode.sector != node ["sector"]:
                self.nodesListMutex.release ()
                return False

        if self.db.exists (nNode.ipAddress):
            nodeName = self.db.get (nNode.ipAddress).decode ("utf-8")
            node = eval (self.db.get (nodeName))

            # Trying to add a node that exists in other sector
            if nNode.sector != node ["sector"]:
                self.nodesListMutex.release ()
                return False

            self.db.delete (nodeName)
            self.db.lrem (name = nNode.sector, value = nodeName, count = 0)

        if not self.db.exists (nNode.name):
            self.db.lpush (nNode.sector, nNode.name)

        nodeInfo = {"ipAddress" : nNode.ipAddress, "type" : nNode.type.name, "sector" : nNode.sector, "prefix": nNode.pvPrefix}

        success = self.db.set (nNode.name, str (nodeInfo))
        success = self.db.set (nNode.ipAddress, nNode.name)

        self.nodesListMutex.release ()

        return success

    def fetchTypes (self):

        self.typesListMutex.acquire ()

        typesList = []

        for tName in self.db.lrange ("types", 0, -1):
            tName = tName.decode ("utf-8")
            typeInfo = eval (self.db.get(tName))
            typesList.append (Type (name = tName, color = typeInfo ["color"], description = typeInfo ["description"]))

        self.typesListMutex.release ()

        return typesList


    def fetchNodesFromSector (self, sector = "1"):

        self.nodesListMutex.acquire ()

        nodesDb = self.db.lrange (sector, 0, -1)
        nodes = []

        for nodeDb in nodesDb:
            nName = nodeDb.decode ("utf-8")
            nodeInfo = eval (self.db.get(nName))
            typeInfo = eval(self.db.get(nodeInfo ["type"]))
            nodeType = Type (name = nodeInfo ["type"], color = typeInfo ["color"], description = typeInfo ["description"])

            try:
                prefix = nodeInfo ["prefix"]
            except:
                prefix = ""

            nodes.append (Node (name = nName, ip = nodeInfo ["ipAddress"], typeNode = nodeType, sector = sector, pvPrefix = prefix))

        self.nodesListMutex.release ()
        return nodes

    def removeType (self, typeName):

        self.typesListMutex.acquire ()

        if self.db.exists (typeName):
            self.db.delete (typeName)
            self.db.lrem (name = "types", value = typeName, count = 0)

        self.typesListMutex.release ()

    def removeNodeFromSector (self, node):

        self.nodesListMutex.acquire ()

        print (node)

        count = 0

        if self.db.exists (node.name):
            self.db.delete (node.name)
            self.db.delete (node.ipAddress)
            count = self.db.lrem (name = node.sector, value = node.name, count = 0)

        self.nodesListMutex.release ()

        return count
