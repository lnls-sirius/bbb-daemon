import fcntl
import pickle
import re
import struct
import socket
import subprocess


class NetUtils:
    """
    A static class to send data through a given connection.
    """

    @staticmethod
    def send_command(connection, command):
        """
        Sends a command through the connection.
        :param connection: the connection to be used to send the integer.
        :param command: A 4-byte integer representing a command.
        """
        connection.send(struct.pack("!i", command))

    @staticmethod
    def recv_command(connection):
        """
        Receives a single 4-byte integer.
        :param connection: the connection to be used to receive the integer.
        :return: the integer representing a command.
        """
        return struct.unpack("!i", connection.recv(4))[0]

    @staticmethod
    def send_data(connection, data):
        """
        Sends bytes through the connection. First, its sends how many bytes the data is composed of.
        :param connection: the connection to be used to send the object.
        :param data: the data to bem sent.
        """
        connection.send(struct.pack("!i", len(data)))
        connection.send(data)

    @staticmethod
    def recv_data(connection):
        """
        Receives bytes from a connection. First, its reads how many bytes were sent.
        :param connection: the connection to be used to receive the object.
        :return: the received data.
        """
        data_size = struct.unpack("!i", connection.recv(4))[0]
        return connection.recv(data_size)

    @staticmethod
    def recv_object(connection):
        """
        Receives an object and de-serializes it.
        :param connection: the connection to be used to receive the object.
        :return: de-serialized object.
        """
        return pickle.loads(NetUtils.recv_data(connection))

    @staticmethod
    def send_object(connection, obj=None):
        """
        Serialize the object with pickle and sends it through the connection.
        :param connection: the connection that will be used to send the object.
        :param obj: the object to be sent.
        """
        NetUtils.send_data(connection, pickle.dumps(obj))

    @staticmethod
    def checksum(data_str: str):
        packet = data_str.strip().encode('utf-8')
        total = 0
        # Add up 16-bit words
        num_words = len(packet) // 2
        for chunk in struct.unpack("!%sH" % num_words, packet[0:num_words * 2]):
            total += chunk

        # Add any left over byte
        if len(packet) % 2:
            total += ord(chr(packet[-1])) << 8

        # Fold 32-bits into 16-bits
        total = (total >> 16) + (total & 0xffff)
        total += total >> 16
        return ~total + 0x10000 & 0xffff

    @staticmethod
    def verify_msg(data: str):
        """
        This method must be updated as the data format sent by the bbb is modified
        BBB sends this: {chk} | {cmd} | {name} | {type} | {ipAddr} | {sha}
        :param data: received packet to be verified.
        :return: Array containing the data, [] if error.
        """
        splt = data.split("|")
        if len(splt) != 6:
            # Error !
            return []
        message = data[(len(splt[0]) + 1):]
        res = NetUtils.checksum(message)
        if int(res) == int(splt[0]):
            return splt
        else:
            return []

    re_ipv4 = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    re_mask_ipv4 = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

    @staticmethod
    def get_ip_address(if_name: str):
        if_name = if_name.encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', if_name[:15])
        )[20:24])

    @staticmethod
    def change_ip(desired_ip: str = None, interface_name: str = 'eth0', net_mask: str = '255.255.255.0',
                  gateway: str = None):
        """
        @todo: now that i know the service i can do whatever i want !
        Execute the connmanclt tool to change the host' IP address
        :param desired_ip: the new IP address
        :param interface_name: ethernet interface to have its address changed.
        :param net_mask: network of the new ip address
        :param gateway: new default gateway
        :return: (True or False), message
        """
        if not desired_ip:
            return False, 'Desired ip not set !'

        service = get_service(interface_name=interface_name)
        if not service:
            return False, 'Service could\'t be found'

        # @todo make the magic happen
        # @todo make two different patterns for mask and ip. Limit them with the correct values.
        if not re.match(re_mask_ipv4, net_mask):
            return False, 'The net_mask={} doesn\'t match the mask pattern.'.format(net_mask)
        if not re.match(re_ipv4, desired_ip):
            return False, 'The desiredIp={} doesn\'t match the ipv4 pattern.'.format(desired_ip)
        if gateway:
            if not re.match(re_ipv4, gateway):
                return False, 'The gateway={} doesn\'t match the ipv4 pattern.'.format(gateway)
        else:
            g_aux = desired_ip.split('.')
            if len(g_aux) == 4:
                g_aux[3] = '1'
                gateway = ''
                for g in g_aux:
                    gateway += g + '.'
                gateway = gateway[:-1]

        res = subprocess.check_output(
            ['connmanctl config {} ipv4 manual {} {} {}'.format(service, desired_ip, net_mask, gateway)],
            shell=True)
        return True, 'Successfully modified the ipv4 address. {}'.format(res)

    @staticmethod
    def get_service(interface_name: str = 'eth0'):
        """
        Return the service name from an interface.
        @fixme: services with spaces on their names won't be detected !
        :return: The service name or None !
        """
        res = subprocess.check_output(['connmanctl services'], stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        res = res.split()
        for s in res:
            if s.startswith('ethernet_'):
                res = subprocess.check_output(['connmanctl services --properties ' + s], stderr=subprocess.STDOUT,
                                              shell=True).decode(
                    'utf-8')
                print(res)
                res = res.split('\n')
                for p in res:
                    if p.strip().startswith('Ethernet'):
                        print('Found it!' + p)
                        data = p.split('[')[1].strip()[:-1].split(',')
                        for d_info in data:
                            d_info = d_info.strip()
                            if d_info.startswith('Interface'):
                                print(d_info)
                                if d_info == 'Interface={}'.format(interface_name):
                                    print('The service related to {} is {}'.format(interface_name, s))
                                    return s
                        print(data)
        return None
