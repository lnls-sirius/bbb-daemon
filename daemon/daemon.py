import os
import socket
import threading
import time

from bbb import BBB
from common.entity.entities import Command
from common.network.utils import NetUtils, checksum

##################################################################
CONFIG_PATH = "/root/bbb-daemon/bbb.bin"
TYPE_RC_LOCAL_PATH = "init/rc.local"
RC_LOCAL_DESTINATION_PATH = "/etc/rc.local"
FTP_SERVER_PORT = 1026

# This info should contain a '/'
FTP_DESTINATION_FOLDER = '/root/'
servAddr = "10.0.6.44"
pingPort = 9876
bindPort = 9877

##################################################################
# CLONE_PATH = "../"  # remember to place the forward slash !


class Daemon():
    def __init__(self, serverAddress: str, pingPort: int, bindPort: int, ftpDestinationFolder: str):
        self.ftpDestinationFolder = ftpDestinationFolder

        self.bbb = BBB(path=CONFIG_PATH, rc_local_dest_path=RC_LOCAL_DESTINATION_PATH, sftp_port=FTP_SERVER_PORT,
                       sfp_server_addr=servAddr, ftp_destination_folder=self.ftpDestinationFolder)
        self.serverAddress = serverAddress
        self.pingPort = pingPort
        self.bindPort = bindPort

        self.pingThread = threading.Thread(target=self.ping_udp)
        self.pinging = True
        self.pingThread.start()

        self.commandThread = threading.Thread(target=self.listen)
        self.listening = True
        self.commandThread.start()

    def ping_udp(self):
        """
        Sends the current parameters set on the bbb to the server so it can monitor if it's configured or not.
        Command.PING,
        self.bbb.name,
            self.bbb.type,
            self.myIp,
            @todo: rc.config,  pv.prefix
            Under development ...
        :return:
        """
        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:
            info = self.bbb.getInfo()
            message = "{}|{}".format(checksum(info), info)
            pingSocket.sendto(message.encode('utf-8'), (self.serverAddress, self.pingPort))
            time.sleep(1)

    def stop(self):
        self.pinging = False
        self.listening = False

    def listen(self):
        """
            Listen to commands from the server.
        :return:
        """
        commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        commandSocket.bind(("0.0.0.0", self.bindPort))
        commandSocket.listen(1)

        while self.listening:

            connection, addr = commandSocket.accept()

            command = NetUtils.recvCommand(connection)

            if command == Command.SWITCH:
                print("Command SWITCH")
                # Don't change this order !
                node = NetUtils.recvObject(connection)
                self.bbb.update(node)
                print("bbb updated ! Rebooting now !")
                self.pinging = False
                self.bbb.reboot()

            if command == Command.REBOOT:
                self.pinging = False
                self.bbb.reboot()

        commandSocket.close()

    def stop(self):
        self.pinging = False
        self.listening = False


if __name__ == '__main__':
    import sys

    print("arg[1]=servAddress\targ[2]=pingPort\targ[3]=bindPort\targ[4]=FTP_DESTINATION_FOLDER")
    if len(sys.argv) == 5:
        servAddr = sys.argv[1]
        pingPort = int(sys.argv[2])
        bindPort = int(sys.argv[3])
        FTP_DESTINATION_FOLDER = sys.argv[4]
        print('\n\t{}\n\n'.format(sys.argv))
    else:
        print('Error with the parameters. Using default values.')

    if not FTP_DESTINATION_FOLDER.endswith('/'):
        FTP_DESTINATION_FOLDER = FTP_DESTINATION_FOLDER + '/'

    if not os.path.exists(FTP_DESTINATION_FOLDER):
        os.makedirs(FTP_DESTINATION_FOLDER)

    print("arg[1]={}\targ[2]={}\targ[3]={}\t".format(servAddr, pingPort, bindPort))
    Daemon(serverAddress=servAddr, pingPort=pingPort, bindPort=bindPort, ftpDestinationFolder=FTP_DESTINATION_FOLDER)
