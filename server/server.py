import signal
import time
import sys

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

from control.controller import MonitorController

REDIS_SERVER_IP = "localhost"
REDIS_SERVER_PORT = 6379

if __name__ == '__main__':

    if len(sys.argv) is not 3:
        print("arg[1]=REDIS_SERVER_IP arg[2]=REDIS_SERVER_PORT")
        print("using: {}:{}".format(REDIS_SERVER_IP, REDIS_SERVER_PORT))
    else:
        REDIS_SERVER_IP = sys.argv[1]
        REDIS_SERVER_PORT = int(sys.argv[2])


    def sighandler(signum, frame):
        global running
        running = False


    running = True

    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)

    c = MonitorController(redis_server_ip=REDIS_SERVER_IP, redis_server_port=REDIS_SERVER_PORT)
    n = DaemonHostListener(controller=c)
    i = CommandInterface(controller=c)

    while running:
        time.sleep(1)

    c.stopAll()
    n.stopAll()
    i.stopAll()

    print("Quiting server")
# labimas
# lab_imas@18