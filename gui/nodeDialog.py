from PyQt4.QtGui import QDialog, QLabel, QPushButton, QTableView, QAbstractItemView,\
                        QLineEdit, QTextEdit, QGridLayout, QVBoxLayout, QMessageBox, QColorDialog, QComboBox
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget

import entity.nodes
import gui.table
import threading
import time

class NodeDialog (QDialog):

    DIALOG_WIDTH = 900
    DIALOG_HEIGHT = 600

    def __init__ (self, parent = None, controller = None):

        super (NodeDialog, self).__init__ (parent)

        self.controller = controller

        self.input = QWidget ()
        self.inputLayout = QGridLayout ()

        self.idlabel = QLabel ("Identification:")
        self.idtext = QLineEdit ()

        self.addrlabel = QLabel ("IP address:")
        self.addrtext = QLineEdit ()
        # self.addrtext.setInputMask ("000.000.000.000;_")

        self.typeslabel = QLabel ("Registered types:")
        self.types = QComboBox ()
        self.updateTypes ()

        self.sectorlabel = QLabel ("Supersector:")
        self.sectors = QComboBox ()
        self.sectors.addItems ([str (i) for i in range(1,21)] + ["LINAC", "RF", "Conectividade"])

        self.submit = QPushButton ("+")
        self.submit.pressed.connect (self.appendNode)

        self.inputLayout.addWidget (self.idlabel, 0, 0, 1, 1)
        self.inputLayout.addWidget (self.idtext, 0, 2, 1, 2)

        self.inputLayout.addWidget (self.addrlabel, 1, 0, 1, 1)
        self.inputLayout.addWidget (self.addrtext, 1, 2, 1, 2)

        self.inputLayout.addWidget (self.typeslabel, 2, 0, 1, 2)
        self.inputLayout.addWidget (self.types, 2, 2, 1, 2)

        self.inputLayout.addWidget (self.sectorlabel, 3, 0, 1, 2)
        self.inputLayout.addWidget (self.sectors, 3, 2, 1, 2)

        self.inputLayout.addWidget (self.submit, 4, 3, 1, 1)

        self.outerLayout = QVBoxLayout ()
        self.outerLayout.setContentsMargins (10, 10, 10, 10)
        self.outerLayout.setSpacing (10)

        self.nodeTable = QTableView (parent)
        self.nodeTable.resizeRowsToContents ();
        self.nodeTable.setSelectionBehavior (QAbstractItemView.SelectRows)
        self.nodeTable.setSelectionMode (QAbstractItemView.SingleSelection)
        self.nodeTable.keyPressEvent = self.keyPressEvent

        self.nodeTableModel = gui.table.NodeTableModel (self.nodeTable, data = self.controller.fetchNodesFromSector (sector = self.sectors.itemText (0)))
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

        self.scanning = True

    def updateTypes (self):

        types = self.controller.fetchTypes ()

        items = []

        for t in types:
            items.append(t ["name"])

        self.types.clear ()
        self.types.addItems (items)

    def sectorChangeEvent (self, index):
        nodes = self.controller.fetchNodesFromSector (sector = self.sectors.itemText (index))
        self.nodeTableModel.setData (nodes)

    def resizeEvent (self, args):

        self.nodeTable.setColumnWidth(0, self.nodeTable.size ().width () / 3 - 5);
        self.nodeTable.setColumnWidth(1, self.nodeTable.size ().width () / 3);
        self.nodeTable.setColumnWidth(2, self.nodeTable.size ().width () / 3);

        QDialog.resizeEvent (self, args)

    def appendNode (self) :

        types = self.controller.typeList ()
        t_dict = {}

        for i, t in enumerate (types):
            if t ["name"] == self.types.itemText (self.types.currentIndex ()):
                    break

        newNode = entity.nodes.Node (name = self.idtext.displayText(), ip = self.addrtext.displayText(), \
                                     typeNode = self.controller.typeList () [i], \
                                     sector = self.sectors.itemText (self.sectors.currentIndex ()))

        self.controller.appendNode (newNode)

        nodes = self.controller.fetchNodesFromSector (sector = self.sectors.itemText (self.sectors.currentIndex ()))
        self.nodeTableModel.setData (nodes)

    def keyPressEvent (self, evt):

        # Del
        if evt.key () == 16777223 and len(self.nodeTable.selectedIndexes ()) > 0:

            selectedRow = self.nodeTable.selectedIndexes ()[0].row ()

            removeNode = entity.nodes.Node (name = self.nodeTableModel.data [selectedRow].name, \
                                            ip = self.nodeTableModel.data [selectedRow].ipAddress, \
                                            typeNode = self.nodeTableModel.data [selectedRow].type, \
                                            sector = self.nodeTableModel.data [selectedRow].sector)

            self.controller.removeNodeFromSector (removeNode)
            nodes = self.controller.fetchNodesFromSector (sector = self.sectors.itemText (self.sectors.currentIndex ()))
            self.nodeTableModel.setData (nodes)
            self.nodeTable.clearSelection ()

        QTableView.keyPressEvent (self.nodeTable, evt)
