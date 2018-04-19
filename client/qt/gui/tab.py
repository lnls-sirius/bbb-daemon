from PyQt4.QtGui import QAbstractItemView, QLabel, QTableView, QVBoxLayout
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget, QLineEdit, QColor, QBrush

import gui.tableModel
import threading
import time

class MonitorTab (QWidget):

    def __init__(self, parent = None, sector = "1", controller = None):

        QWidget.__init__ (self, parent)

        self.sector = sector
        self.controller = controller

        self.widgetbox = QVBoxLayout ()
        self.widgetbox.setContentsMargins (10, 10, 10, 10)
        self.widgetbox.setSpacing (10)

        self.staticTableTitle = QLabel ("Preconfigured BBBs:")

        self.staticTable = QTableView (parent)
        self.staticTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.staticTable.setSelectionMode (QAbstractItemView.SingleSelection);
        self.staticTable.keyPressEvent = self.keyPressStaticEvent
        self.staticTableModel = gui.tableModel.MonitorTableModel (self.staticTable)

        self.staticTable.setModel (self.staticTableModel)
        self.staticTable.verticalHeader ().hide ()

        self.staticTable.setMinimumHeight (400)
        self.staticTable.setMinimumWidth (200)

        self.dynamicTableTitle = QLabel ("Unconfigured BBBs:")

        self.dynamicTable = QTableView (parent)
        self.dynamicTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.dynamicTable.setSelectionMode (QAbstractItemView.SingleSelection);
        self.dynamicTable.keyPressEvent = self.keyPressDynamicEvent
        self.dynamicTableModel = gui.tableModel.MonitorTableModel (self.dynamicTable)

        self.dynamicTable.setModel (self.dynamicTableModel)
        self.dynamicTable.verticalHeader ().hide ()

        self.dynamicTable.setMaximumHeight (400)
        self.dynamicTable.setMinimumWidth (200)

        self.widgetbox.addWidget (self.staticTableTitle)
        self.widgetbox.addWidget (self.staticTable)
        self.widgetbox.addWidget (self.dynamicTableTitle)
        self.widgetbox.addWidget (self.dynamicTable)

        self.setLayout (self.widgetbox)

    def scan (self):

        while self.scanning:
            self.staticTableModel.setData (self.controller.getNodesFromSector (sector = self.sector, registered = True))
            self.dynamicTableModel.setData (self.controller.getNodesFromSector (sector = self.sector, registered = False))
            time.sleep (1)

    def showEvent (self, evt):

        self.scanThread = threading.Thread (target = self.scan)
        self.scanning = True
        self.scanThread.start ()

    def hideEvent (self, evt):
        self.scanning = False

    def resizeEvent (self, args):

        self.staticTable.setColumnWidth(0, self.staticTable.size ().width () / 4 - 5);
        self.staticTable.setColumnWidth(1, self.staticTable.size ().width () / 4);
        self.staticTable.setColumnWidth(2, self.staticTable.size ().width () / 4);
        self.staticTable.setColumnWidth(3, self.staticTable.size ().width () / 4);

        self.dynamicTable.setColumnWidth(0, self.staticTable.size ().width () / 4 - 5);
        self.dynamicTable.setColumnWidth(1, self.staticTable.size ().width () / 4);
        self.dynamicTable.setColumnWidth(2, self.staticTable.size ().width () / 4);
        self.dynamicTable.setColumnWidth(3, self.staticTable.size ().width () / 4);

        QWidget.resizeEvent (self, args)

    def keyPressStaticEvent (self, evt):

        if evt.key () == 16777216:

            self.staticTable.clearSelection ()

        QTableView.keyPressEvent (self.staticTable, evt)

    def keyPressDynamicEvent (self, evt):

        if evt.key () == 16777216:

            self.dynamicTable.clearSelection ()

        QTableView.keyPressEvent (self.dynamicTable, evt)
