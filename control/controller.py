import comm.persistence

class MonitorController ():

    def __init__ (self):

        self.db = comm.persistence.RedisPersistence (host = '10.0.6.65', port = 6379)
        self.sectors = [str (i) for i in range(1,21)] + ["LINAC", "RF", "Conectividade"]

    def fetchTypes (self):

        return self.db.fetchTypes ()

    def appendType (self, newType = {}):

        return self.db.appendType (newType)

    def appendNode (self, newNode = {}):

        return self.db.appendNode (newNode)

    def removeType (self, t):

        self.db.removeType (t)

    def removeNodeFromSector (self, node):

        return self.db.removeNodeFromSector (node)

    def fetchNodesFromSector (self, sector = 1):

        return self.db.fetchNodesFromSector (sector)
