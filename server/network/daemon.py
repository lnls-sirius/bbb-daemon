import socket
import threading

from common.entity.entities import Command
from common.entity.metadata import Singleton
from common.network.utils import NetUtils
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from server.control.controller import ServerController


class DaemonHostListener(metaclass=Singleton):
    """

    """

    def __init__(self, workers: int = 10, bbb_udp_port: int = 9876, bbb_tcp_port: int = 9877):

        self.bbbUdpPort = bbb_udp_port
        self.bbbTcpPort = bbb_tcp_port

        self.controller = ServerController.get_instance()
        self.controller.daemon = self

        self.ipInProcess = {}

        self.queueUdp = Queue()

        self.listening = True
        self.listenThread = threading.Thread(target=self.listen_udp)
        self.listenThread.start()

        self.executor = ThreadPoolExecutor(max_workers=workers)
        for i in range(workers):
            self.executor.submit(self.process_worker_udp)

    def send_command(self, command, address, **kargs):

        command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        command_socket.settimeout(10)

        try:
            command_socket.connect((address, self.bbbTcpPort))

            NetUtils.send_command(command_socket, command)

            if command == Command.SWITCH:
                node = kargs["node"]
                NetUtils.send_object(command_socket, node)
                # pv prefixes ...
            command_socket.close()
            return True
        except socket.error:
            return False

    def process_worker_udp(self):
        while self.listening:
            try:
                #  {chk} | {cmd} | {name} | {type} | {ipAddr} | {sha}
                info = self.queueUdp.get(timeout=5, block=True)
                command = int(info[1])
                if command == Command.PING:
                    name = info[2]
                    hostType = info[3]
                    bbbIpAddr = info[4]
                    bbbSha = info[5]
                    self.controller.update_host_counter_by_address(address=bbbIpAddr, name=name, hostType=hostType,
                                                                   bbbSha=bbbSha)
                elif command == Command.EXIT:
                    print("Worker ... EXIT")
                    return
            except Exception as e:
                pass
        print("Worker ... Finished")

    def listen_udp(self):
        ping_socket = socket.socket(socket.AF_INET,  # Internet
                                   socket.SOCK_DGRAM)  # UDP
        ping_socket.bind(("0.0.0.0", self.bbbUdpPort))
        print("Listening UDP on 0.0.0.0 : {} ....".format(self.bbbUdpPort))
        while self.listening:
            data, ipAddr = ping_socket.recvfrom(1024)  # buffer size is 1024 bytes
            data = str(data.decode('utf-8'))
            info = NetUtils.verify_msg(data=data)
            if info:
                self.queueUdp.put(info)
        ping_socket.close()
        print('Ping socket closed ')

    def stop_all(self):
        """
           Stop !
        """
        self.listening = False
        # In order to close the socket and exit from the accept () function, emulate a new connection
        self.executor.shutdown()
        try:
            shutdown_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            shutdown_socket.connect(("0.0.0.0", self.bbbTcpPort))
            NetUtils.send_command(shutdown_socket, Command.EXIT)
            shutdown_socket.close()
        except ConnectionRefusedError:
            pass
        print("Services Stopped.")
