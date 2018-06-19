import fcntl
import pickle
import struct
import socket


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
    return (~total + 0x10000 & 0xffff)


def get_ip_address(ifname: str):
    ifname = ifname.encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def verify_msg(data: str):
    """
        This method must be update as the data format sent by the bbb is modified
        BBB sends this: {chk} | {cmd} | {name} | {type} | {ipAddr} | {sha}
    :param data:
    :return: Array containing the data, [] if error.
    """
    splt = data.split("|")
    if len(splt) != 6:
        # Error !
        return []
    message = data[(len(splt[0]) + 1):]
    res = checksum(message)
    if int(res) == int(splt[0]):
        return splt
    else:
        return []


class NetUtils():

    @staticmethod
    def sendCommand(connection, command):
        return connection.send(struct.pack("!i", command))

    @staticmethod
    def recvCommand(connection):
        return struct.unpack("!i", connection.recv(4))[0]

    @staticmethod
    def sendData(connection, data):
        connection.send(struct.pack("!i", len(data)))
        connection.send(data)

    @staticmethod
    def recvData(connection):
        dataSize = struct.unpack("!i", connection.recv(4))[0]
        return connection.recv(dataSize)

    @staticmethod
    def recvObject(connection):
        return pickle.loads(NetUtils.recvData(connection))

    @staticmethod
    def sendObject(connection, obj=None):
        NetUtils.sendData(connection, pickle.dumps(obj))
