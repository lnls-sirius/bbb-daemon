from PyQt4.QtGui import QTableView, QAbstractItemView
from PyQt4.QtCore import *
from PyQt4.Qt import QWidget, QLineEdit, QColor, QBrush

class MonitorTableModel (QAbstractTableModel):

    def __init__ (self, parent = None, node_list = ["2", "3"]):

        self._data = node_list

        QAbstractTableModel.__init__(self, parent)

    def rowCount(self, *args, **kwargs):
        return len(self._data)

    def columnCount(self, *args, **kwargs):
        return 2

    def data(self, index, role):

        __row = index.row()
        __col = index.column()
        __node = self._data[__row]

        if role == Qt.BackgroundRole :

            #if __node.state == Control_Node_State.DISCONNECTED:
            #    return QBrush(QColor(229, 85, 94))

            #if __node.state == Control_Node_State.CONNECTED:
            #    return QBrush(QColor(92, 255, 130))

            return QBrush(QColor(255, 255, 0))


        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter;

        if role == Qt.DisplayRole:

            if __col == 0:
                return "Teste"

            return "Tedte"

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "SBC"

            elif section == 1:
                return "Status"

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
        return len(self.types)

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
