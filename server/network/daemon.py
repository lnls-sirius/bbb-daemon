import socket
import threading

from common.entity.entities import Command
from common.network.utils import NetUtils
from control.controller import MonitorController


class DaemonHostListener():

    def __init__(self, serverBindPort=9876, hostConnectionPort=9877, controller: MonitorController = None):

        self.port = serverBindPort
        self.hostPort = hostConnectionPort

        self.controller = controller
        self.controller.daemon = self

        self.listenThread = threading.Thread(target=self.listen)
        self.listening = True
        self.listenThread.start()

    def sendCommand(self, command, address, **kargs):

        commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        commandSocket.settimeout(10)

        try:
            commandSocket.connect((address, self.hostPort))

            NetUtils.sendCommand(commandSocket, command)

            if command == Command.SWITCH:
                node = kargs["node"]
                NetUtils.sendObject(commandSocket, node.type.name)
                NetUtils.sendObject(commandSocket, node.type.repoUrl)
                NetUtils.sendObject(commandSocket, node.type.rcLocalPath)
                NetUtils.sendObject(commandSocket, node.name)
                NetUtils.sendObject(commandSocket, node.ipAddress)

            commandSocket.close()
            return True
        except socket.error:
            return False

    def process(self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = NetUtils.recvCommand(connection)

                if command == Command.PING:
                    name = NetUtils.recvObject(connection)
                    hostType = NetUtils.recvObject(connection)
                    self.controller.updateHostCounterByAddress(address=addr[0], name=name, hostType=hostType)
                if command == Command.EXIT:
                    print("Exiting")
                    return

            except Exception as e:
                print("Lost connection with host " + addr[0])
                print(e)
                connectionAlive = False

        connection.close()

    def listen(self):

        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        pingSocket.bind(("0.0.0.0", self.port))
        pingSocket.listen(255)

        while self.listening:
            connection, addr = pingSocket.accept()
            requestThread = threading.Thread(target=self.process, args=[connection, addr])
            requestThread.start()

        pingSocket.close()

    def stopAll(self):

        self.listening = False

        # In order to close the socket and exit from the accept () function, emulate a new connection
        shutdownSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shutdownSocket.connect(("0.0.0.0", self.port))
        NetUtils.sendCommand(shutdownSocket, Command.EXIT)
        shutdownSocket.close()
