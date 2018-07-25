from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QColorDialog, QComboBox, QDesktopWidget, QDialog, QFormLayout, \
    QHeaderView, QGridLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton, QTableView, QTextEdit, \
    QVBoxLayout, QWidget
from common.entity.entities import Node, Type, Sector
from client.qt.gui.controller import QtInterfaceController
from client.qt.gui.tableModel import NodeTableModel, TypeTableModel
import threading
import time


class QtDialog(QDialog):
    """
    A base class for dialogs. Inherits from QDialog.
    """
    def __init__(self, parent=None):
        super(QtDialog, self).__init__(parent)

    def center(self):
        """
        Centers the dialog.
        """
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())


class QtTypeDialog(QtDialog):
    """
    Dialogs that allows managing type instances.
    """
    DIALOG_WIDTH = 800
    DIALOG_HEIGHT = 600

    UPDATE_TIME = 5

    def __init__(self, parent=None):
        """
        Draws a new dialog to manage types.
        :param parent: the widget that launched the dialog.
        """

        super(QtTypeDialog, self).__init__(parent)

        self.controller = QtInterfaceController.get_instance()

        self.input = QWidget()

        self.input_layout = QFormLayout()
        self.input_layout.setContentsMargins(0, 0, 0, 0)

        self.input.setLayout(self.input_layout)

        self.name_label = QLabel("Name:")
        self.name = QLineEdit()

        self.descriptionLabel = QLabel("Description:")
        self.description = QTextEdit()
        self.description.setMinimumHeight(85)

        self.repoUrlLabel = QLabel("Repository URL:")
        self.repoUrl = QLineEdit()

        self.rcLocalPathLabel = QLabel("rc.local Relative Path:")
        self.rcLocalPath = QLineEdit()

        self.buttons = QWidget()
        self.buttonsLayout = QGridLayout()
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.setSpacing(10)

        self.colorButton = QPushButton("Choose color")
        self.colorButton.setAutoFillBackground(True)
        self.colorButton.pressed.connect(self.select_color)

        self.submit = QPushButton("+")
        self.submit.pressed.connect(self.append_type)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(200, 80, 250, 20)

        self.checkUrl = QPushButton("Check Git URL")
        self.checkUrl.pressed.connect(self.check_url_action)

        self.buttonsLayout.addWidget(QWidget(), 0, 0, 1, 5)
        self.buttonsLayout.addWidget(self.colorButton, 0, 5, 1, 1)
        self.buttonsLayout.addWidget(self.submit, 0, 6, 1, 1)
        self.buttonsLayout.addWidget(self.checkUrl, 0, 7, 1, 1)
        self.buttonsLayout.addWidget(self.progressBar, 0, 8, 1, 1)

        self.buttons.setLayout(self.buttonsLayout)

        self.outerLayout = QVBoxLayout()
        self.outerLayout.setContentsMargins(10, 10, 10, 10)
        self.outerLayout.setSpacing(10)

        self.typeTable = QTableView(parent)
        self.typeTable.selectionChanged = self.selection_changed
        self.typeTable.keyPressEvent = self.keyPressEvent
        self.typeTable.resizeRowsToContents()
        self.typeTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.typeTable.setSelectionMode(QAbstractItemView.SingleSelection)

        self.typeTableModel = TypeTableModel(self.typeTable, data=self.controller.fetch_types())
        self.typeTable.setModel(self.typeTableModel)

        self.typeTable.horizontalHeader().setStretchLastSection(True)
        self.typeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.labelTable = QLabel("Available types: (press [DEL] to remove)")

        self.input_layout.addWidget(self.name_label)
        self.input_layout.addWidget(self.name)
        self.input_layout.addWidget(self.repoUrlLabel)
        self.input_layout.addWidget(self.repoUrl)
        self.input_layout.addWidget(self.rcLocalPathLabel)
        self.input_layout.addWidget(self.rcLocalPath)
        self.input_layout.addWidget(self.descriptionLabel)
        self.input_layout.addWidget(self.description)

        self.outerLayout.addWidget(self.input)
        self.outerLayout.addWidget(self.buttons)
        self.outerLayout.addWidget(self.labelTable)
        self.outerLayout.addWidget(self.typeTable)

        self.setLayout(self.outerLayout)

        self.setGeometry(500, 500, QtTypeDialog.DIALOG_WIDTH, QtTypeDialog.DIALOG_HEIGHT)

        self.setWindowTitle("Types Management")

        self.color_dialog = QColorDialog(QColor(255, 255, 0), self)

        self.scanThread = threading.Thread(target=self.scan)
        self.scanning = True
        self.scanThread.start()

    def keyPressEvent(self, evt):
        """
        Process a key event in the dialog. Two keys are allowed: DEL and ESC. DEL removes the selected element and
        ESC clears all the input widgets.
        :param evt: event data
        """

        if evt.key() == Qt.Key_Delete and len(self.typeTable.selectedIndexes()) > 0:

            selected_row = self.typeTable.selectedIndexes()[0].row()
            type_name = self.typeTableModel.data(self.typeTableModel.index(selected_row, 0), Qt.DisplayRole)

            self.controller.remove_type_by_name(type_name)
            self.typeTableModel.setData(self.controller.fetch_types())
            self.typeTable.clearSelection()

        elif evt.key() == Qt.Key_Escape:

            self.name.clear()
            self.description.clear()
            self.repoUrl.clear()
            self.rcLocalPath.clear()
            self.typeTable.clearSelection()
            self.color_dialog.setCurrentColor(QColor(255, 255, 0))

        QTableView.keyPressEvent(self.typeTable, evt)

    def selection_changed(self, selected, deselected):
        """
        Updates the input widgets according to the selected type.
        :param selected: the selected item.
        :param deselected: the item that was de-selected.
        """

        if len(selected.indexes()) > 0:
            selected_row = selected.indexes()[0].row()
            host_type = self.typeTableModel.types[selected_row]

            # Updates input widgets
            self.name.setText(host_type.name)
            self.repoUrl.setText(host_type.repoUrl)
            self.rcLocalPath.setText(host_type.rcLocalPath)
            self.description.setPlainText(host_type.description)
            self.color_dialog.setCurrentColor(QColor(host_type.color[0], host_type.color[1], host_type.color[2]))

        QTableView.selectionChanged(self.typeTable, selected, deselected)

    def check_url_action(self):
        """
        @todo: how does this work?
        success, message = checkUrlFunc()
        if success:
            QMessageBox.about(self, "Success!", message)
        else:
            QMessageBox.about(self, "Failure!", message)
        """
        pass

    def select_color(self):
        """
        Opens a color dialog allowing the user to choose a different color to represent the type.
        """
        self.color_dialog.open()

    def append_type(self):
        """
        Appends a new type. This method is call every time that the Append button is pushed.
        """
        selected_color = self.color_dialog.currentColor()

        new_type = Type(name=self.name.displayText().strip(),
                        description=self.description.toPlainText().strip(),
                        repo_url=self.repoUrl.displayText().strip(),
                        rcLocalPath=self.rcLocalPath.displayText().strip(),
                        color=(selected_color.red(), selected_color.green(), selected_color.blue()))

        self.controller.manage_types(new_type)

        self.typeTableModel.setData(self.controller.fetch_types())
        self.typeTable.clearSelection()

    def scan(self):
        """
        Keeps requesting the registered types saved in the database.
        """
        while self.scanning:
            self.typeTableModel.setData(self.controller.fetch_types())
            time.sleep(QtTypeDialog.UPDATE_TIME)

    def closeEvent(self, args):
        """
        Closes and shuts the scanning thread down.
        """
        self.scanning = False
        QDialog.closeEvent(self, args)


