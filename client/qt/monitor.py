from gui.interface import MonitorInterface
from PyQt4.QtGui import QApplication

import sys

if __name__ == '__main__':

    app = QApplication(sys.argv)
    i = MonitorInterface ()
    i.show ()
    sys.exit(app.exec_())
