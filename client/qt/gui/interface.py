from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from common.entity.entities import Sector
from gui.controller import GUIController
from gui.nodeDialog import NodeDialog
from gui.typeDialog import TypeDialog
from gui.tab import MonitorTab


class MonitorInterface(QMainWindow):
    WIDTH = 1600
    HEIGHT = 1200

    updateIcon = pyqtSignal(int)

    def __init__(self, server="localhost"):

        super().__init__()

        self.controller = GUIController(server=server)

        self.menubar = self.menuBar()
        self.editMenu = self.menubar.addMenu('&Edit')

        self.addType = self.editMenu.addAction('&Types Management')
        self.addType.setShortcut("Ctrl+T")
        self.addType.triggered.connect(self.appendType)
        self.addType.setShortcutContext(Qt.ApplicationShortcut)

        self.addNode = self.editMenu.addAction('&Nodes Management')
        self.addNode.setShortcut("Ctrl+N")
        self.addNode.triggered.connect(self.appendNode)
        self.addNode.setShortcutContext(Qt.ApplicationShortcut)

        self.exitMenu = self.menubar.addAction('E&xit')
        self.exitMenu.triggered.connect(self.exit)
        self.exitMenu.setShortcut("Ctrl+X")
        self.exitMenu.setShortcutContext(Qt.ApplicationShortcut)

        self.centralwidget = QWidget()

        self.widgetbox = QVBoxLayout()
        self.widgetbox.setContentsMargins(10, 10, 10, 10)
        self.widgetbox.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)

        for index, i in enumerate(Sector.sectors()):
            self.tabs.insertTab(index,
                                MonitorTab(parent=self.tabs, sector=str(i), controller=self.controller, tabIndex=index,
                                           updateIcon=self.updateIcon), str(i))

        self.widgetbox.addWidget(self.tabs)
        self.centralwidget.setLayout(self.widgetbox)

        self.setWindowTitle("Controls Group's Single Board Computer Monitor")
        self.setCentralWidget(self.centralwidget)

        self.setGeometry(500, 500, MonitorInterface.WIDTH, MonitorInterface.HEIGHT)

        self.icons = QIcon()
        self.icons.addFile('ico/bbb16x16.png', QSize(16, 16))
        self.icons.addFile('ico/bbb24x24.png', QSize(24, 24))
        self.icons.addFile('ico/bbb32x32.png', QSize(32, 32))
        self.icons.addFile('ico/bbb48x48.png', QSize(48, 48))
        self.icons.addFile('ico/bbb256x256.png', QSize(256, 256))

        self.setWindowIcon(self.icons)

        self.updateIcon.connect(self.test)
        self.show()

    def test(self, tabIndex):

        if self.tabs.widget(tabIndex).isInWarningStateState():
            self.tabs.setTabIcon(tabIndex, QIcon.fromTheme("dialog-warning"))
        else:
            self.tabs.setTabIcon(tabIndex, QIcon())

    def appendType(self):
        typeDialog = TypeDialog(controller=self.controller)
        self.centerWindow(typeDialog)
        typeDialog.show()

    def appendNode(self):
        nodeDialog = NodeDialog(controller=self.controller)
        self.centerWindow(nodeDialog)
        nodeDialog.show()

    def stopAll(self):
        for tabIndex in range(self.tabs.count()):
            self.tabs.widget(tabIndex).stop()

    def closeEvent(self, evt):
        self.stopAll()
        QMainWindow.closeEvent(self, evt)

    def exit(self):
        self.stopAll()
        self.close()

    def centerWindow(self, windows_to_center):
        qtRectangle = windows_to_center.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        windows_to_center.move(qtRectangle.topLeft())
