import signal
import time

from network.commandinterface import CommandInterface
from network.daemon import DaemonHostListener

from control.controller import MonitorController

if __name__ == '__main__':

    def sighandler(signum, frame):
        global running
        running = False


    running = True

    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)

    c = MonitorController()
    n = DaemonHostListener(controller=c)
    i = CommandInterface(controller=c)

    while running:
        time.sleep(1)

    c.stopAll()
    n.stopAll()
    i.stopAll()

    print("Quiting server")
