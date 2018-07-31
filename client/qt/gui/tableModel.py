from PyQt5.QtCore import pyqtSignal, QAbstractTableModel, Qt
from PyQt5.QtGui import QBrush, QColor

from common.entity.entities import NodeState, Node


class MainTableModel(QAbstractTableModel):
    """
    The table model which contains the data of each one the tab's tables.
    """
    # This signal is needed because Qt requires that methods dealing with graphic elements be called from the graphic
    # thread.
    updateModel = pyqtSignal()

    def update_data(self):
        """
        When the data changes, a signal is emitted in order to redraw the table widget.
        """
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()), [Qt.EditRole])
        self.layoutChanged.emit()

    def __init__(self, parent=None, data=[]):
        """
        Constructor method.
        :param parent: usually the object that created it.
        :param data: an optional list of Node objects.
        """
        QAbstractTableModel.__init__(self, parent)
        self.nodes = self.sort_by_address(data)
        self.updateModel.connect(self.update_data)

    def sort_by_address(self, data):
        """
        Sort table by IP address.
        :param data: a list of nodes to be sorted.
        :return: sorted list.
        """
        return sorted(data, key=lambda x: (x.state, x.ip_address), reverse=False)

    def setData(self, data):
        """
        Updates the table's content.
        :param data: a list of Node objects, representing the new table's content.
        """
        self.nodes = self.sort_by_address(data)
        self.updateModel.emit()

    def rowCount(self, *args, **kwargs):
        """
        Returns the data list's length.
        :param args: Not used.
        :param kwargs:  Not used.
        :return: the number of elements currently stored.
        """
        return len(self.nodes)

    def columnCount(self, *args, **kwargs):
        """
        Returns the number of columns of the table.
        :param args: Not used.
        :param kwargs: Not used.
        :return: the constant 4, representing a node's name, IP address, type name and current status.
        """
        return 4

    def data(self, index, role):
        """
        According to the role parameter, return the cell's background color or content.
        :param index: the cell's index.
        :param role: what kind of information is requested.
        :return: cell's color or content according to the role given as parameter.
        """
        row = index.row()
        col = index.column()
        node = self.nodes[row]

        if role == Qt.BackgroundRole:

            if node.state == NodeState.DISCONNECTED:
                return QBrush(QColor(229, 85, 94))

            if node.state == NodeState.MIS_CONFIGURED:
                if node.misconfiguredColor is None:
                    color = node.misconfiguredColor
                    return QBrush(QColor(color[0], color[1], color[2]))

                return QBrush(QColor(135, 206, 250))

            if node.state == NodeState.REBOOTING:
                return QBrush(QColor(255, 255, 130))

            return QBrush(QColor(92, 255, 130))

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter;

        if role == Qt.DisplayRole:

            if col == 0:
                return node.name
            if col == 1:
                return str(node.ip_address)
            if col == 2:
                return node.type.name

            return NodeState.to_string(node.state)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns a header cell's content.
        :param section: the cell's column index.
        :param orientation: if role is different than Qt.Horizontal this method returns None.
        :param role: if role is different than Qt.DisplayRole this method returns None.
        :return: a header cell's content.
        """

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


class TypeTableModel(QAbstractTableModel):
    """
    The table model which contains the data of the type management dialog's table.
    """
    # This signal is needed because Qt requires that methods dealing with graphic elements be called from the graphic
    # thread.
    updateModel = pyqtSignal()

    def update_data(self):
        """
        When the data changes, a signal is emitted in order to redraw the table widget.
        """
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))
        self.layoutChanged.emit()

    def __init__(self, parent=None, data=[]):
        """
        Constructor method.
        :param parent: usually the object that created it.
        :param data: an optional list of Type objects.
        """
        QAbstractTableModel.__init__(self, parent)
        self.types = data
        self.updateModel.connect(self.update_data)

    def setData(self, data):
        """
        Updates the table's content.
        :param data: a list of Type objects, representing the new table's content.
        """
        self.types = data
        self.updateModel.emit()

    def rowCount(self, *args, **kwargs):
        """
        Returns the data list's length.
        :param args: Not used.
        :param kwargs:  Not used.
        :return: the number of elements currently stored.
        """
        return len(self.types)

    def columnCount(self, *args, **kwargs):
        """
        Returns the number of columns of the table.
        :param args: Not used.
        :param kwargs: Not used.
        :return: the constant 4, representing the type's name, repository URL, rc.local script path inside the repo
         and description.
        """
        return 3

    def data(self, index, role):
        """
        According to the role parameter, return the cell's background color or content.
        :param index: the cell's index.
        :param role: what kind of information is requested.
        :return: cell's color or content according to the role given as parameter.
        """
        row = index.row()
        col = index.column()
        type_node = self.types[row]

        if role == Qt.BackgroundRole:
            return QBrush(QColor(type_node.color[0], type_node.color[1], type_node.color[2]))

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter

        if role == Qt.DisplayRole:
            if col == 0:
                return type_node.name
            elif col == 1:
                return type_node.repoUrl
            else:
                return type_node.description

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns a header cell's content.
        :param section: the cell's column index.
        :param orientation: if role is different than Qt.Horizontal this method returns None.
        :param role: if role is different than Qt.DisplayRole this method returns None.
        :return: a header cell's content.
        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            if section == 0:
                return "Name"
            elif section == 1:
                return "Repository Url"
            elif section == 2:
                return "rc.local Path"
            elif section == 3:
                return "Description"

        return None


class NodeTableModel(QAbstractTableModel):
    """
    The table model which contains the data of the node management dialog's table.
    """
    # This signal is needed because Qt requires that methods dealing with graphic elements be called from the graphic
    # thread.
    updateModel = pyqtSignal()

    def __init__(self, parent=None, data=None):
        """
        Constructor method.
        :param parent: usually the object that created it.
        :param data: an optional list of Node objects.
        """
        QAbstractTableModel.__init__(self, parent)
        self.nodes = self.sort_by_address(data)
        self.updateModel.connect(self.update_data)

    def update_data(self):
        """
        When the data changes, a signal is emitted in order to redraw the table widget.
        """
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))
        self.layoutChanged.emit()

    def sort_by_address(self, data):
        """
        Sort table by IP address.
        :param data: a list of nodes to be sorted.
        :return: sorted list.
        """
        return sorted(data, key=lambda x: x.ip_address, reverse=False)

    def setData(self, data):
        """
        Updates the table's content.
        :param data: a list of Type objects, representing the new table's content.
        """
        self.nodes = self.sort_by_address(data)
        self.updateModel.emit()

    def rowCount(self, *args, **kwargs):
        """
        Returns the data list's length.
        :param args: Not used.
        :param kwargs:  Not used.
        :return: the number of elements currently stored.
        """
        return len(self.nodes)

    def columnCount(self, *args, **kwargs):
        """
        Returns the number of columns of the table.
        :param args: Not used.
        :param kwargs: Not used.
        :return: the constant 4, representing a node's name, IP address, type name and PV prefixes.
        """
        return 4

    def data(self, index, role):
        """
        According to the role parameter, return the cell's background color or content.
        :param index: the cell's index.
        :param role: what kind of information is requested.
        :return: cell's color or content according to the role given as parameter.
        """

        row = index.row()
        col = index.column()
        node = self.nodes[row]

        if role == Qt.BackgroundRole:
            if node.type is not None:
                return QBrush(QColor(node.type.color[0], node.type.color[1], node.type.color[2]))
            else:
                return QBrush(QColor(255, 255, 255))

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter

        if role == Qt.DisplayRole:
            if col == 0:
                return node.name
            if col == 1:
                return str(node.ip_address)
            if col == 2:
                return node.type.name
            if col == 3:
                return Node.get_prefix_string(node.pvPrefix)

            return ""

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns a header cell's content.
        :param section: the cell's column index.
        :param orientation: if role is different than Qt.Horizontal this method returns None.
        :param role: if role is different than Qt.DisplayRole this method returns None.
        :return: a header cell's content.
        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            if section == 0:
                return "Id."
            if section == 1:
                return "IP"
            if section == 2:
                return "Type"
            if section == 3:
                return "Prefix"

        return None
