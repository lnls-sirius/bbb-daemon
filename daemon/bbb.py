import os
import shutil
import time
from configparser import ConfigParser
from copy import copy

from git import Repo

from daemon import RC_LOCAL_DESTINATION_PATH, typeRcLocalPath
from entity.entities import Command
from network.utils import get_ip_address


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