from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QPushButton, QTableView, \
    QVBoxLayout, QWidget
from common.entity.entities import NodeState
from client.qt.gui.controller import QtInterfaceController
from client.qt.gui.tableModel import MainTableModel
import threading
import time


class QtInterfaceTab(QWidget):

    UPDATE_TIME = 5

    def __init__(self, parent=None, sector="1", tab_index=0, update_icon=None):
        """
        Initializes a new tab representing a sector.
        :param parent: the component which created the object.
        :param sector: the sector that it represents.
        :param tab_index: index of this tab.
        :param update_icon: the signal to be updated when this component is in a warning state.
        """

        QWidget.__init__(self, parent)

        self.controller = QtInterfaceController.get_instance()

        self.sector = sector
        self.parent = parent
        self.tab_index = tab_index
        self.update_icon_signal = update_icon

        self.widget_box = QVBoxLayout()
        self.widget_box.setContentsMargins(10, 10, 10, 10)
        self.widget_box.setSpacing(10)

        self.staticTableTitle = QLabel("Preconfigured BBBs:")

        self.staticTable = QTableView(parent)
        self.staticTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.staticTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.staticTable.keyPressEvent = self.key_press_static_event
        self.staticTableModel = MainTableModel(self.staticTable)

        self.staticTable.setModel(self.staticTableModel)
        self.staticTable.verticalHeader().hide()

        self.staticTable.setMinimumHeight(400)
        self.staticTable.setMinimumWidth(200)

        self.dynamicTableTitle = QLabel("Unconfigured BBBs:")

        self.rebootButton = QPushButton("Reboot")
        self.rebootButton.pressed.connect(self.reboot_node)
        self.rebootButton.setEnabled(False)

        self.switchButton = QPushButton("Switch BBBs")
        self.switchButton.pressed.connect(self.switch_nodes)
        self.switchButton.setEnabled(False)

        self.dynamicTable = QTableView(parent)
        self.dynamicTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dynamicTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dynamicTable.keyPressEvent = self.key_press_dynamic_event
        self.dynamicTableModel = MainTableModel(self.dynamicTable)

        self.dynamicTable.setModel(self.dynamicTableModel)
        self.dynamicTable.verticalHeader().hide()

        self.staticTable.horizontalHeader().setStretchLastSection(True)
        self.staticTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.dynamicTable.horizontalHeader().setStretchLastSection(True)
        self.dynamicTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.staticTable.selectionChanged = self.registered_node_table_selection_changed
        self.dynamicTable.selectionChanged = self.dynamic_node_table_selection_changed

        self.dynamicTable.setMaximumHeight(400)
        self.dynamicTable.setMinimumWidth(200)

        self.dynamicHeader = QWidget()
        self.dynamicHeaderLayout = QHBoxLayout()
        self.dynamicHeaderLayout.addWidget(self.dynamicTableTitle)
        self.dynamicHeaderLayout.addWidget(QWidget())
        self.dynamicHeaderLayout.addWidget(self.rebootButton)
        self.dynamicHeaderLayout.addWidget(self.switchButton)
        self.dynamicHeader.setLayout(self.dynamicHeaderLayout)

        self.widget_box.addWidget(self.staticTableTitle)
        self.widget_box.addWidget(self.staticTable)
        self.widget_box.addWidget(self.dynamicHeader)
        self.widget_box.addWidget(self.dynamicTable)

        self.setLayout(self.widget_box)

        self.scanThread = threading.Thread(target=self.scan)
        self.scanning = True
        self.scanThread.start()

    def is_in_warning_state(self):
        """
        A tab is in 'warning state' if one of its registered nodes is not connected.
        :return: True if node is in a 'warning state'. False, otherwise.
        """

        for node in self.staticTableModel.nodes:
            if node.state != NodeState.CONNECTED:
                return True

        if len(self.dynamicTableModel.nodes) > 0:
            return True

        return False

    def switch_nodes(self):
        """
        Copies a configured from a not connected and registered node to a connected and registered node.
        """
        self.controller.switch(self.selected_node(self.staticTable), self.selected_node(self.dynamicTable))

    def reboot_node(self):
        """
        Reboots a connected node.
        """
        node = self.selected_node(self.staticTable)
        if node.state == NodeState.CONNECTED:
            self.controller.reboot(self.selected_node(self.staticTable))

    def selected_node(self, table):
        """
        :param table: the table to lookup the select the node.
        :return: The node that is selected or None if no nodes are selected.
        """
        rows = table.selectionModel().selectedRows()
        if len(rows) == 0:
            return None
        return table.model().nodes[rows[0].row()]

    def update_buttons(self):
        """
        Update buttons according to the tables selection state.
        """
        registered_node = self.selected_node(self.staticTable)
        dynamic_node = self.selected_node(self.dynamicTable)

        if registered_node is None or dynamic_node is None:
            self.switchButton.setEnabled(False)
            if registered_node is None or registered_node.state == NodeState.DISCONNECTED:
                self.rebootButton.setEnabled(False)
            else:
                self.rebootButton.setEnabled(True)
        else:

            if registered_node.state != NodeState.DISCONNECTED:
                self.rebootButton.setEnabled(True)
            else:
                self.rebootButton.setEnabled(False)

            if registered_node.ipAddress == dynamic_node.ipAddress:
                if registered_node.state == dynamic_node.state and registered_node.state == NodeState.MIS_CONFIGURED:
                    self.switchButton.setEnabled(True)
                else:
                    self.switchButton.setEnabled(False)

            elif registered_node.state == NodeState.DISCONNECTED and dynamic_node.state == NodeState.CONNECTED:
                self.switchButton.setEnabled(True)
            else:
                self.switchButton.setEnabled(False)

    def registered_node_table_selection_changed(self, selected, deselected):
        """
        Selection change event handler for the table of registered nodes. Updates the interface buttons accordingly.
        """
        self.update_buttons()
        QTableView.selectionChanged(self.staticTable, selected, deselected)

    def dynamic_node_table_selection_changed(self, selected, deselected):
        """
        Selection change event handler for the table of unregistered nodes. Updates the interface buttons accordingly.
        """
        self.update_buttons()
        QTableView.selectionChanged(self.dynamicTable, selected, deselected)

    def update_all(self):
        self.staticTableModel.setData(self.controller.get_nodes_from_sector(sector=self.sector, registered=True))
        self.dynamicTableModel.setData(self.controller.get_nodes_from_sector(sector=self.sector, registered=False))
        self.update_icon_signal.emit(self.tab_index)
        self.update_buttons()

    def scan(self):
        """
        Scans all nodes, registered and unregistered.
        """

        while self.scanning:
            self.update_all()
            time.sleep(QtInterfaceTab.UPDATE_TIME)

    def hideEvent(self, evt):
        pass

    def stop(self):
        """
        Stops all threads.
        """
        self.scanning = False

    def key_press_static_event(self, evt):
        """
        Clear table selection if the ESC key is pressed.
        :param evt: Event data.
        """
        if evt.key() == Qt.Key_Escape:
            self.staticTable.clearSelection()

        QTableView.keyPressEvent(self.staticTable, evt)

    def key_press_dynamic_event(self, evt):
        """
        Clear table selection if the ESC key is pressed.
        :param evt: Event data.
        """
        if evt.key() ==  Qt.Key_Escape:
            self.dynamicTable.clearSelection()

        QTableView.keyPressEvent(self.dynamicTable, evt)
