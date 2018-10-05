import ipaddress
import logging
import pickle
import os
import shutil
import subprocess
import time
import json

from common.entity.entities import Command, Node, Sector, Type
from host.sftp import download_from_ftp


class BBB:
    """
    A class to represent a Beaglebone host.
    """
    CONFIG_JSON_PATH = '/opt/config.json'
    
    def __init__(self, path, rc_local_destination_path, sftp_server_address, sftp_port=22,
                 ftp_destination_folder = None, interface='eth0'):
        """
        Creates a new object instance.
        :param path: the configuration file's location
        :param rc_local_destination_path: the node's rc.local path.
        :param sftp_server_address: the FTP server's IP address.
        :param sftp_port: the FTP server's listening port.
        :param ftp_destination_folder: the path which the project will be copied to.
        """

        #  Parameters that define absolute locations inside the host
        self.ftp_destination_folder = ftp_destination_folder
        self.rc_local_destination_path = rc_local_destination_path
        self.configuration_file_path = path

        self.sfp_server_address = sftp_server_address
        self.sftp_port = sftp_port

        # The interface used (ethernet port on the Beaglebone).
        self.interface_name = interface

        # Creates the objects that wrap the host's settings.
        self.node = Node()
        self.node.type = Type()
        print(self.get_ip_address()[0])
        self.node.ip_address = ipaddress.ip_address(self.get_ip_address()[0])

        self.logger = logging.getLogger('BBB')
        self.current_config_json_mtime = None

        # Load the data from the cfg file.
        self.read_node_parameters()

    def check_config_json(self):
        """
        Verify if the version loaded of the file config.json is the lattest
        available. If not, load again.
        """
        if os.path.exists(BBB.CONFIG_JSON_PATH):
            config_json_mtime = os.path.getmtime(BBB.CONFIG_JSON_PATH)
            if self.current_config_json_mtime == None or config_json_mtime != self.current_config_json_mtime:
                with open(BBB.CONFIG_JSON_PATH, 'r') as f:
                    config = json.load(f)
                    self.current_config_json_mtime = config_json_mtime
                    self.node.device = config['device']
                    self.node.details  = config['details'] + '   ' + str(config['baudrate'])
                    self.node.config_time = config['time']
        

    def get_current_config(self):
        """
        Returns a dictionary containing the host's information and the command type.
        :return: message representing the current configuration.
        """ 
        dict_res = self.node.to_set()
        return {'comm' : Command.PING, 'n' : dict_res[1], 't' : dict_res[2][1]}

    def reboot(self):
        """
        Reboots this node.
        """
        self.logger.info("Rebooting system.")
        os.system('reboot')

    def update_project(self):
        """
        Imports the current project version from the FTP server. This method does not keep old project versions.
        :return: True or False
        """
        try:
            repo_name = self.node.type.repoUrl.strip().split('/')[-1].split('.')[0]

            repo_dir = self.ftp_destination_folder + repo_name + "/"
            if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                shutil.rmtree(repo_dir)
                time.sleep(1)

            if repo_dir.endswith('/') and self.node.rcLocalPath.startswith('/'):
                self.node.rcLocalPath = self.node.rcLocalPath[1:]

            download_from_ftp(sftp_server_addr=self.sfp_server_address, sftp_port=self.sftp_port, path=repo_name,
                              destination=repo_dir)

            print("Downloaded Node repository from FTP server {} at {}".format(self.node.type.repoUrl, repo_name))

            if not os.path.isfile(repo_dir + self.node.rcLocalPath):
                self.logger.info("rc.local not found on path {}".format(repo_dir + self.node.rcLocalPath))
            else:
                shutil.copy2((repo_dir + self.node.rcLocalPath), self.rc_local_destination_path)
                print("Copied file {} to {}".format(repo_dir + self.node.rcLocalPath, self.rc_local_destination_path))

            return True
        except:
            self.logger.exception('Error when updating the project via SFTP.')
            return False

    def update_hostname(self, new_hostname):
        """
        Updates the host with anew hostname.
        """
        old_hostname = self.node.name.replace(':', '-')
        new_hostname = new_hostname.replace(':','-')
        
        if old_hostname != new_hostname:
            self.logger.info("Updating current hostname from {} to {}.".format(old_hostname, new_hostname))

            with open("/etc/hostname", "w") as hostnameFile:
                hostnameFile.write(new_hostname)
                hostnameFile.close()

    def update_ip_address(self, new_ip_address):
        """
        Updates the host with a new ip address
        """
        if self.node.ip_address != new_ip_address:
            self.logger.info("Updating current ip address from {} to {}.".format(self.node.ip_address, new_ip_address))

            network_address = Sector.get_network_address_from_ip_address(new_ip_address)
            self.change_ip_address(new_ip_address=new_ip_address, net_address=network_address)
            self.node.ip_address = self.get_ip_address()[0]


    def update(self, new_config_node=None):
        """
        @todo : NODE! Update Code !!!!
        Updates the bbb with new data and refreshes the project.
        :return:
        """
        try:

            self.logger.info("Updating current configuration from {} to {}.".format(self.node, new_config_node))

            self.node = new_config_node
            
            self.update_ip_address(self.node.ip_address)

            self.update_hostname(self.node.name)

            self.update_project()
            self.write_node_configuration()

            self.logger.info("Current configuration updated successfully.")

        except IOError:
            self.logger.exception("Could not update hostname file.")

    def read_node_parameters(self):
        """
        Reads current node parameters, editing the name to include ':' where needed.
        """
        try:
            self.read_node_configuration()
        except IOError:
            self.logger.exception("Configuration file not found. Adopting default values.")

        name = subprocess.check_output(["hostname"]).strip('\n')
        indexes = [i for i, letter in enumerate(name) if letter == "-"]
        name = list(name)
        if len(indexes) > 2:
            name[indexes[1]] = ":"

        self.node.name = "".join(name)

    def read_node_configuration(self):
        """
        Reads the current node configuration from a binary file with the pickle module.
        """
        with open(self.configuration_file_path, 'rb') as file:
            self.node = pickle.load(file)
            file.close()
            self.logger.info("Node configuration file read successfully.")

    def write_node_configuration(self):
        """
        Writes the current node configuration to a binary file with the pickle module. Overrides old files.
        """
        with open(self.configuration_file_path, 'wb') as file:
            file.write(pickle.dumps(self.node))
            file.close()
            self.logger.info("Node configuration file updated successfully.")

    def get_ip_address(self):
        """
        Get the host's IP address with the 'ip addr' Linux command.
        :return: a tuple containing the host's ip address and network address.
        """
        command_out = subprocess.check_output("ip addr show dev {} scope global".format(self.interface_name).split())

        lines = command_out.split('\n')
        address_line = lines[2].split()[1]

        return ipaddress.IPv4Address(address_line.decode('utf-8')[0:address_line.index('/')]), \
               ipaddress.IPv4Network(address_line.decode('utf-8'), strict=False)

    def change_ip_address(self, new_ip_address, net_address, default_gateway_address = None):
        """
        Execute the connmanclt tool to change the host' IP address.
        :param new_ip_address: the new IP address. An ipaddress.IPv4Address object.
        :param net_address: new sub-network address. An ipaddress.IPv4Network object.
        :param default_gateway_address: the new default gateway
        :raise TypeError: new_ip_address or net_address are None or are neither ipaddress nor string objects.
        """
        if not new_ip_address:
            raise TypeError("The provided IP address is none.")
        elif type(new_ip_address) is not ipaddress.IPv4Address or type(new_ip_address) is not str:
            raise TypeError("The provided IP address is neither a string nor a ipaddress.IPv4Address object.")

        if not net_address:
            raise TypeError("The provided sub-network's address is none.")
        elif type(net_address) is not ipaddress.IPv4Address or type(net_address) is not str:
            raise TypeError("The provided sub-network's address is neither a "
                            "string nor a ipaddress.IPv4Address object.")

        self.logger.info('Changing current IP address from {} to {}'.format(self.get_ip_address()[0], new_ip_address))

        service = self.get_connman_service_name()
        self.logger.debug("Service for interface {} is {}.".format(self.interface_name, service))

        if default_gateway_address is None:
            default_gateway_address = Sector.get_default_gateway_of_address(new_ip_address)

        subprocess.check_output(
            ['connmanctl config {} ipv4 manual {} {} {}'.format(service, new_ip_address, net_address,
                                                                default_gateway_address)],
            shell=True)

        self.logger.debug('IP address after update is {}'.format(self.get_ip_address()[0]))

    def get_connman_service_name(self):
        """
        Returns the service name assigned to manage an interface.
        @fixme: services with spaces on their names won't be detected!
        :return: A service's name.
        :raise ValueError: service is not found.
        """
        services = subprocess.check_output(['connmanctl services'], stderr=subprocess.STDOUT,
                                           shell=True).decode('utf-8')

        for service in services.split():

            if service.startswith('ethernet_'):
                service_properties = subprocess.check_output(['connmanctl services ' + service],
                                                             stderr=subprocess.STDOUT,
                                                             shell=True).decode('utf-8')

                for prop in service_properties.split('\n'):
                    if prop.strip().startswith('Ethernet'):
                        data = prop.split('[')[1].strip()[:-1].split(',')
                        for d_info in data:
                            d_info = d_info.strip()
                            if d_info.startswith('Interface'):
                                if d_info == 'Interface={}'.format(self.interface_name):
                                    return service

        raise ValueError('Connmanctl service could not be found for interface {}'.format(self.interface_name))
