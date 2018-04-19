from common.entity.entities import Command, Node, NodeState, Type

import socket
import struct
import threading

class DaemonHostListener ():

    def __init__ (self, serverBindPort = 9876, controller = None):

        self.port = serverBindPort

        self.controller = controller

        self.commandSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listenThread = threading.Thread (target = self.listen)
        self.listening = True
        self.listenThread.start ()

    def process (self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = struct.unpack ("!i", connection.recv(4)) [0]

                if command == Command.PING:
                    name = struct.unpack ("=32s", connection.recv(32)) [0].decode("utf-8").strip ()
                    hostType = struct.unpack ("=32s", connection.recv(32)) [0].decode("utf-8").strip ()
                    self.controller.updateHostCounterByAddress (address = addr [0], name = name, hostType = hostType)
                if command == Command.EXIT:
                    print ("Exiting")
                    return

            except Exception as e:
                print ("Lost connection with host " + addr [0])
                print (e)
                connectionAlive = False

        connection.close ()

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
        self.shutdownSocket.send (struct.pack ("!i", Command.EXIT))
        self.shutdownSocket.close ()
