import os
import shutil
import socket
import sys
import threading
import time
from configparser import ConfigParser
from copy import copy

from git import Repo

from common.entity.entities import Command
from common.network.utils import NetUtils, checksum
from common.network.utils import get_ip_address

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

    def __init__(self, path=None):

        self.configPath = path

        self.name = ""
        self.desiredName = ""
        self.desiredIp = ""
        self.type = "none"
        self.typeRepoUrl = ""
        self.typeRcLocalPath = ""
        self.myIp = ''
        self.readParameters()

    def getInfo(self):
        self.myIp = get_ip_address('eth0')
        info = "{}|{}|{}|{}" \
            .format(Command.PING, self.name, self.type, self.myIp)
        print(info)
        return info

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

    def update(self, newName=None, newType=None, newTypeRepoUrl=None, newTypeRcLocalPath=None):
        configFile = ConfigParser()
        configFile['NODE-CONFIG'] = {'node_name': '',
                                     'node_ip': '',
                                     'type_name': '',
                                     'type_url': '',
                                     'type_path': ''}
        if newName is not None:
            self.name = newName
            hostnameFile = open("/etc/hostname", "w")
            hostnameFile.write(self.name.replace(":", "-"))
            hostnameFile.close()

        if newType is not None:
            self.type = newType

        if newTypeRcLocalPath is not None and newTypeRepoUrl is not None:
            self.typeRcLocalPath = newTypeRcLocalPath
            self.typeRepoUrl = newTypeRepoUrl
            self.update_rclocal()

        configFile['NODE-CONFIG']['node_name'] = self.name
        configFile['NODE-CONFIG']['node_ip'] = self.myIp
        configFile['NODE-CONFIG']['type_name'] = self.type
        configFile['NODE-CONFIG']['type_url'] = self.typeRepoUrl
        configFile['NODE-CONFIG']['type_path'] = self.typeRcLocalPath


        self.writeNodeConfig(configFile=configFile)

    def readParameters(self):
        self.readNodeConfig()
        try:
            name = os.popen("hostname", "r").readline()[:-1]
            indexes = [i for i, letter in enumerate(name) if letter == "-"]
            name = list(name)
            if len(indexes) > 2:
                name[indexes[1]] = ":"

            self.name = "".join(name)
        except FileNotFoundError:
            self.name = "error-hostname-not-found"

    def readNodeConfig(self):
        try:
            configFile = ConfigParser()
            configFile.read(self.configPath)
            self.desiredName = configFile['NODE-CONFIG']['node_name']
            self.desiredIp = configFile['NODE-CONFIG']['node_ip']
            self.type = configFile['NODE-CONFIG']['type_name']
            self.typeRepoUrl = configFile['NODE-CONFIG']['type_url']
            self.typeRcLocalPath = configFile['NODE-CONFIG']['type_path']
            self.update(newName=self.desiredName, newType=self.type, newTypeRepoUrl=self.typeRepoUrl,
                        newTypeRcLocalPath=typeRcLocalPath)
        except Exception as e:
            print("{}".format(e))
            configFile = ConfigParser()
            configFile['NODE-CONFIG'] = {'node_name': 'default',
                                         'node_ip': 'default',
                                         'type_name': 'default',
                                         'type_url': 'default',
                                         'type_path': 'default'}
            with open(self.configPath, 'w') as f:
                configFile.write(f)

            self.desiredName = ''
            self.desiredIp = ''
            self.type = ''
            self.typeRepoUrl = ''
            self.typeRcLocalPath = ''

    def writeNodeConfig(self, configFile: ConfigParser):
        with open(self.configPath, 'w+') as bbb_cfg_file:
            configFile.write(bbb_cfg_file)


class Daemon():

    def __init__(self, serverAddress: str, pingPort: int, bindPort: int):

        self.bbb = BBB(path=CONFIG_PATH)
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
                Command.PING,
                self.bbb.name,
                self.bbb.type,
                self.myIp

            Under development ...
        :return:
        """
        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.pinging:
            info = self.bbb.getInfo()
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

                self.bbb.update(newName=nodeName, newType=typeName, newTypeRepoUrl=typeRepoUrl,
                                newTypeRcLocalPath=typeRcLocalPath)

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

    if not os.path.exists('/root/bbb-daemon-repos/'):
        os.makedirs('/root/bbb-daemon-repos/')

    print("arg[1]={}\targ[2]={}\targ[3]={}\t".format(servAddr, pingPort, bindPort))
    Daemon(serverAddress=servAddr, pingPort=pingPort, bindPort=bindPort)
