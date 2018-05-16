import pickle
import struct


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
