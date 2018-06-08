import shutil
import socket
import threading
import time
import os
import sys
from configparser import ConfigParser

from git import Repo

from common.entity.entities import Command
from common.network.utils import NetUtils, checksum, get_ip_address

from shutil import copy

##################################################################
CONFIG_PATH = "/root/bbb-daemon/bbb.cfg"
typeRcLocalPath = "init/rc.local"
RC_LOCAL_DESTINATION_PATH = "/etc/rc.local"

servAddr = "10.0.0.70"
pingPort = 9876
bindPort = 9877


##################################################################
# CLONE_PATH = "../"  # remember to place the forward slash !

class BBB():

    def __init__(self, path=CONFIG_PATH):
        self.configFile = ConfigParser()
        self.configFile['NODE-CONFIG'] = {'node_name': '',
                                          'node_ip': '',
                                          'type_name': '',
                                          'type_url': '',
                                          'type_path': ''}

        self.configPath = path

        self.name = ""
        self.desiredIp = ""
        self.type = "none"
        self.typeRepoUrl = ""
        self.typeRcLocalPath = ""
        self.readParameters()

    def reboot(self):
        os.system('reboot')

    def update_rclocal(self):
        try:
            if type is not None:
                repo_name = self.typeRepoUrl.strip().split('/')[-1].split('.')[0]

                if not self.typeRepoUrl.endswith(".git") or (
                        not self.typeRepoUrl.startswith("http://") and not self.typeRepoUrl.startswith("https://")):
                    raise Exception("\'{}\' is not a valid git URL.".format(self.typeRepoUrl))

                repo_dir = "/root/bbb-daemon-repos/" + repo_name + "/"
                if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                    shutil.rmtree(repo_dir)
                    time.sleep(1)

                Repo.clone_from(url=self.typeRepoUrl.strip(), to_path=repo_dir)

                if repo_dir.endswith('/') and self.typeRcLocalPath.startswith('/'):
                    self.typeRcLocalPath = self.typeRcLocalPath[1:]
                elif not repo_dir.endswith('/') and not self.typeRcLocalPath.startswith('/'):
                    repo_dir = repo_dir + '/'

                if not os.path.isfile(repo_dir + self.typeRcLocalPath):
                    shutil.rmtree(repo_dir)
                    raise Exception("rc.local not found on path.")
                pass

                print("Cloned repository {} at {}/{}".format(self.typeRepoUrl, os.getcwd(), repo_name))
                copy(repo_dir + self.typeRcLocalPath, RC_LOCAL_DESTINATION_PATH)
                print("Copied file {} to {}".format(repo_dir + self.typeRcLocalPath, RC_LOCAL_DESTINATION_PATH))
                shutil.rmtree(repo_dir)
            else:
                print("Not repo URL defined.")
        except Exception as e:
            print("{}".format(e))

    def update(self, newName, newType, typeRepoUrl, typeRcLocalPath):
        if newName is not None:
            self.name = newName
            self.configFile['NODE-CONFIG']['node_name'] = self.name

        if newType is not None:
            self.type = newType
            self.configFile['NODE-CONFIG']['type_name'] = self.type

        if typeRcLocalPath is not None and typeRepoUrl is not None:
            self.typeRcLocalPath = typeRcLocalPath
            self.typeRepoUrl = typeRepoUrl
            self.configFile['NODE-CONFIG']['type_url'] = self.typeRepoUrl
            self.configFile['NODE-CONFIG']['type_path'] = self.typeRcLocalPath

            self.update_rclocal()

        self.writeNodeConfig()

    def readParameters(self):
        try:
            name = os.popen("hostname", "r").readline()[:-1]
            indexes = [i for i, letter in enumerate(name) if letter == "-"]
            name = list(name)
            if len(indexes) > 2:
                name[indexes[1]] = ":"

            self.name = "".join(name)
        except FileNotFoundError:
            self.name = "error-hostname-not-found"

        self.readNodeConfig()

    def readNodeConfig(self):
        try:
            bbb_cfg_file = open(self.configPath, 'r')
            self.configFile.read(bbb_cfg_file, encoding='utf-8')
        except:
            with open(self.configPath, 'w+') as bbb_cfg_file:
                self.configFile.write(bbb_cfg_file)

#        self.name = self.configFile['NODE-CONFIG']['node_name']
        self.desiredIp = self.configFile['NODE-CONFIG']['node_ip']
        self.type = self.configFile['NODE-CONFIG']['type_name']
        self.typeRepoUrl = self.configFile['NODE-CONFIG']['type_url']
        self.typeRcLocalPath = self.configFile['NODE-CONFIG']['type_path']

    def writeNodeConfig(self):
        with open(self.configPath, 'w+') as bbb_cfg_file:
            self.configFile.write(bbb_cfg_file)


class Daemon():

    def __init__(self, path="", serverAddress="10.0.6.44", pingPort=9876, bindPort=9877):

        if not os.path.exists('/root/bbb-daemon-repos/'):
            os.makedirs('/root/bbb-daemon-repos/')
        self.myIp = get_ip_address('eth0')
        self.serverAddress = serverAddress
        self.pingPort = pingPort
        self.bindPort = bindPort
        self.bbb = BBB()

        self.pingThread = threading.Thread(target=self.ping_udp)
        self.pinging = True
        self.pingThread.start()

        self.commandThread = threading.Thread(target=self.listen)
        self.listening = True
        self.commandThread.start()

    def ping_udp(self):
        """
                Command.PING,
                self.bbb.name,
                self.bbb.type,
                self.myIp

            Under development ...
        :return:
        """
        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:
            info = "{}|{}|{}|{}" \
                .format(Command.PING, self.bbb.name, self.bbb.type, self.myIp)
            message = "{}|{}".format(checksum(info), info)
            ## {chk} | {cmd} | {name} | {type} | {ipAddr}
            pingSocket.sendto(message.encode('utf-8'), (self.serverAddress, self.pingPort))
            time.sleep(1)

    def stop(self):
        self.pinging = False
        self.listening = False

    def listen(self):

        commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        commandSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        commandSocket.bind(("0.0.0.0", self.bindPort))
        commandSocket.listen(1)

        while self.listening:

            connection, addr = commandSocket.accept()

            command = NetUtils.recvCommand(connection)

            if command == Command.SWITCH:
                print("Commando SWITCH")
                # Type ...
                typeName = NetUtils.recvObject(connection)
                typeRepoUrl = NetUtils.recvObject(connection)
                typeRcLocalPath = NetUtils.recvObject(connection)

                # Node
                nodeName = NetUtils.recvObject(connection)

                print(typeName + " " + nodeName + " " + typeRepoUrl + " " + typeRcLocalPath)

                self.bbb.update(nodeName, typeName, typeRepoUrl, typeRcLocalPath)

            if command == Command.REBOOT:
                self.pinging = False
                self.bbb.reboot()

        commandSocket.close()

    def stop(self):
        self.pinging = False
        self.listening = False


if __name__ == '__main__':

    print("arg[1]=servAddress arg[2]=pingPort arg[3]=bindPort")
    if len(sys.argv) == 4:
        servAddr = sys.argv[1]
        pingPort = int(sys.argv[2])
        bindPort = int(sys.argv[3])

    print("arg[1]={}\targ[2]={}\targ[3]={}\t".format(servAddr, pingPort, bindPort))
    Daemon(serverAddress=servAddr, pingPort=pingPort, bindPort=bindPort)
