import comm.network
import control.controller
import gui.interface

from PyQt4.QtGui import QApplication
import sys

if __name__ == '__main__':

    c = control.controller.MonitorController ()
    n = comm.network.NetDaemon (controller = c)

    app = QApplication(sys.argv)
    i = gui.interface.MonitorInterface (controller = c)
    i.show ()

    appReturn = app.exec_()
    print ("oi")
    n.stopAll ()

    sys.exit(appReturn)
