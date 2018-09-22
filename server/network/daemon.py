import socket
import threading
import json

from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from common.entity.entities import Command
from common.network.utils import NetUtils, verify_msg
from control.controller import MonitorController


class DaemonHostListener():

    def __init__(self, workers: int = 10, bbbUdpPort: int = 9876, bbbTcpPort: int = 9877,
                 controller: MonitorController = None):

        self.bbbUdpPort = bbbUdpPort
        self.bbbTcpPort = bbbTcpPort

        self.controller = controller
        self.controller.daemon = self

        self.ipInProcess = {}

        self.queueUdp = Queue()

        self.listening = True
        self.listenThread = threading.Thread(target=self.listen_udp)
        self.listenThread.start()

        self.executor = ThreadPoolExecutor(max_workers=workers)
        for i in range(workers):
            self.executor.submit(self.process_worker_udp)

    def sendCommand(self, command, address, **kargs):

        commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        commandSocket.settimeout(10)

        try:
            commandSocket.connect((address, self.bbbTcpPort))

            NetUtils.sendCommand(commandSocket, command)

            if command == Command.SWITCH:
                node = kargs["node"]
                NetUtils.sendObject(commandSocket, node)
                # pv prefixes ...
            commandSocket.close()
            return True
        except socket.error:
            return False

    def process_worker_udp(self):
        while self.listening:
            try: 
                
                info = self.queueUdp.get(timeout=5, block=True)
                payload = json.loads(info[1])
                command = payload['command']  
                
                if command == Command.PING:  
                    self.controller.updateHostCounterByAddress(payload) 

            except Exception as e:
                pass
        print("Worker ... Finished")

    def listen_udp(self):
        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pingSocket.bind(("0.0.0.0", self.bbbUdpPort))

        print("Listening UDP on 0.0.0.0 : {} ....".format(self.bbbUdpPort))
        
        while self.listening:
            data, ipAddr = pingSocket.recvfrom(1024)  # buffer size is 1024 bytes
            data = str(data.decode('utf-8'))
            info = verify_msg(data=data)
            if info:
                self.queueUdp.put(info)
        pingSocket.close()
        
        print('UDP: Ping socket closed ')

    def stopAll(self):
        """
           Stop !
        """
        self.listening = False
        # In order to close the socket and exit from the accept () function, emulate a new connection
        self.executor.shutdown()
        try:
            shutdownSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            shutdownSocket.connect(("0.0.0.0", self.bbbTcpPort))
            NetUtils.sendCommand(shutdownSocket, Command.EXIT)
            shutdownSocket.close()
        except ConnectionRefusedError:
            pass
        print("Services Stopped.")
