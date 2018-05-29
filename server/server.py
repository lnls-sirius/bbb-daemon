import signal
import time
import sys

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

from control.controller import MonitorController

REDIS_SERVER_IP = "localhost"
REDIS_SERVER_PORT = 6379

BBB_UDP = 9876
BBB_TCP = 9877

COM_INTERFACE_TCP = 6789

WORKERS_NUM = 10

if __name__ == '__main__':
    print(
        "arg[1]=REDIS_SERVER_IP\targ[2]=REDIS_SERVER_PORT\targ[3]=BBB_UDP\targ[4]=BBB_TCP\targ[5]=COM_INTERFACE_TCP\targ[6]=WORKERS_NUM")
    if len(sys.argv) is not 6 or len(sys.argv) is not 7 :
        print("using: {}:{}:{}:{} ".format(REDIS_SERVER_IP, REDIS_SERVER_PORT, BBB_UDP, BBB_TCP,
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


    def sighandler(signum, frame):
        global running
        running = False


    running = True

    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)

    # bbbUdpPort=9876, bbbTcpPort=9877

    c = MonitorController(redis_server_ip=REDIS_SERVER_IP, redis_server_port=REDIS_SERVER_PORT)
    n = DaemonHostListener(controller=c, bbbUdpPort=BBB_UDP, bbbTcpPort=BBB_TCP, workers=WORKERS_NUM)
    i = CommandInterface(controller=c, comInterfacePort=COM_INTERFACE_TCP)

    while running:
        time.sleep(1)

    c.stopAll()
    n.stopAll()
    i.stopAll()

    print("Quiting server")
# labimas
# lab_imas@18
