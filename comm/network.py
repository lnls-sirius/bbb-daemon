import entity.entities
import socket
import struct
import threading

class NetDaemon ():

    def __init__ (self, serverBindPort = 9876, controller = None):

        self.port = serverBindPort

        self.controller = controller

        self.commandSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listenThread = threading.Thread (target = self.listen)
        self.listening = True
        self.listenThread.start ()

    def process (self, connection, addr):

        # First 4 bytes are the command id
        command = struct.unpack ("!i", connection.recv(4)) [0]
        print (command)

        if command == entity.entities.Command.PING:
            self.controller.updateHostCounterByAddress (address = addr)
        if command == entity.entities.Command.EXIT:
            print ("Exiting")
            return

    def listen (self):

        self.commandSocket.bind (("0.0.0.0", self.port))
        self.commandSocket.listen (255)

        while self.listening:

            connection, addr = self.commandSocket.accept ()
            requestThread = threading.Thread (target = self.process, args = [connection, addr])
            requestThread.start ()

        self.commandSocket.close ()

    def stopAll (self):

        self.listening = False

        # In order to close the socket and exit from the accept () function, emulate a new connection
        self.shutdownSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.shutdownSocket.connect (("0.0.0.0",  self.port))
        self.shutdownSocket.send (struct.pack ("!i", entity.entities.Command.EXIT))
        self.shutdownSocket.close ()
