#!/usr/bin/python
import ftplib

import os

import ftputil


class MySession(ftplib.FTP):

    def __init__(self, host, userid, password, port):
        """Act like ftplib.FTP's constructor but connect to another port."""
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(userid, password)


# Download some files from the login directory.

def download_from_ftp(sftp_server_addr: str = '0.0.0.0', sftp_port: int = 22, path=None, destination=None):
    print('\n\ndownload_from_ftp\n\npath={}\tdestination={}'.format(path, destination))
    with ftputil.FTPHost(sftp_server_addr, 'anonymous', 'anonymous', port=sftp_port,
                         session_factory=MySession) as host:
        host.chdir(path)
        names = host.listdir(host.curdir)
        for name in names:
            if host.path.isfile(name):
                # Remote name, local name
                host.download(name, destination + '/' + name)
                print('Downloaded {} at {}'.format(name, (destination + '/' + name)))
            elif host.path.isdir(name):
                cur_dir = host.getcwd()
                download_dir(host=host, path=name, destination=destination + name)
                host.chdir(cur_dir)


def download_dir(host=None, path=None, destination=None):
    if not os.path.isdir(destination):
        os.mkdir(destination)
    host.chdir(path)
    names = host.listdir(host.curdir)
    for name in names:
        print('name in names={}'.format(name))
        if host.path.isfile(name):
            # Remote name, local name
            host.download(name, destination + '/' + name)
            print('Downloaded {} at {}'.format(name, (destination + '/' + name)))
        elif host.path.isdir(name):
            cur_dir = host.getcwd()
            download_dir(host=host, path=name, destination=destination + '/' + name)
            host.chdir(cur_dir)
