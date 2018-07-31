import argparse
import sys

from PyQt5.QtWidgets import QApplication
from client.qt.gui.interface import QtInterface

serverAddress = "localhost"
servPort = 6789

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Qt5 based client interface.')

    parser.add_argument('--server-address', '-s', nargs='?', default='localhost',
                        help="Server's IP address", dest='server_address')

    parser.add_argument('--server-port', '-s', nargs='?', default=6789,
                        help="Server's port", dest='server_port')

    args = vars(parser.parse_args())

    app = QApplication(sys.argv)
    i = QtInterface(server=serverAddress, server_port=servPort)
    sys.exit(app.exec_())
