import os
import time
import shutil
from configparser import ConfigParser
from common.entity.entities import Command
from common.network.utils import get_ip_address
from sftp import downloadFiles, connect_to_ftp_server, download_from_ftp


class BBB():

    def __init__(self, path: str = None, rcLocalDestPath: str = None, sfp_server_addr: str = None, sftp_port: int = 22,
                 ftpDestinationFolder: str = None):

        self.ftpDestinationFolder = ftpDestinationFolder
        self.rcLocalDestPath = rcLocalDestPath
        self.configPath = path
        self.name = ""
        self.desiredName = ""
        self.desiredIp = ""
        self.type = "none"
        self.typeRepoUrl = ""
        self.typeRcLocalPath = ""
        self.myIp = ''
        self.typeSha = ''
        self.sftp_port = sftp_port
        self.sfp_server_addr = sfp_server_addr
        self.readParameters()

    def getInfo(self):
        self.myIp = get_ip_address('eth0')
        info = "{}|{}|{}|{}|{}" \
            .format(Command.PING, self.name, self.type, self.myIp, self.typeSha)
        print(info)
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
            repo_name = self.typeRepoUrl.strip().split('/')[-1].split('.')[0]

            repo_dir = self.ftpDestinationFolder + repo_name + "/"
            if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                shutil.rmtree(repo_dir)
                time.sleep(1)

            if repo_dir.endswith('/') and self.typeRcLocalPath.startswith('/'):
                self.typeRcLocalPath = self.typeRcLocalPath[1:]

            download_from_ftp(sftp_server_addr=self.sfp_server_addr, sftp_port=self.sftp_port, path=repo_name,
                              destination=repo_dir)

            print("Downloaded Node repository from FTP server {} at {}".format(self.typeRepoUrl, repo_name))

            if not os.path.isfile(repo_dir + self.typeRcLocalPath):
                shutil.rmtree(repo_dir)
                raise Exception("rc.local not found on path.")

            shutil.copy2((repo_dir + self.typeRcLocalPath), self.rcLocalDestPath)
            print("Copied file {} to {}".format(repo_dir + self.typeRcLocalPath, self.rcLocalDestPath))
            return True
        except Exception as e:
            print("{}".format(e))
            return False

    def update(self, newName=None, newType=None, newTypeRepoUrl=None, newTypeRcLocalPath=None, sha: str = ''):
        """
            Update the bbb with new data and refresh the project.
        :param newName:
        :param newType:
        :param newTypeRepoUrl:
        :param newTypeRcLocalPath:
        :return:
        """
        configFile = ConfigParser()
        configFile['NODE-CONFIG'] = {'node_name': '',
                                     'node_ip': '',
                                     'type_name': '',
                                     'type_url': '',
                                     'type_path': '',
                                     'type_sha': ''}
        self.typeSha = sha

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

        configFile['NODE-CONFIG']['node_name'] = self.name
        configFile['NODE-CONFIG']['node_ip'] = self.myIp
        configFile['NODE-CONFIG']['type_name'] = self.type
        configFile['NODE-CONFIG']['type_url'] = self.typeRepoUrl
        configFile['NODE-CONFIG']['type_path'] = self.typeRcLocalPath
        configFile['NODE-CONFIG']['type_sha'] = self.typeSha

        self.writeNodeConfig(configFile=configFile)

        self.update_project()

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
            if configFile['NODE-CONFIG']:
                config = configFile['NODE-CONFIG']

                self.desiredName = config.get('node_name', 'default')
                self.desiredIp = config.get('node_name', 'node_ip', 'default')
                self.type = config.get('node_name', 'type_name', 'default')
                self.typeRepoUrl = config.get('node_name', 'type_url', 'default')
                self.typeRcLocalPath = config.get('node_name', 'type_path', 'default')
                self.typeSha = config.get('node_name', 'type_sha', 'default')

                self.update(newName=self.desiredName, newType=self.type, newTypeRepoUrl=self.typeRepoUrl,
                            newTypeRcLocalPath=self.typeRcLocalPath, sha=self.typeSha)
        except Exception as e:
            print('Read node config exception {}'.format(e))
            self.desiredName = 'default'
            self.desiredIp = 'default'
            self.type = 'default'
            self.typeRepoUrl = 'default'
            self.typeRcLocalPath = 'default'
            self.typeSha = 'default'

    def writeNodeConfig(self, configFile: ConfigParser):
        with open(self.configPath, 'w+') as bbb_cfg_file:
            configFile.write(bbb_cfg_file)
