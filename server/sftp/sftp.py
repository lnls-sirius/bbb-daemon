from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class BBBHandler(FTPHandler):

    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        print('Client disconnected')
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


def start_ftp_server(ftp_home_dir='/home/', ftp_port: int = 1026):
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(ftp_home_dir, perm="elr")

    handler = BBBHandler
    handler.authorizer = authorizer

    server = FTPServer(("0.0.0.0", ftp_port), handler)
    server.serve_forever()

