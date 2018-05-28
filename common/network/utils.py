import fcntl
import pickle
import struct
import socket


def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)


def checksum(msg):
    if len(msg) % 2 != 0:
        msg += "\x00"
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def verify_msg(data: str):
    """
        BBB sends this: {chk} | {cmd} | {name} | {type} | {ipAddr}
    :param data:
    :return: Array containing the data, [] if error.
    """
    splt = data.split("|")
    if len(splt) != 5:
        # Error !
        return []
    if checksum(splt[0]) != data[len(splt[0]):]:
        return []
    return splt


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
