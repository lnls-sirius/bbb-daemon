#!/usr/bin/python3
import os
import signal
import time
import sys
from threading import Thread

from envs import *
from waitress import serve

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

from app import app
from control.controller import MonitorController
from sftp.sftp import start_ftp_server
 

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


if __name__ == '__main__':
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

    # app.set_controller(c=MonitorController.monitor_controller)

    # serve(app.get_wsgi_app(), host='0.0.0.0', port=WEB_CLIENT_SERVER_PORT)
    # app.get_wsgi_app().run(debug=False, use_reloader=False, port=WEB_CLIENT_SERVER_PORT, host="0.0.0.0")
    
    
    # print("Server Stopped")
