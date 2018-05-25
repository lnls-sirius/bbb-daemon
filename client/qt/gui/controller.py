import threading

from comm.commandinterface import CommandInterface
from common.entity.entities import Sector


class GUIController():

    def __init__(self, server="localhost"):
        self.commandInterface = CommandInterface(serverAddress=server)

        self.sectors = Sector.sectors()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes[sector] = {"configured": [], "unconfigured": []}
            self.updateNodesLockList[sector] = threading.Lock()

        self.types = []
        self.typeLock = threading.Lock()

    def switch(self, registeredNode, unregisteredNode):
        return self.commandInterface.switch(registeredNode, unregisteredNode)

    def reboot(self, registeredNode):
        return self.commandInterface.reboot(registeredNode)

    def getNodesFromSector(self, sector, registered=True):
        return self.commandInterface.getNodesFromSector(sector, registered)

    def fetchTypes(self):
        return self.commandInterface.fetchTypes()

    def appendType(self, newType):
        return self.commandInterface.appendType(newType)

    def removeType(self, typeName):
        self.commandInterface.removeType(typeName)

    def appendNode(self, node):
        return self.commandInterface.appendNode(node)

    def removeNodeFromSector(self, node):
        return self.commandInterface.removeNodeFromSector(node)
