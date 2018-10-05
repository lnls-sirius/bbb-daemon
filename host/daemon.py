import logging
import socket
import threading
import time
import msgpack

from host.bbb import BBB
from common.entity.definition import PING_INTERVAL
from common.entity.entities import Command
from common.entity.metadata import Singleton
from common.network.utils import NetUtils


class Daemon():
    """
    A class to monitor and update.
    """

    def __init__(self, server_address, ping_port, boot_port, bind_port,
                 ftp_destination_folder, path, rc_local_dest_path, sftp_port, ping_candidates):
        """
        Initializes a new Daemon object.

        :param server_address:
        :param ping_port:
        :param boot_port:
        :param bind_port:
        :param ftp_destination_folder:
        :param path:
        :param rc_local_dest_path:
        :param sftp_port:
        """

        self.bbb = BBB(path=path, rc_local_destination_path=rc_local_dest_path, sftp_port=sftp_port,
                       sftp_server_address=server_address, ftp_destination_folder=ftp_destination_folder)

        self.logger = logging.getLogger('Daemon')

        self.ping_candidates = ping_candidates

        self.ftpDestinationFolder = ftp_destination_folder

        self.server_address = server_address
        self.ping_port = ping_port
        self.boot_port = boot_port
        self.bind_port = bind_port

        self.ping_thread = threading.Thread(target=self.ping_udp)
        self.pinging = True
        self.ping_thread.start()

        self.command_thread = threading.Thread(target=self.listen)
        self.listening = True
        self.command_thread.start()

        self.logger.debug("Daemon object instantiated.")

    def request_project_defaults(self):
        """
        Requests the project that the current node should run when it boots.
        """

        command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command_socket.settimeout(10)

        command_socket.connect((self.server_address, self.boot_port))

        NetUtils.send_command(command_socket, Command.GET_REG_NODE_BY_IP)
        NetUtils.send_data(command_socket, self.bbb.node.ipAddress)

        node_from_server = NetUtils.recv_data(command_socket)

        if node_from_server != self.bbb.node:
            self.bbb.update(node_from_server)

        command_socket.close()

    def ping_udp(self):
        """
        Pings the server with the current configuration each ServerController.PING_INTERVAL seconds.
        """
        self.logger.info("Ping thread started.")

        ping_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:

            info = self.bbb.get_current_config()
            chk = NetUtils.checksum(str(info))
            payload = {'chk' : chk, 'payload':info}
            pack = msgpack.packb(payload, use_bin_type=True)

            for addr in self.ping_candidates:
                ping_socket.sendto(pack, (addr, self.ping_port))

            time.sleep(PING_INTERVAL)

        ping_socket.close()

        self.logger.info("Ping thread finished.")

    def stop(self):
        """
        Stops all threads.
        """
        self.pinging = False
        self.listening = False

    def listen(self):
        """
        Waits for commands sent by the server and acts accordingly. Should run on a dedicated thread.
        """

        self.logger.info("Command listening thread started.")

        command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        command_socket.bind(("0.0.0.0", self.bind_port))
        command_socket.listen(1)

        while self.listening:

            connection, address = command_socket.accept()

            command = NetUtils.recv_command(connection)

            self.logger.info("Command {} received from server.".format(Command.command_name(command)))

            if command == Command.SWITCH:
                node = NetUtils.recv_object(connection)
                self.bbb.update(node)
                self.stop()
                self.bbb.reboot()

            if command == Command.REBOOT:
                self.stop()
                self.bbb.reboot()

        command_socket.close()

        self.logger.info("Command listening thread finished.")
