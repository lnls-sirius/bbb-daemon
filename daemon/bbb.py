import os
import time
import shutil
import pickle

from common.entity.entities import Command, Node, Type
from common.network.utils import get_ip_address
from common.network.utils import changeIp
from sftp import download_from_ftp


class BBB():

    def __init__(self, path, rc_local_dest_path, sfp_server_addr, sftp_port: int = 22,
                 ftp_destination_folder: str = None):

        #  Parameters that define absolute locations inside the Beaglebone
        self.ftpDestinationFolder = ftp_destination_folder
        self.rcLocalDestPath = rc_local_dest_path
        self.configPath = path
        self.sfp_server_addr = sfp_server_addr
        self.sftp_port = sftp_port

        # The interface used (ethernet port on the Beaglebone).
        self.interfaceName = 'eth0'

        # My configs !
        self.node = Node()
        self.node.type = Type()
        self.node.ipAddress = get_ip_address(self.interfaceName)

        # Load the data from the cfg file.
        self.readParameters()

    def getInfo(self):
        info = "{}|{}|{}|{}|{}" \
            .format(Command.PING, self.node.name, self.node.type.name, self.node.ipAddress, self.node.type.sha)
        return info

    def reboot(self):
        os.system('reboot')

    def update_project(self):
        """
            Update the project, getting the current version available on the FTP server.
            The responsibility to keep it up to date is all on the server side.
            Always removing the old ones.
        :return: True or False
        """
        if type is None:
            return False
        try:
            repo_name = self.node.type.repoUrl.strip().split('/')[-1].split('.')[0]

            repo_dir = self.ftpDestinationFolder + repo_name + "/"
            if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                shutil.rmtree(repo_dir)
                time.sleep(1)

            if repo_dir.endswith('/') and self.node.rcLocalPath.startswith('/'):
                self.node.rcLocalPath = self.node.rcLocalPath[1:]

            download_from_ftp(sftp_server_addr=self.sfp_server_addr, sftp_port=self.sftp_port, path=repo_name,
                              destination=repo_dir)

            print("Downloaded Node repository from FTP server {} at {}".format(self.node.type.repoUrl, repo_name))

            if not os.path.isfile(repo_dir + self.node.rcLocalPath):
                shutil.rmtree(repo_dir)
                raise Exception("rc.local not found on path.")

            shutil.copy2((repo_dir + self.node.rcLocalPath), self.rcLocalDestPath)
            print("Copied file {} to {}".format(repo_dir + self.node.rcLocalPath, self.rcLocalDestPath))
            return True
        except Exception as e:
            print("{}".format(e))
            return False

    def update(self, desiredNode: Node = None):
        """
        @todo : NODE! Update Code !!!!
        Update the bbb with new data and refresh the project.
        :return:
        """
        if not desiredNode or not desiredNode.type:
            print('Node/Type is None !')
            return
        if not desiredNode.ipAddress:
            print('IP Address is None !')
            return
        try:
            self.node = desiredNode

            res, msg = changeIp(interface_name=self.interfaceName, desired_ip=desiredNode.ipAddress)
            if res:
                self.node.ipAddress = get_ip_address(self.interfaceName)
            print(msg)

            with open("/etc/hostname", "w") as hostnameFile:
                hostnameFile.write(desiredNode.name.replace(":", "-"))
                hostnameFile.close()

            self.update_project()

            self.writeNodeConfig(pickle.dumps(self.node))
        except Exception as e:
            print('Update Error ! {}'.format(e))

    def readParameters(self):
        self.readNodeConfig()
        try:
            name = os.popen("hostname", "r").readline()[:-1]
            indexes = [i for i, letter in enumerate(name) if letter == "-"]
            name = list(name)
            if len(indexes) > 2:
                name[indexes[1]] = ":"

            self.node.name = "".join(name)
        except FileNotFoundError:
            self.node.name = "error-hostname-not-found"

    def readNodeConfig(self):
        try:
            with open(self.configPath, 'rb') as file:
                self.node = pickle.load(file)
        except Exception as e:
            print('Read node config exception {}'.format(e))

    def writeNodeConfig(self, data):
        with open(self.configPath, 'wb+') as file:
            file.write(data)
