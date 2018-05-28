import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from common.entity.entities import Command
from common.network.utils import NetUtils, verify_msg
from control.controller import MonitorController


class DaemonHostListener():

    def __init__(self, serverBindPort=9876, hostConnectionPort=9877, controller: MonitorController = None):

        self.port = serverBindPort
        self.hostPort = hostConnectionPort

        self.controller = controller
        self.controller.daemon = self

        self.ipInProcess = {}

        self.queueUdp = Queue()
        self.executor = ThreadPoolExecutor(max_workers=10)
        for i in range(10):
            self.executor.submit(self.process_worker_udp)

        #self.listenThread = threading.Thread(target=self.listen)
        self.listenThread = threading.Thread(target=self.listen_udp)
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

    def process_worker_udp(self):
        while self.listening:
            #  {chk} | {cmd} | {name} | {type} | {ipAddr}
            info = self.queueUdp.get()

            command = info[1]
            if command == Command.PING:
                name = info[2]
                hostType = info[3]
                bbbIpAddr = info[4]
                self.controller.updateHostCounterByAddress(address=bbbIpAddr, name=name, hostType=hostType)

    def process(self, connection, addr):

        connectionAlive = True

        while connectionAlive and self.listening:

            try:
                # First 4 bytes are the command id
                command = NetUtils.recvCommand(connection)

                if command == Command.PING:
                    name = NetUtils.recvObject(connection)
                    hostType = NetUtils.recvObject(connection)
                    bbIpAddr = NetUtils.recvObject(connection)
                    self.controller.updateHostCounterByAddress(address=addr[0], name=name, hostType=hostType)
                    # self.controller.updateHostCounterByAddress(address=bbIpAddr, name=name, hostType=hostType)
                if command == Command.EXIT:
                    print("Exiting")
                    return

            except Exception as e:
                print("Lost connection with host " + addr[0])
                # print("Lost connection with host {}.".format(addr[0]))
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

    def listen_udp(self):

        pingSocket = socket.socket(socket.AF_INET,  # Internet
                                   socket.SOCK_DGRAM)  # UDP
        pingSocket.bind(("0.0.0.0", self.port))

        while self.listening:
            data, addr = pingSocket.recvfrom(1024)  # buffer size is 1024 bytes
            info = verify_msg(data=data)
            if info:
                self.queueUdp.put(info)

        pingSocket.close()

    def stopAll(self):

        self.listening = False

        # In order to close the socket and exit from the accept () function, emulate a new connection
        shutdownSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shutdownSocket.connect(("0.0.0.0", self.port))
        NetUtils.sendCommand(shutdownSocket, Command.EXIT)
        shutdownSocket.close()