class NodeDialog(QtDialog):
    """
    Dialogs that allows managing node instances.
    """
    DIALOG_WIDTH = 1200
    DIALOG_HEIGHT = 600

    # in seconds
    UPDATE_TIME = 5

    def __init__(self, parent=None):
        """
        Draws a new dialog to manage nodes.
        :param parent: the widget that launched the dialog.
        """

        super(NodeDialog, self).__init__(parent)

        self.controller = QtInterfaceController.get_instance()

        self.input = QWidget()
        self.inputLayout = QGridLayout()

        self.id_label = QLabel("Identification:")
        self.id_text = QLineEdit()

        self.address_label = QLabel("IP Address:")
        self.address_text = QLineEdit()
        # self.address_text.setInputMask ("000.000.000.000;_")

        self.types_label = QLabel("Registered types:")
        self.types = QComboBox()
        self.update_types()

        self.sector_label = QLabel("Supersector:")
        self.sectors = QComboBox()
        self.sectors.addItems(Sector.sectors())

        self.submit = QPushButton("+")
        self.submit.pressed.connect(self.append_node)

        self.prefixLabel = QLabel("PV Prefix:")
        self.prefix = QLineEdit()

        self.inputLayout.addWidget(self.id_label, 0, 0, 1, 1)
        self.inputLayout.addWidget(self.id_text, 0, 1, 1, 1)
        self.inputLayout.addWidget(self.types_label, 0, 2, 1, 1)
        self.inputLayout.addWidget(self.types, 0, 3, 1, 1)

        self.inputLayout.addWidget(self.address_label, 1, 0, 1, 1)
        self.inputLayout.addWidget(self.address_text, 1, 1, 1, 1)

        self.inputLayout.addWidget(self.sector_label, 1, 2, 1, 1)
        self.inputLayout.addWidget(self.sectors, 1, 3, 1, 1)

        self.inputLayout.addWidget(self.prefixLabel, 2, 0, 1, 1)
        self.inputLayout.addWidget(self.prefix, 2, 1, 1, 1)
        self.inputLayout.addWidget(self.submit, 2, 3, 1, 1)

        self.outerLayout = QVBoxLayout()
        self.outerLayout.setContentsMargins(10, 10, 10, 10)
        self.outerLayout.setSpacing(10)

        self.nodeTable = QTableView(parent)
        self.nodeTable.resizeRowsToContents()
        self.nodeTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.nodeTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.nodeTable.keyPressEvent = self.keyPressEvent
        self.nodeTable.selectionChanged = self.selection_changed

        self.nodeTableModel = NodeTableModel(self.nodeTable,
                                             data=self.controller.get_nodes_from_sector(sector=self.sectors.itemText(0),
                                                                                        registered=True))
        self.nodeTable.setModel(self.nodeTableModel)

        self.nodeTable.horizontalHeader().setStretchLastSection(True)
        self.nodeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # self.nodeTable.setMinimumHeight(800)
        # self.nodeTable.setMinimumWidth(500)

        self.labelTable = QLabel("Available nodes in sector: (press [DEL] to remove)")

        self.sectors.currentIndexChanged.connect(self.sector_change_event)
        self.input.setLayout(self.inputLayout)

        self.outerLayout.addWidget(self.input)
        self.outerLayout.addWidget(self.labelTable)
        self.outerLayout.addWidget(self.nodeTable)

        self.setLayout(self.outerLayout)

        self.setGeometry(500, 500, NodeDialog.DIALOG_WIDTH, NodeDialog.DIALOG_HEIGHT)

        self.setWindowTitle("BBB Hosts Management")

        self.scanThread = threading.Thread(target=self.scan)

        self.scanning = True
        self.scanThread.start()

    def scan(self):
        """
        Continuously scans for nodes and types.
        """

        while self.scanning:
            self.nodeTableModel.setData(
                self.controller.get_nodes_from_sector(sector=self.sectors.itemText(self.sectors.currentIndex()),
                                                      registered=True))
            self.update_types()
            time.sleep(NodeDialog.UPDATE_TIME)

    def update_types(self):
        """
        Updates the types combo box with a new list of types.
        """

        types = self.controller.fetch_types()

        items = [self.types.itemText(i) for i in range(self.types.count())]

        for t in types:
            if t.name not in items:
                self.types.addItem(t.name, t)

        for index, item in enumerate(items):
            remove = True
            for t in types:
                if t.name == item:
                    remove = False
                    break
            if remove:
                self.types.removeItem(index)

    def sector_change_event(self, index):
        """
        Method called when a new sector is chosen in the combo box.
        :param index: the index of the new sector.
        """
        self.nodeTableModel.setData(
            self.controller.get_nodes_from_sector(sector=self.sectors.itemText(index), registered=True))

    def append_node(self):
        """
        Append a new node to the database. Method called when the button is pressed.
        """

        new_node = Node(name=self.id_text.displayText(), ip=self.address_text.displayText(),
                       type_node=self.types.itemData(self.types.currentIndex()),
                       sector=self.sectors.itemText(self.sectors.currentIndex()),
                       pv_prefixes=Node.get_prefix_array(self.prefix.displayText()))

        appended = self.controller.manage_nodes(new_node)

        if appended:
            nodes = self.controller.get_nodes_from_sector(sector=self.sectors.itemText(self.sectors.currentIndex()),
                                                          registered=True)
            self.nodeTableModel.setData(nodes)
        else:
            QMessageBox(QMessageBox.Warning, "Failed!", "Could not add a new node. Verify if the IP address!",
                        QMessageBox.Ok, self).open()

    def keyPressEvent(self, evt):
        """
        Process a key event in the dialog. Two keys are allowed: DEL and ESC. DEL removes the selected element and
        ESC clears all the input widgets.
        :param evt: event data.
        """

        if evt.key() == Qt.Key_Delete and len(self.nodeTable.selectedIndexes()) > 0:

            selected_row = self.nodeTable.selectedIndexes()[0].row()

            remove_node = Node(name=self.nodeTableModel.nodes[selected_row].name,
                              ip=self.nodeTableModel.nodes[selected_row].ipAddress,
                              type_node=self.nodeTableModel.nodes[selected_row].type,
                              sector=self.nodeTableModel.nodes[selected_row].sector,
                              pv_prefixes=Node.get_prefix_array(self.nodeTableModel.nodes[selected_row].pvPrefix))

            self.controller.remove_node_from_sector(remove_node)
            nodes = self.controller.get_nodes_from_sector(sector=self.sectors.itemText(self.sectors.currentIndex()),
                                                          registered=True)
            self.nodeTableModel.setData(nodes)
            self.nodeTable.clearSelection()

        elif evt.key() == Qt.Key_Escape:

            self.id_text.clear()
            self.address_text.clear()
            self.nodeTable.clearSelection()

        QTableView.keyPressEvent(self.nodeTable, evt)

    def selection_changed(self, selected, deselected):
        """
        Updates the input widgets according to the selected node.
        :param selected: the selected item.
        :param deselected: the item that was de-selected.
        """

        if len(selected.indexes()) > 0:
            selected_row = selected.indexes()[0].row()
            node = self.nodeTableModel.nodes[selected_row]

            self.id_text.setText(node.name)
            self.address_text.setText(node.ipAddress)
            self.prefix.setText(Node.get_prefix_string(node.pvPrefix))

            items = [self.types.itemText(i) for i in range(self.types.count())]
            for index, item in enumerate(items):
                if node.type.name == item:
                    self.types.setCurrentIndex(index)

        QTableView.selectionChanged(self.nodeTable, selected, deselected)

    def closeEvent(self, args):
        """
        Closes and shuts the scanning thread down.
        """
        self.scanning = False
        QDialog.closeEvent(self, args)
