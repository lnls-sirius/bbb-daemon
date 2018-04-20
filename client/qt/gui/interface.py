from common.entity.entities import Sector
from gui.controller import GUIController
from gui.typeDialog import TypeDialog
from gui.nodeDialog import NodeDialog
from gui.tab import MonitorTab

from PyQt4.QtGui import QMainWindow,\
    QGridLayout, QLabel, QPushButton, QTableView, QAbstractItemView, QInputDialog,\
    QTabWidget, QTextEdit, QVBoxLayout

from PyQt4.QtCore import *
from PyQt4.Qt import QWidget, QLineEdit, QColor, QBrush

import threading

class MonitorInterface (QMainWindow):

    WIDTH = 1600
    HEIGHT = 1200

    def __init__(self, parent = None):

        QMainWindow.__init__(self, parent)

        self.controller = GUIController ()

        self.menubar = self.menuBar()
        self.editMenu = self.menubar.addMenu('&Edit')

        self.addType = self.editMenu.addAction('&Types Management')
        self.addType.setShortcut("Ctrl+T")
        self.addType.triggered.connect (self.appendType)
        self.addType.setShortcutContext(Qt.ApplicationShortcut)

        self.addNode = self.editMenu.addAction('&Nodes Management')
        self.addNode.setShortcut("Ctrl+N")
        self.addNode.triggered.connect (self.appendNode)
        self.addNode.setShortcutContext(Qt.ApplicationShortcut)

        self.exitMenu = self.menubar.addAction('E&xit')
        self.exitMenu.triggered.connect (self.exit)
        self.exitMenu.setShortcut("Ctrl+X")
        self.exitMenu.setShortcutContext(Qt.ApplicationShortcut)

        self.centralwidget = QWidget ()

        self.widgetbox = QVBoxLayout ()
        self.widgetbox.setContentsMargins (10, 10, 10, 10)
        self.widgetbox.setSpacing (10)

        self.tabs = QTabWidget ()
        self.tabs.setTabPosition (QTabWidget.North)
        self.tabs.setTabShape (QTabWidget.Rounded)

        for i in Sector.sectors ():
            self.tabs.insertTab (self.tabs.count (), MonitorTab (parent = self.tabs, sector = str(i), \
                                                                 controller = self.controller), str(i))

        self.widgetbox.addWidget (self.tabs)
        self.centralwidget.setLayout (self.widgetbox)

        self.setWindowTitle ("Controls Group's Single Board Computer Monitor")
        self.setCentralWidget (self.centralwidget)

        self.setGeometry (500, 500, MonitorInterface.WIDTH, MonitorInterface.HEIGHT)

    def appendType (self):
        typeDialog = TypeDialog (controller = self.controller)
        typeDialog.show ()

    def appendNode (self):
        nodeDialog = NodeDialog (controller = self.controller)
        nodeDialog.show ()

    def stopAll (self):
        self.controller.stop ()

    def closeEvent (self, evt):
        self.stopAll ()
        QMainWindow.closeEvent (self, evt)

    def exit (self):
        self.stopAll ()
        self.close ()