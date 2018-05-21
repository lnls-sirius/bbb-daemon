import threading

import redis

from common.entity.entities import Node, Type


class RedisPersistence():

    def __init__(self, host='10.0.6.70', port=6379):

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
            raise ValueError("Type object isn't fit to be persisted.")

        self.typesListMutex.acquire()
        if not self.db.exists(nType.name):
            self.db.lpush("types", nType.name)

        success = self.db.set(nType.name,
                              str({k: vars(nType)[k] for k in ("description", "color", "repoUrl", "rcLocalPath")}))

        self.typesListMutex.release()

        return success

    def appendNode(self, nNode: Node = None):
        """
        Append a Node
        :param nNode:
        :return:
        """
        if nNode is None or nNode.name is None or nNode.name == "":
            raise ValueError("Node object isn't fit to be persisted.")

        self.nodesListMutex.acquire()

        # Trying to add a node that exists in other sector
        if self.db.exists(nNode.name):
            node = eval(self.db.get(nNode.name))
            if nNode.sector != node["sector"]:
                self.nodesListMutex.release()
                return False

        if self.db.exists(nNode.ipAddress) and self.db.get(nNode.ipAddress) is not None:
            nodeName = self.db.get(nNode.ipAddress).decode("utf-8")
            if self.db.exists(nodeName) and self.db.exists(nodeName) is not None:
                node = eval(self.db.get(nodeName))

                # Trying to add a node that exists in other sector
                if nNode.sector != node["sector"]:
                    self.nodesListMutex.release()
                    return False

                self.db.delete(nodeName)
                self.db.lrem(name=nNode.sector, value=nodeName, count=0)

        if not self.db.exists(nNode.name):
            self.db.lpush(nNode.sector, nNode.name)

        nodeInfo = {"ipAddress": nNode.ipAddress, "type": nNode.type.name, "sector": nNode.sector,
                    "prefix": nNode.pvPrefix}

        success = self.db.set(nNode.name, str(nodeInfo))
        success = self.db.set(nNode.ipAddress, nNode.name)

        self.nodesListMutex.release()

        return success

    def fetchTypes(self):

        self.typesListMutex.acquire()

        typesList = []
        typeMap = {}
        typeMap.setdefault("")

        typesDb = self.db.lrange("types", 0, -1)

        if typesDb is not None:
            for tName in typesDb:
                typeName = tName.decode("utf-8")
                typeMap = self.db.get(typeName)
                if typeMap is not None:
                    typeMap = eval(typeMap)
                    aType = Type(name=typeName, color=typeMap["color"], repoUrl=typeMap.get("repoUrl", ""),
                                 rcLocalPath=typeMap.get("rcLocalPath", "init/rc.local"),
                                 description=typeMap["description"])
                else:
                    aType = Type()

                typesList.append(aType)

            self.typesListMutex.release()
        return typesList

    def fetchNodesFromSector(self, sector="1"):
        self.nodesListMutex.acquire()

        nodesDb = self.db.lrange(sector, 0, -1)
        nodes = []

        for nNames in nodesDb:
            nName = nNames.decode("utf-8")

            nodeMap = {}
            typeMap = {}
            nodeMap.setdefault("")
            typeMap.setdefault("")

            nodeMap = self.db.get(nName)
            if nodeMap is not None:
                nodeMap = eval(nodeMap)
                typeMap = self.db.get(nodeMap["type"])

                if typeMap is not None:
                    typeMap = eval(self.db.get(nodeMap["type"]))
                    nType = Type(name=nodeMap["type"], color=typeMap["color"], repoUrl=typeMap.get("repoUrl", ""),
                                 rcLocalPath=typeMap.get("rcLocalPath", "init/rc.local"),
                                 description=typeMap["description"])
                    pass
                else:
                    nType = Type()

                nodes.append(Node(name=nName, ip=nodeMap["ipAddress"], typeNode=nType, sector=sector,
                                  pvPrefix=nodeMap.get("prefix", "")))

        self.nodesListMutex.release()
        return nodes

    def removeType(self, typeName):
        self.typesListMutex.acquire()

        if self.db.exists(typeName):
            self.db.delete(typeName)
            self.db.lrem(name="types", value=typeName, count=0)

        self.typesListMutex.release()

    def removeNodeFromSector(self, node: Node):
        count = 0

        if node is None:
            return count

        self.nodesListMutex.acquire()

        print(node)

        if self.db.exists(node.name):
            self.db.delete(node.name)
            self.db.delete(node.ipAddress)
            count = self.db.lrem(name=node.sector, value=node.name, count=0)
        elif self.db.exists(node.ipAddress):
            self.db.delete(node.ipAddress)
            count = self.db.lrem(name=node.sector, value=node.ipAddress, count=0)

        self.nodesListMutex.release()

        return count
