from common.entity.entities import Command, Node, NodeState, Type
from PyQt4.QtGui import QTableView, QAbstractItemView
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget, QLineEdit, QColor, QBrush

class MonitorTableModel (QAbstractTableModel):

    def __init__ (self, parent = None, data = []):
        self.nodes = self.sortByAddress(data)
        QAbstractTableModel.__init__(self, parent)

    def sortByAddress (self, data):
        return sorted(data, key = lambda x: (x.state, x.ipAddress), reverse = False)

    def setData (self, data):
        self.nodes = self.sortByAddress(data)
        self.dataChanged.emit (self.index (0, 0), self.index (self.rowCount (), self.columnCount ()))
        self.layoutChanged.emit ()

    def rowCount(self, *args, **kwargs):
        return len (self.nodes)

    def columnCount(self, *args, **kwargs):
        return 4

    def data(self, index, role):

        row = index.row ()
        col = index.column ()
        node = self.nodes [row]

        if role == Qt.BackgroundRole :

            if node.state == NodeState.DISCONNECTED:
                return QBrush (QColor (229, 85, 94))

            if node.state == NodeState.MISCONFIGURED:
                if node.misconfiguredColor != None:
                    color = node.misconfiguredColor
                    return QBrush (QColor (color [0], color [1], color [2]))

                return QBrush (QColor (135, 206, 250))

            return QBrush (QColor (92, 255, 130))

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter;

        if role == Qt.DisplayRole:

            if col == 0:
                return node.name
            if col == 1:
                return node.ipAddress
            if col == 2:
                return node.type.name

            return NodeState.toString (node.state)

        return None

    def headerData(self, section, orientation, role = Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            if section == 0:
                return "Name"
            elif section == 1:
                return "IP Address"
            elif section == 2:
                return "Type"
            else:
                return "Current status"

        return None

class TypeTableModel (QAbstractTableModel):

    def __init__ (self, parent = None, data = None):

        QAbstractTableModel.__init__(self, parent)
        self.types = data

    def setData (self, data):
        self.types = data
        self.dataChanged.emit (self.index (0, 0), self.index (self.rowCount (), self.columnCount ()))
        self.layoutChanged.emit ()

    def rowCount (self, *args, **kwargs):
        return len (self.types)

    def columnCount (self, *args, **kwargs):
        return 2

    def data (self, index, role):

        row = index.row ()
        col = index.column ()
        typeNode = self.types [row]

        if role == Qt.BackgroundRole:
            return QBrush (QColor (typeNode.color [0], typeNode.color [1], typeNode.color [2]))

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter;

        if role == Qt.DisplayRole:
            if col == 0:
                return typeNode.name

            return typeNode.description

        return None

    def headerData (self, section, orientation, role = Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            if section == 0:
                return "Name"
            elif section == 1:
                return "Description"

        return None

class NodeTableModel (QAbstractTableModel):

    def __init__ (self, parent = None, data = None):

        QAbstractTableModel.__init__(self, parent)
        self.nodes = self.sortByAddress (data)

    def sortByAddress (self, data):
        return sorted(data, key = lambda x: x.ipAddress, reverse = False)

    def setData (self, data):
        self.nodes = self.sortByAddress (data)
        self.dataChanged.emit (self.index (0, 0), self.index (self.rowCount (), self.columnCount ()))
        self.layoutChanged.emit ()

    def rowCount (self, *args, **kwargs):
        return len (self.nodes)

    def columnCount (self, *args, **kwargs):
        return 3

    def data (self, index, role):

        row = index.row()
        col = index.column()
        node = self.nodes [row]

        if role == Qt.BackgroundRole:
            return QBrush (QColor (node.type.color [0], node.type.color [1], node.type.color [2]))

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter;

        if role == Qt.DisplayRole:
            if col == 0:
                return node.name
            if col == 1:
                return node.ipAddress

            return node.type.name

        return None

    def headerData (self, section, orientation, role = Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            if section == 0:
                return "Id."
            if section == 1:
                return "IP"
            if section == 2:
                return "Type"

        return None