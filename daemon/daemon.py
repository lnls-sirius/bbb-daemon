import shutil
import socket
import threading
import time
import os
import sys

from git import Repo

from common.entity.entities import Command
from common.network.utils import NetUtils

from shutil import copy


class BBB():
    CONFIG_PATH = "/root/bbb-daemon/bbb.cfg"
    typeRcLocalPath = "init/rc.local"
    RC_LOCAL_DESTINATION_PATH = "/etc/rc.local"

    # CLONE_PATH = "../"  # remember to place the forward slash !

    def __init__(self, path=CONFIG_PATH):
        self.name = ""
        self.configPath = path
        self.typeRepoUrl = ""
        self.typeRcLocalPath = ""
        self.type = ""
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
                copy(repo_dir + self.typeRcLocalPath, self.RC_LOCAL_DESTINATION_PATH)
                print("Copied file {} to {}".format(repo_dir + self.typeRcLocalPath, self.RC_LOCAL_DESTINATION_PATH))
                shutil.rmtree(repo_dir)
            else:
                print("Not repo URL defined.")
        except Exception as e:
            print("{}".format(e))

    def update(self, newName, newType, typeRepoUrl, typeRcLocalPath):
        try:
            if newName is not None:
                self.name = newName
                hostnameFile = open("/etc/hostname", "w")
                hostnameFile.write(self.name.replace(":", "-"))
                hostnameFile.close()

            if newType is not None:
                self.type = newType
                typeFile = open(self.configPath, "w+")
                typeFile.write(self.type + "\n")
                typeFile.close()

            if typeRcLocalPath is not None and typeRepoUrl is not None:
                self.typeRcLocalPath = typeRcLocalPath
                self.typeRepoUrl = typeRepoUrl
                self.update_rclocal()

        except FileNotFoundError:
            print("Configuration files not found.")

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

        try:
            f = open(self.configPath, "r")
            self.type = f.readline()[:-1]
            f.close()
        except FileNotFoundError:
            print("Cfg file not found.")


class Daemon():

    def __init__(self, path="", serverAddress="10.0.6.70", pingPort=9876, bindPort=9877):

        if not os.path.exists('/root/bbb-daemon-repos/'):
            os.makedirs('/root/bbb-daemon-repos/')
        self.serverAddress = serverAddress
        self.pingPort = pingPort
        self.bindPort = bindPort
        self.bbb = BBB()

        self.pingThread = threading.Thread(target=self.ping)
        self.pinging = True
        self.pingThread.start()

        self.commandThread = threading.Thread(target=self.listen)
        self.listening = True
        self.commandThread.start()

    def ping(self):

        pingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        pingSocket.settimeout(10)

        connected = False

        while self.pinging:

            try:
                if not connected:
                    pingSocket.connect((self.serverAddress, self.pingPort))
                    print("connection established")
                    connected = True

                NetUtils.sendCommand(pingSocket, Command.PING)
                NetUtils.sendObject(pingSocket, self.bbb.name)
                NetUtils.sendObject(pingSocket, self.bbb.type)

            except socket.error:
                print("error")
                connected = False

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

        self.commandSocket.close()

    def stop(self):
        self.pinging = False
        self.listening = False


if __name__ == '__main__':

    servAddr = "10.0.0.70"
    pingPort = 9876
    bindPort = 9877

    print("arg[1]=servAddress arg[2]=pingPort arg[3]=bindPort")
    if len(sys.argv) == 4:
        servAddr = sys.argv[1]
        pingPort = int(sys.argv[2])
        bindPort = int(sys.argv[3])

    print("arg[1]={}\targ[2]={}\targ[3]={}\t".format(servAddr, pingPort, bindPort))
    Daemon(serverAddress=servAddr, pingPort=pingPort, bindPort=bindPort)
