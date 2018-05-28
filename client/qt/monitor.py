import sys

from PyQt5.QtWidgets import QApplication

from gui.interface import MonitorInterface

serverAddress = "localhost"
servPort = 6789

if __name__ == '__main__':

    print("arg[1]=servAddress\targ[2]=servPort")
    if len(sys.argv) == 2:
        serverAddress = sys.argv[1]
    else:
        print("Using default")
    try:
        servPort = int(servPort)
    except:
        servPort = 6789

    print("arg[1]={}\targ[2]={}\t".format(serverAddress, servPort))

    app = QApplication(sys.argv)
    i = MonitorInterface(server=serverAddress, servPort=servPort)
    sys.exit(app.exec_())
