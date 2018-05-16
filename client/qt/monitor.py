import sys

from PyQt5.QtWidgets import QApplication
from gui.interface import MonitorInterface

serverAddress = "10.0.6.70"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    i = MonitorInterface(server = serverAddress)
    sys.exit(app.exec_())
