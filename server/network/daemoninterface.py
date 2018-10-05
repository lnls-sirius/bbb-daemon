import logging
import socket
import threading
import msgpack

from common.entity.entities import Command
from common.entity.metadata import Singleton
from common.network.utils import NetUtils
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue


class DaemonHostListener(metaclass=Singleton):
    """
    This class interfaces the BBB hosts and the serves.
    """

    def __init__(self, workers: int = 10, bbb_udp_port: int = 9876, bbb_tcp_port: int = 9877):
        from server.control.controller import ServerController

        self.bbbUdpPort = bbb_udp_port
        self.bbbTcpPort = bbb_tcp_port

        self.controller = ServerController.get_instance()
        self.controller.daemon = self

        self.ipInProcess = {}

        # UDP Ethernet socket
        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ping_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.queueUdp = Queue()

        self.logger = logging.getLogger('DaemonHostListener')

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
        """
        A worker's thread. It dequeues an element and updates the respective node's paramenters.
        """
        while self.listening:
            try:
                data = self.queueUdp.get(timeout=5, block=True)
                payload = NetUtils.compare_checksum(expected_chk=data['chk'], payload=data['payload'])
                if payload['comm'] == Command.PING:  
                    self.controller.update_host_counter_by_address(node_dict=payload['n'], type_dict=payload['t'])
                    
                elif payload['comm'] == Command.EXIT:
                    self.logger.info("Worker received an EXIT command. Finishing its thread.")
                    return
                    
            except KeyError:
                self.logger.exception("Worker UDP wrong payload format.")
            except ValueError:
                self.logger.info("Received a corrupted message.")
            except Empty:
                # Queue is empty, wait again
                pass

        self.logger.info("Worker's thread closed.")

    def listen_udp(self):
        """
        Listens for host pings via UDP datagrams.
        """
        self.logger.info("Creating ping listening thread.")
        self.ping_socket.bind(("0.0.0.0", self.bbbUdpPort))
        self.logger.info("Listening UDP on 0.0.0.0:{}.".format(self.bbbUdpPort))

        while self.listening:
            try:
                data, ip_address = self.ping_socket.recvfrom(1024)  # buffer size is 1024 bytes
                if type(data) != bin:
                    pass
                    
                data = msgpack.unpackb(data, raw=False)

                if len(data) == 1 and int(data) == Command.EXIT:
                    self.logger.info("Stopping pinging thread's inner loop")
                    break 

                self.queueUdp.put(data)
            except:
                # Probably a malformed message caused an exception when unpacking
                self.logger.exception('asdasd')
                pass
        self.ping_socket.close()
        self.logger.info("Ping listening thread closed.")

    def stop_all(self):
        """
        Stop all threads and workers.
        """
        self.listening = False
        self.executor.shutdown()

        # In order to close the socket and exit from the accept () function, emulate a new connection
        try:
            shutdown_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            shutdown_socket.sendto('{}'.format(msgpack.packb(Command.EXIT, use_bin_type=True)), ("localhost", self.bbbUdpPort))
            shutdown_socket.close()
        except socket.error:
            self.logger.exception("Error while closing threads.")
