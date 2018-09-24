import argparse
import logging
import sys

from PyQt5.QtWidgets import QApplication
from client.qt.comm.commandinterface import CommandNetworkInterface
from client.qt.gui.controller import QtInterfaceController
from client.qt.gui.interface import QtInterface

DEFAULT_SERVER_ADDR = 'localhost'
DEFAULT_SERVER_PORT = 6789

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Qt5 based client interface.')

    parser.add_argument('--server-address', '-s', nargs='?', default=DEFAULT_SERVER_ADDR,
                        help="Server's IP address", dest='server_address')

    parser.add_argument('--server-port', '-p', nargs='?', default=DEFAULT_SERVER_PORT,
                        help="Server's port", dest='server_port')

    args = vars(parser.parse_args())

    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)-15s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    command_interface = CommandNetworkInterface(server_address=args['server_address'], server_port=args['server_port'])
    controller = QtInterfaceController()

    app = QApplication(sys.argv)
    i = QtInterface()

    sys.exit(app.exec_())
