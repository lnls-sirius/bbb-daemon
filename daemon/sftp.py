#!/usr/bin/python
import errno
import sys
import ftplib
import os
import time

user = "anonymous"
password = "anonymous"
interval = 0.05

ftp = ftplib.FTP()


def connect_to_ftp_server(sftp_server_addr: str = '0.0.0.0', sftp_port: int = 22):
    ftp.connect(sftp_server_addr, sftp_port)
    ftp.login(user, password)


def downloadFiles(path, destination):
    """
        Download the file located on the path and copy it to the destination
    :param path: file or folder to be copied
    :param destination: Place on the client to copy to
    :return:
    """
    try:
        ftp.cwd(path)
        os.chdir(destination)
        mkdir_p(destination[0:len(destination) - 1] + path)
        print("Created: " + destination[0:len(destination) - 1] + path)
    except OSError:
        pass
    except ftplib.error_perm:
        print("Error: could not change to " + path)
        sys.exit("Ending Application")

    filelist = ftp.nlst()

    for file in filelist:
        time.sleep(interval)
        try:
            ftp.cwd(path + file + "/")
            downloadFiles(path + file + "/", destination)
        except ftplib.error_perm:
            os.chdir(destination[0:len(destination) - 1] + path)

            try:
                ftp.retrbinary("RETR " + file, open(os.path.join(destination + path, file), "wb").write)
                print("Downloaded: " + file)
            except:
                print("Error: File could not be downloaded " + file)
    return


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


