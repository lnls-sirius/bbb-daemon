import control.controller
import gui.interface

from PyQt4.QtGui import QApplication
import sys

if __name__ == '__main__':

    c = control.controller.MonitorController ()

    app = QApplication(sys.argv)
    i = gui.interface.MonitorInterface (controller = c)
    i.show ()

    sys.exit(app.exec_())
