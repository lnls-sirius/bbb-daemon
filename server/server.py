import signal
import time
import sys
from threading import Thread

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

import app
from control.controller import MonitorController


def init_conf():
    REDIS_SERVER_IP = "10.0.6.70"
    REDIS_SERVER_PORT = 6379

    BBB_UDP = 9876
    BBB_TCP = 9877

    WEB_CLIENT_SERVER_PORT = 4850

    COM_INTERFACE_TCP = 6789

    WORKERS_NUM = 10

    print("arg[1]=REDIS_SERVER_IP\t"
          "arg[2]=REDIS_SERVER_PORT\t"
          "arg[3]=BBB_UDP\t"
          "arg[4]=BBB_TCP\t"
          "arg[5]=COM_INTERFACE_TCP"
          "\targ[6]=WORKERS_NUM")

    if len(sys.argv) is not 6 or len(sys.argv) is not 7:
        print("using: {}\t{}\t{}\t{} ".format(REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP,
                                              COM_INTERFACE_TCP))
        print("WORKERS={}".format(WORKERS_NUM))
    else:
        REDIS_SERVER_IP = sys.argv[1]
        REDIS_SERVER_PORT = int(sys.argv[2])
        BBB_UDP = int(sys.argv[3])
        BBB_TCP = int(sys.argv[4])
        COM_INTERFACE_TCP = int(sys.argv[5])
        try:
            WORKERS_NUM = int(sys.argv[6])
        except:
            WORKERS_NUM = 10

    return REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP, COM_INTERFACE_TCP, WORKERS_NUM, WEB_CLIENT_SERVER_PORT


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
    REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP, COM_INTERFACE_TCP, WORKERS_NUM, WEB_CLIENT_SERVER_PORT \
        = init_conf()

    running = True

    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)

    c = MonitorController(redis_server_ip=REDIS_SERVER_IP, redis_server_port=REDIS_SERVER_PORT)
    n = DaemonHostListener(controller=c, bbbUdpPort=BBB_UDP, bbbTcpPort=BBB_TCP, workers=WORKERS_NUM)
    i = CommandInterface(controller=c, comInterfacePort=COM_INTERFACE_TCP)

    Thread(target=stop_services, args=[c, n, i]).start()

    app.start_webserver(WEB_CLIENT_SERVER_PORT, c)

    print("Server Stopped")
