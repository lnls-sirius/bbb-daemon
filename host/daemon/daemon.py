#!/usr/bin/python3

import logging
import socket
import threading
import time
import msgpack

from host.daemon.bbb import BBB
from common.entity.definition import PING_INTERVAL
from common.entity.entities import Command
from common.entity.metadata import Singleton
from common.network.utils import NetUtils


class Daemon():
    """
    A class to monitor and update.
    """
    def __init__(self, ping_port, bind_port, path, ping_candidates):
        """
        Initializes a new Daemon object.

        :param ping_port:
        :param bind_port:
        :param path:
        """

        self.bbb = BBB(path=path)

        self.logger = logging.getLogger('Daemon')

        self.ping_candidates = ping_candidates

        self.ping_port = ping_port
        self.bind_port = bind_port

        self.ping_thread = threading.Thread(target=self.ping_udp, daemon=True)
        self.pinging = True
        self.ping_thread.start()

        self.command_thread = threading.Thread(target=self.listen, daemon=True)
        self.listening = True
        self.command_thread.start()

        self.logger.debug("Daemon object instantiated.")

    def ping_udp(self):
        """
        Pings the server with the current configuration each ServerController.PING_INTERVAL seconds.
        """
        self.logger.info("Ping thread started.")

        ping_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:
            try:
                info = self.bbb.get_current_config()
                chk = NetUtils.checksum(str(info))
                payload = {'chk':chk, 'payload':info}
                pack = msgpack.packb(payload, use_bin_type=True)

                for addr in self.ping_candidates:
                    ping_socket.sendto(pack, (addr, self.ping_port))

                time.sleep(PING_INTERVAL)
            except:
                # Exception occurs when changing IP address without rebooting
                # Close and reopen socket
                ping_socket.close()
                time.sleep(1)
                ping_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

        while self.listening:

            command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            command_socket.bind(("0.0.0.0", self.bind_port))
            command_socket.listen(1)


            connection, address = command_socket.accept()

            command = NetUtils.recv_command(connection)

            self.logger.info("Command {} received from server.".format(Command.command_name(command)))

            if command == Command.REBOOT:
                self.stop()
                self.bbb.reboot()

            elif command == Command.SET_HOSTNAME:
                new_hostname = NetUtils.recv_object(connection)
                self.bbb.update_hostname(new_hostname)

            elif command == Command.SET_IP:
                type = NetUtils.recv_object(connection)
                if type == 'manual':
                    new_ip = NetUtils.recv_object(connection)
                    new_mask = NetUtils.recv_object(connection)
                    new_gateway = NetUtils.recv_object(connection)
                    nameserver_1 = NetUtils.recv_object(connection)
                    nameserver_2 = NetUtils.recv_object(connection)
                    self.bbb.update_ip_address(type, new_ip, new_mask, new_gateway, nameserver_1, nameserver_2)
                elif type == 'dhcp':
                    self.bbb.update_ip_address(type)

            command_socket.close()

        self.logger.info("Command listening thread finished.")
