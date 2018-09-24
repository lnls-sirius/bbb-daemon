import logging
import os
import threading
from common.entity.metadata import Singleton
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer

PASSIVE_PORT_MIN_DEFAULT, PASSIVE_PORT_MAX_DEFAULT = 3000, 3010


class BBBHandler(FTPHandler):
    """
    A class to handle FTP requests and events.
    """

    def on_connect(self):
        print("Client \t%s:%s\tCONNECTED" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        print("Client \t%s:%s\tDISCONNECTED" % (self.remote_ip, self.remote_port))
        pass

    def on_login(self, username):
        # do something when user login
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        pass

    def on_file_received(self, file):
        # do something when a file has been received
        print('Operation not supported!')
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)


class FTPServerManager(metaclass=Singleton):
    """
    A simple class to manage FTP servers.
    """

    def __init__(self, ftp_home_dir='/home/', ftp_port: int = 1026, passive_port_min: int = 3000,
                     passive_port_max: int = 3010):
        """
        Starts a new FTP server.
        :param ftp_home_dir: FTP's home directory.
        :param ftp_port: the connection's port.
        :param passive_port_min: @todo
        :param passive_port_max: @todo
        """

        self.home = ftp_home_dir
        self.listening_port = ftp_port
        self.logger = logging.getLogger('sftp')

        if os.path.exists(self.home) and not os.path.isdir(self.home):
            raise ValueError('FTP server failed to start! {} path is not valid!'.format(self.home))

        if not os.path.isdir(ftp_home_dir):
            os.mkdir(ftp_home_dir)

        authorizer = DummyAuthorizer()
        authorizer.add_anonymous(ftp_home_dir, perm="elr")

        handler = BBBHandler
        handler.authorizer = authorizer
        handler.masquerade_address = '10.0.6.70'
        handler.permit_foreign_addresses = True

        if passive_port_max < 2000 or passive_port_min < 1999 or passive_port_max <= passive_port_min:
            passive_port_min, passive_port_max = PASSIVE_PORT_MIN_DEFAULT, PASSIVE_PORT_MAX_DEFAULT

        handler.passive_ports = range(passive_port_min, passive_port_max)

        self.server = ThreadedFTPServer(("0.0.0.0", ftp_port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

        self.start_server()

    def start_server(self):

        self.logger.info('Starting FTP server at {} {}.'.format(self.home, self.listening_port))
        self.server_thread.start()

    def stop_ftp_server(self):
        """
        Stops the FTP server.
        """
        self.logger.info('Stopping FTP server.')
        self.server.close_all()
        self.logger.info('FTP server is shut.')

