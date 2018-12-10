#!/usr/bin/python3
import ipaddress
import logging
import pickle
import os
import shutil
import subprocess
import time
import json

from common.entity.entities import Command, Node, Sector, Type, NodeState

class BBB:
    """
    A class to represent a Beaglebone host.
    """
    CONFIG_JSON_PATH = '/opt/device.json'

    def __init__(self, path, interface='eth0'):
        """
        Creates a new object instance.
        :param path: the configuration file's location
        """
        # Creates the objects that wrap the host's settings.
        self.node = Node()

        self.logger = logging.getLogger('BBB')

        #  Parameters that define absolute locations inside the host
        self.configuration_file_path = path

        # The interface used (ethernet port on the Beaglebone).
        self.interface_name = interface

        self.read_node_parameters()


        self.node.type = Type.from_code(Type.UNDEFINED)
        self.node.update_state(NodeState.CONNECTED)
        self.node.ip_address = str(ipaddress.ip_address(self.get_ip_address()[0]))

        self.current_config_json_mtime = None

        # Load the data from the cfg file.
        self.check_config_json()

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
                    self.node.type.code = int(config['device'])
                    self.node.details  = '{}\tbaudrate={}'.format(config['details'], config['baudrate'])
                    self.node.config_time = config['time']

                    self.write_node_configuration()

    def get_current_config(self):
        """
        Returns a dictionary containing the host's information and the command type.
        :return: message representing the current configuration.
        """
        self.check_config_json()
        dict_res = self.node.to_dict()
        return {'comm' : Command.PING, 'n' : dict_res[1]}

    def reboot(self):
        """
        Reboots this node.
        """
        self.logger.info("Setting state to reboot ... Waiting for the next ping ...")
        self.node.update_state(NodeState.REBOOTING)
        time.sleep(3.)
        self.logger.info("Rebooting system.")
        os.system('reboot')

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

    def update_ip_address(self, new_ip_address, new_mask, new_gateway):
        """
        Updates the host with a new ip address
        """
        if self.node.ip_address != new_ip_address:
            self.logger.info("Updating current ip address from {} to {}, mask {}, default gateway {}.".format(
                self.node.ip_address, new_ip_address, new_mask, new_gateway))

            self.change_ip_address(new_ip_address, new_gateway, new_mask)
            self.node.ip_address = self.get_ip_address()[0]


    def read_node_parameters(self):
        """
        Reads current node parameters, editing the name to include ':' where needed.
        """
        try:
            self.read_node_configuration()
        except IOError:
            self.logger.exception("Configuration file not found. Adopting default values.")

        name = subprocess.check_output(["hostname"]).decode('utf-8').strip('\n')
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
        command_out = subprocess.check_output("ip addr show dev {} scope global".format(self.interface_name).split()).decode('utf-8')

        lines = command_out.split('\n')
        address_line = lines[2].split()[1]

        return ipaddress.IPv4Address(address_line[0:address_line.index('/')]), \
               ipaddress.IPv4Network(address_line, strict=False)

    def change_ip_address(self, new_ip_address, new_mask, new_gateway):
        """
        Execute the connmanclt tool to change the host' IP address.
        :param new_ip_address: the new IP address. An ipaddress.IPv4Address object.
        :param net_address: new sub-network address. An ipaddress.IPv4Network object.
        :param default_gateway_address: the new default gateway
        :raise TypeError: new_ip_address or net_address are None or are neither ipaddress nor string objects.
        """ 
        self.logger.info('Changing current IP address from {} to {}'.format(self.get_ip_address()[0], new_ip_address))

        service = self.get_connman_service_name()
        self.logger.debug("Service for interface {} is {}.".format(self.interface_name, service))

        if new_gateway is None:
            new_gateway = Sector.get_default_gateway_of_address(new_ip_address)

        subprocess.check_output(
            ['connmanctl config {} --ipv4 manual {} {} {}'.format(service, new_ip_address, new_mask,
                                                                new_gateway)],
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
