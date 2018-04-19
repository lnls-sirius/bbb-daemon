from comm.commandinterface import CommandInterface
from common.entity.entities import Sector

import threading
import time

class GUIController ():

    def __init__ (self):

        self.commandInterface = CommandInterface ()

        self.sectors = Sector.sectors ()

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes [sector] = { "configured" : [], "unconfigured": [] }
            self.updateNodesLockList [sector] = threading.Lock ()

        self.types = []
        self.typeLock = threading.Lock ()

        self.scanThread = threading.Thread (target = self.scan)
        self.scanning = True
        self.scanThread.start ()

    def scan (self):

        while self.scanning:

            self.typeLock.acquire ()
            self.types = self.commandInterface.fetchTypes ()
            self.typeLock.release ()

            for sector in self.sectors:
                self.updateNodesLockList [sector].acquire ()
                self.nodes [sector]["configured"] = self.commandInterface.getNodesFromSector (sector, registered = True)
                self.nodes [sector]["unconfigured"] = self.commandInterface.getNodesFromSector (sector, registered = False)
                self.updateNodesLockList [sector].release ()

            time.sleep (1)

    def getNodesFromSector (self, sector, registered = True):

        self.typeLock.acquire ()

        if registered:
            nodeList = self.nodes [sector]["configured"]
        else:
            nodeList = self.nodes [sector]["unconfigured"]

        self.typeLock.release ()

        return nodeList

    def fetchTypes (self):

        self.typeLock.acquire ()
        types = self.types
        self.typeLock.release ()

        return types

    def appendType (self, newType):
        return self.commandInterface.appendType (newType)

    def removeType (self, typeName):
        self.commandInterface.removeType (typeName)

    def appendNode (self, node):
        return self.commandInterface.appendNode (node)

    def removeNodeFromSector (self, node):
        return self.commandInterface.removeNodeFromSector (node)

    def stop (self):
        self.scanning = False
