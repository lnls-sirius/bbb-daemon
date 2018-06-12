import signal
import time
import sys
from threading import Thread

from waitress import serve

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

import app
from control.controller import MonitorController
from sftp.sftp import start_ftp_server


def init_conf():
    REDIS_SERVER_IP = '0.0.0.0'
    REDIS_SERVER_PORT = 6379

    BBB_UDP = 9876
    BBB_TCP = 9877

    WEB_CLIENT_SERVER_PORT = 4850

    COM_INTERFACE_TCP = 6789

    WORKERS_NUM = 10

    FTP_SERVER_PORT = 1026
    FTP_HOME_DIR = '/home/carneirofc/types/'

    print("=======================================================")
    print('                 BBB DAEMON SERVER STARTED             ')
    print("=======================================================")
    print('\tArguments:')
    print("\targ[1]=REDIS_SERVER_IP\n"
          "\targ[2]=REDIS_SERVER_PORT\n"
          "\targ[3]=BBB_UDP\n"
          "\targ[4]=BBB_TCP\n"
          "\targ[5]=COM_INTERFACE_TCP\n"
          "\targ[6]=WORKERS_NUM\n"
          "\targ[7]=FTP_SERVER_PORT\n"
          "\targ[8]=FTP_HOME_DIR\n")

    try:
        REDIS_SERVER_IP = sys.argv[1]
        REDIS_SERVER_PORT = int(sys.argv[2])
        BBB_UDP = int(sys.argv[3])
        BBB_TCP = int(sys.argv[4])
        COM_INTERFACE_TCP = int(sys.argv[5])
        WORKERS_NUM = int(sys.argv[6])
        FTP_SERVER_PORT = int(sys.argv[7])
        FTP_HOME_DIR = sys.argv[8]
    except:
        pass
        print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t'.format(REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP,
                                                        COM_INTERFACE_TCP, WORKERS_NUM, \
                                                        WEB_CLIENT_SERVER_PORT, FTP_HOME_DIR, FTP_SERVER_PORT))
    return REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP, COM_INTERFACE_TCP, WORKERS_NUM, \
           WEB_CLIENT_SERVER_PORT, FTP_HOME_DIR, FTP_SERVER_PORT


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
    REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP, COM_INTERFACE_TCP, WORKERS_NUM, WEB_CLIENT_SERVER_PORT, \
    FTP_HOME_DIR, FTP_SERVER_PORT = init_conf()

    running = True

    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)

    # Start FTP server
    Thread(target=start_ftp_server, args=[FTP_HOME_DIR, FTP_SERVER_PORT]).start()

    c = MonitorController(redis_server_ip=REDIS_SERVER_IP, redis_server_port=REDIS_SERVER_PORT,
                          sftp_home_dir=FTP_HOME_DIR)
    n = DaemonHostListener(controller=c, bbbUdpPort=BBB_UDP, bbbTcpPort=BBB_TCP, workers=WORKERS_NUM)
    i = CommandInterface(controller=c, comInterfacePort=COM_INTERFACE_TCP)

    Thread(target=stop_services, args=[c, n, i]).start()

    app.set_controller(c=c)

    serve(app.get_wsgi_app(), host='0.0.0.0', port=WEB_CLIENT_SERVER_PORT)

    print("Server Stopped")
