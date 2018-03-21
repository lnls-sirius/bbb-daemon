import constants

import mutex
import socket
import threading
import time

class Daemon ():

    def __init__ (self, hostType = 0):

        self.hostTypeMutex = threading.Lock ()
        self.hostType = hostType

        self.scanThread = threading.Thread (target = self.scan)
        self.pingThread = threading.Thread (target = self.ping)

        self.scanThread.start ()
        self.pingThread.start ()

    def getType (self):

        self.hostTypeMutex.acquire ()
        t = self.hostType
        self.hostTypeMutex.release ()

        return t        

    def ping (self):

        pingSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

        pingSocket.connect ((constants.SERVER_IP, constants.PING_PORT))

        while True:

            pingSocket.send (str (self.getType ()))

            time.sleep (constants.PING_PERIOD)

        pingSocket.close ()

    def scan (self):

        pass

