#!/usr/bin/python3
import os
import signal
import time
import sys
from threading import Thread

from waitress import serve

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

from app import app
from control.controller import MonitorController
from sftp.sftp import start_ftp_server
from os import environ

REDIS_SERVER_IP = environ.get('REDIS_SERVER_IP', '0.0.0.0')
REDIS_SERVER_PORT = int(environ.get('REDIS_SERVER_PORT', 6379))

BBB_UDP = int(environ.get('BBB_UDP', 9876))
BBB_TCP = int(environ.get('BBB_TCP', 9877))

COM_INTERFACE_TCP = int(environ.get('COM_INTERFACE_TCP', 6789))
WORKERS_NUM = int(environ.get('WORKERS_NUM', 10))
WEB_CLIENT_SERVER_PORT = int(environ.get('FLASK_PORT', 4850))
FTP_SERVER_PORT = int(environ.get('FTP_SERVER_PORT', 21))
FTP_HOME_DIR = environ.get('FTP_HOME', '/root/bbb-daemon/types_repository/') 

def sighandler(signum, frame):
    global running
    running = False


def stop_services(c: MonitorController, n: DaemonHostListener, i: CommandInterface):
    while running:
        time.sleep(1)

    c.stopAll()
    n.stopAll()
    i.stopAll()
    print("Services Stopped")


print("=======================================================")
print('                 BBB DAEMON SERVER STARTED             ')
print("=======================================================")

running = True

signal.signal(signal.SIGTERM, sighandler)
signal.signal(signal.SIGINT, sighandler)

if not os.path.exists(FTP_HOME_DIR):
    os.mkdir(FTP_HOME_DIR)

# Start FTP server
Thread(target=start_ftp_server, args=[FTP_HOME_DIR, FTP_SERVER_PORT]).start()

MonitorController.monitor_controller = MonitorController(redis_server_ip=REDIS_SERVER_IP,
                                                            redis_server_port=REDIS_SERVER_PORT,
                                                            sftp_home_dir=FTP_HOME_DIR)
                                                    
n = DaemonHostListener(controller=MonitorController.monitor_controller, bbbUdpPort=BBB_UDP, bbbTcpPort=BBB_TCP,
                        workers=WORKERS_NUM)
i = CommandInterface(controller=MonitorController.monitor_controller, comInterfacePort=COM_INTERFACE_TCP)

Thread(target=stop_services, args=[MonitorController.monitor_controller, n, i]).start()
