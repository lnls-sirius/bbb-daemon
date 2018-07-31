import pickle
import struct
from common.entity.entities import Command


class NetUtils:
    """
    A static class to send data through a given connection.
    """

    @staticmethod
    def send_failure(connection, error_message):
        """
        Sends a failure message to a given connection socket.
        :param connection: the connection to be used to send the integer.
        :param error_message: a message explaining the failure.
        """
        NetUtils.send_command(connection, Command.FAILURE)
        NetUtils.send_object(connection, error_message)

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
    def compare_checksum(data: str):
        """
        Compares the received message's and the object checksum fields. This method must be updated
        as the data format sent by the bbb is modified.
        Message content: {chk} | {cmd} | {name} | {type} | {ipAddr} | {sha}
        :param data: received packet to be verified.
        :return: Array containing the data.
        :raise ValueError: checksum fields do not match.
        """
        splt = data.split("|")
        if len(splt) != 6:
            # Error !
            return []
        message = data[(len(splt[0]) + 1):]
        res = NetUtils.checksum(message)
        if int(res) == int(splt[0]):
            return splt

        raise ValueError("Computed and received checksum fields do not match.")
