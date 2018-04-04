from PyQt4.QtGui import QAbstractItemView, QLabel, QTableView, QVBoxLayout
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget, QLineEdit, QColor, QBrush

import gui.tableModel
import threading

class MonitorTab (QWidget):

    def __init__(self, parent = None, sector = "1"):

        QWidget.__init__ (self, parent)

        self.sector = sector

        self.widgetbox = QVBoxLayout ()
        self.widgetbox.setContentsMargins (10, 10, 10, 10)
        self.widgetbox.setSpacing (10)

        self.staticTableTitle = QLabel ("Preconfigured BBBs:")

        self.staticTable = QTableView (parent)
        self.staticTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.staticTable.setSelectionMode (QAbstractItemView.SingleSelection);

        self.staticTableModel = gui.tableModel.MonitorTableModel (self.staticTable)

        self.staticTable.setModel (self.staticTableModel)
        self.staticTable.verticalHeader ().hide ()

        self.staticTable.setMinimumHeight (400)
        self.staticTable.setMinimumWidth (200)

        self.dynamicTableTitle = QLabel ("Unconfigured BBBs:")

        self.dynamicTable = QTableView (parent)
        self.dynamicTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.dynamicTable.setSelectionMode (QAbstractItemView.SingleSelection);

        self.dynamicTableModel = gui.tableModel.MonitorTableModel (self.dynamicTable)

        self.dynamicTable.setModel (self.dynamicTableModel)
        self.dynamicTable.verticalHeader ().hide ()

        self.dynamicTable.setMaximumHeight (200)
        self.dynamicTable.setMinimumWidth (200)

        self.widgetbox.addWidget (self.staticTableTitle)
        self.widgetbox.addWidget (self.staticTable)
        self.widgetbox.addWidget (self.dynamicTableTitle)
        self.widgetbox.addWidget (self.dynamicTable)

        self.setLayout (self.widgetbox)

        self.scan = threading.Thread (target = "")

    def showEvent (self, evt):
        print ("oi " + self.sector)

    def hideEvent (self, evt):
        print ("tchau " + self.sector)
