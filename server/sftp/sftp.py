import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

PASSIVE_PORT_MIN_DEFAULT, PASSIVE_PORT_MAX_DEFAULT = 60000, 65535


class BBBHandler(FTPHandler):

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


def start_ftp_server(ftp_home_dir='/home/', ftp_port: int = 1026, passive_port_min: int = 60000,
                     passive_port_max: int = 65535):
    if os.path.exists(ftp_home_dir) and not os.path.isdir(ftp_home_dir):
        print('FTP Server Failed to Start! FTP_HOME Path is not valid !!')
        return
    if not os.path.isdir(ftp_home_dir):
        os.mkdir(ftp_home_dir)

    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(ftp_home_dir, perm="elr")

    handler = BBBHandler
    handler.authorizer = authorizer

    if passive_port_max < 2000 or passive_port_min < 1999 or passive_port_max <= passive_port_min:
        passive_port_min, passive_port_max = PASSIVE_PORT_MIN_DEFAULT, PASSIVE_PORT_MAX_DEFAULT

    #handler.masquerade_address = '10.0.6.70'
    #handler.passive_ports = range(passive_port_min, passive_port_max)

    print('FTP server at {} {}'.format(ftp_home_dir, ftp_port))
    server = FTPServer(("0.0.0.0", ftp_port), handler)
    server.serve_forever()
