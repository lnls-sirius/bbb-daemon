import comm.persistence
import entity.entities
import threading
import time

class MonitorController ():

    def __init__ (self):
        self.db = comm.persistence.RedisPersistence (host = '10.0.6.65', port = 6379)
        self.sectors = [str (i) for i in range(1,21)] + ["LINAC", "Fontes", "RF", "Conectividade"]

        self.nodes = {}
        self.updateNodesLockList = {}

        for sector in self.sectors:
            self.nodes [sector] = []
            self.updateNodesLockList [sector] = threading.Lock ()

        self.updateNodesThread = threading.Thread (target = self.scanNodes)
        self.scanNodes = True
        self.updateNodesThread.start ()

    def fetchTypes (self):
        return self.db.fetchTypes ()

    def appendType (self, newType = {}):
        return self.db.appendType (newType)

    def scanNodes (self):

        while self.scanNodes:

            for sector in self.sectors:

                self.updateNodesLockList [sector].acquire ()
                fetchedNodes = self.fetchNodesFromSector (sector)

                # Verify if there is an unregistered node
                for node in fetchedNodes:
                    for n in self.nodes [sector]:
                        if node.name == n.name:
                            node.counter = max (0, n.counter - 1)
                            # A host is considered disconnected if its internal counter is null
                            if node.counter == 0:
                                node.state = entity.entities.NodeState.DISCONNECTED
                            else:
                                node.state = entity.entities.NodeState.CONNECTED

                self.nodes [sector] = fetchedNodes
                self.updateNodesLockList [sector].release ()

            time.sleep (1)

    def appendNode (self, newNode = {}):
        return self.db.appendNode (newNode)

    def removeType (self, t):
        self.db.removeType (t)

    def removeNodeFromSector (self, node):
        return self.db.removeNodeFromSector (node)

    def fetchNodesFromSector (self, sector = 1):
        return self.db.fetchNodesFromSector (sector)

    def getNodesFromSector (self, sector = 1):
        self.updateNodesLockList [sector].acquire ()
        nodes = self.nodes [sector]
        self.updateNodesLockList [sector].release ()
        return nodes

    def updateHostCounterByAddress (self, address) :

        for sector in self.sectors:

            self.updateNodesLockList [sector].release ()

            for node in self.nodes [sector]:
                if node.ipAddress == address:
                    node.counter = 5
                    node.state = entity.entities.NodeState.CONNECTED
                    self.updateNodesLockList [sector].release ()
                    return True

            self.updateNodesLockList [sector].release ()

            # An unknown host has connected to the server 
        return False
