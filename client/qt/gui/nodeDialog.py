from common.entity.entities import Command, Node, NodeState, Sector, Type
from gui.tableModel import NodeTableModel

from PyQt4.QtGui import QDialog, QLabel, QPushButton, QTableView, QAbstractItemView,\
                        QLineEdit, QTextEdit, QGridLayout, QVBoxLayout, QMessageBox, QColorDialog, QComboBox
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget

import threading
import time

class NodeDialog (QDialog):

    DIALOG_WIDTH = 1200
    DIALOG_HEIGHT = 600

    UPDATE_TIME = 5

    def __init__ (self, parent = None, controller = None):

        super (NodeDialog, self).__init__ (parent)

        self.controller = controller

        self.input = QWidget ()
        self.inputLayout = QGridLayout ()

        self.idlabel = QLabel ("Identification:")
        self.idtext = QLineEdit ()

        self.addrlabel = QLabel ("IP Address:")
        self.addrtext = QLineEdit ()
        # self.addrtext.setInputMask ("000.000.000.000;_")

        self.typeslabel = QLabel ("Registered types:")
        self.types = QComboBox ()
        self.updateTypes ()

        self.sectorlabel = QLabel ("Supersector:")
        self.sectors = QComboBox ()
        self.sectors.addItems (Sector.sectors ())

        self.submit = QPushButton ("+")
        self.submit.pressed.connect (self.appendNode)

        self.prefixLabel = QLabel ("PV Prefix:")
        self.prefix = QLineEdit ()

        self.inputLayout.addWidget (self.idlabel, 0, 0, 1, 1)
        self.inputLayout.addWidget (self.idtext, 0, 1, 1, 1)
        self.inputLayout.addWidget (self.typeslabel, 0, 2, 1, 1)
        self.inputLayout.addWidget (self.types, 0, 3, 1, 1)

        self.inputLayout.addWidget (self.addrlabel, 1, 0, 1, 1)
        self.inputLayout.addWidget (self.addrtext, 1, 1, 1, 1)

        self.inputLayout.addWidget (self.sectorlabel, 1, 2, 1, 1)
        self.inputLayout.addWidget (self.sectors, 1, 3, 1, 1)

        self.inputLayout.addWidget (self.prefixLabel, 2, 0, 1, 1)
        self.inputLayout.addWidget (self.prefix, 2, 1, 1, 1)
        self.inputLayout.addWidget (self.submit, 2, 3, 1, 1)

        self.outerLayout = QVBoxLayout ()
        self.outerLayout.setContentsMargins (10, 10, 10, 10)
        self.outerLayout.setSpacing (10)

        self.nodeTable = QTableView (parent)
        self.nodeTable.resizeRowsToContents ();
        self.nodeTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.nodeTable.setSelectionMode (QAbstractItemView.SingleSelection)
        self.nodeTable.keyPressEvent = self.keyPressEvent
        self.nodeTable.selectionChanged = self.selectionChanged

        self.nodeTableModel = NodeTableModel (self.nodeTable, data = self.controller.getNodesFromSector (sector = self.sectors.itemText (0), registered = True))
        self.nodeTable.setModel (self.nodeTableModel)

        self.nodeTable.setMinimumHeight (800)
        self.nodeTable.setMinimumWidth (500)

        self.labelTable = QLabel ("Available nodes in sector: (press [DEL] to remove)")

        self.sectors.currentIndexChanged.connect (self.sectorChangeEvent)
        self.input.setLayout (self.inputLayout)

        self.outerLayout.addWidget (self.input)
        self.outerLayout.addWidget (self.labelTable)
        self.outerLayout.addWidget (self.nodeTable)

        self.setLayout (self.outerLayout)

        self.setGeometry (500, 500, NodeDialog.DIALOG_WIDTH, NodeDialog.DIALOG_HEIGHT)

        self.setWindowTitle ("BBB Hosts Management")

        self.scanThread = threading.Thread (target = self.scan)

        self.scanning = True
        self.scanThread.start ()

    def scan (self):

        while self.scanning:

            self.nodeTableModel.setData (self.controller.getNodesFromSector (sector = self.sectors.itemText (self.sectors.currentIndex ()), registered = True))
            self.updateTypes ()
            time.sleep (NodeDialog.UPDATE_TIME)

    def updateTypes (self):

        types = self.controller.fetchTypes ()

        items = [self.types.itemText(i) for i in range (self.types.count())]

        for t in types:
            if t.name not in items:
                self.types.addItem (t.name, t)

        for index, item in enumerate (items):
            remove = True
            for t in types:
                if t.name == item:
                    remove = False
                    break
            if remove:
                self.types.removeItem (index)

    def sectorChangeEvent (self, index):
        self.nodeTableModel.setData (self.controller.getNodesFromSector (sector = self.sectors.itemText (index), registered = True))

    def resizeEvent (self, args):

        for i in range (self.nodeTableModel.columnCount ()):
            self.nodeTable.setColumnWidth(i, self.nodeTable.size ().width () / self.nodeTableModel.columnCount () - 1);

        QDialog.resizeEvent (self, args)

    def appendNode (self) :

        newNode = Node (name = self.idtext.displayText(), ip = self.addrtext.displayText(), \
                        typeNode = self.types.itemData (self.types.currentIndex ()), \
                        sector = self.sectors.itemText (self.sectors.currentIndex ()), \
                        pvPrefix = self.prefix.displayText())

        appended = self.controller.appendNode (newNode)

        if appended:
            nodes = self.controller.getNodesFromSector (sector = self.sectors.itemText (self.sectors.currentIndex ()), registered = True)
            self.nodeTableModel.setData (nodes)
        else:
            QMessageBox (QMessageBox.Warning, "Failed!", "IP address already in use!", QMessageBox.Ok, self).open ()

    def keyPressEvent (self, evt):

        # Del
        if evt.key () == 16777223 and len(self.nodeTable.selectedIndexes ()) > 0:

            selectedRow = self.nodeTable.selectedIndexes ()[0].row ()

            removeNode = Node (name = self.nodeTableModel.nodes [selectedRow].name, \
                               ip = self.nodeTableModel.nodes [selectedRow].ipAddress, \
                               typeNode = self.nodeTableModel.nodes [selectedRow].type, \
                               sector = self.nodeTableModel.nodes [selectedRow].sector, \
                               pvPrefix = self.nodeTableModel.nodes [selectedRow].pvPrefix)

            self.controller.removeNodeFromSector (removeNode)
            nodes = self.controller.getNodesFromSector (sector = self.sectors.itemText (self.sectors.currentIndex ()), registered = True)
            self.nodeTableModel.setData (nodes)
            self.nodeTable.clearSelection ()

        elif evt.key () == 16777216:

            self.idtext.clear ()
            self.addrtext.clear ()
            self.nodeTable.clearSelection ()

        QTableView.keyPressEvent (self.nodeTable, evt)

    def selectionChanged (self, selected, deselected):

        if len(selected.indexes ()) > 0:
            selectedRow = selected.indexes ()[0].row ()
            nodeObject = self.nodeTableModel.nodes [selectedRow]

            self.idtext.setText (nodeObject.name)
            self.addrtext.setText (nodeObject.ipAddress)
            self.prefix.setText (nodeObject.pvPrefix)

            items = [self.types.itemText(i) for i in range (self.types.count())]
            for index, item in enumerate (items):
                if nodeObject.type.name == item:
                    self.types.setCurrentIndex (index)

        QTableView.selectionChanged (self.nodeTable, selected, deselected)

    def closeEvent (self, args):

        self.scanning = False
        QDialog.closeEvent (self, args)
