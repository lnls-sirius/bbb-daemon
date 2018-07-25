from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from client.qt.gui.controller import QtInterfaceController
from client.qt.gui.dialogs import NodeDialog, QtTypeDialog
from client.qt.gui.tab import QtInterfaceTab
from common.entity.entities import Sector


class QtInterface(QMainWindow):
    """
    The Qt5-based main graphical interface.
    """
    WIDTH = 1600
    HEIGHT = 1200

    updateIcon = pyqtSignal(int)

    def __init__(self, server: str = "localhost", server_port: int = 6789):
        """
        Builds the interface.
        :param server: the server's IP address.
        :param server_port: the server's port.
        """

        super().__init__()

        self.controller = QtInterfaceController(server=server, servPort=server_port)

        self.menu_bar = self.menuBar()
        self.edit_menu = self.menu_bar.addMenu('&Edit')

        self.add_type_action = self.edit_menu.addAction('&Types Management')
        self.add_type_action.setShortcut("Ctrl+T")
        self.add_type_action.triggered.connect(self.manage_types)
        self.add_type_action.setShortcutContext(Qt.ApplicationShortcut)

        self.add_node_action = self.edit_menu.addAction('&Nodes Management')
        self.add_node_action.setShortcut("Ctrl+N")
        self.add_node_action.triggered.connect(self.manage_nodes)
        self.add_node_action.setShortcutContext(Qt.ApplicationShortcut)

        self.exit_action = self.menu_bar.addAction('E&xit')
        self.exit_action.triggered.connect(self.exit)
        self.exit_action.setShortcut("Ctrl+X")
        self.exit_action.setShortcutContext(Qt.ApplicationShortcut)

        self.central_widget = QWidget()

        self.widget_box = QVBoxLayout()
        self.widget_box.setContentsMargins(10, 10, 10, 10)
        self.widget_box.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)

        for index, i in enumerate(Sector.sectors()):
            self.tabs.insertTab(index,
                                QtInterfaceTab(parent=self.tabs, sector=str(i), controller=self.controller, tab_index=index,
                                               update_icon=self.updateIcon), str(i))

        self.widget_box.addWidget(self.tabs)
        self.central_widget.setLayout(self.widget_box)

        self.setWindowTitle("Controls Group's Single Board Computer Monitor")
        self.setCentralWidget(self.central_widget)

        self.setGeometry(500, 500, QtInterface.WIDTH, QtInterface.HEIGHT)

        self.icons = QIcon()
        self.icons.addFile('ico/bbb16x16.png', QSize(16, 16))
        self.icons.addFile('ico/bbb24x24.png', QSize(24, 24))
        self.icons.addFile('ico/bbb32x32.png', QSize(32, 32))
        self.icons.addFile('ico/bbb48x48.png', QSize(48, 48))
        self.icons.addFile('ico/bbb256x256.png', QSize(256, 256))

        self.setWindowIcon(self.icons)

        self.updateIcon.connect(self.test)
        self.show()

    def test(self, tab_index):
        """
        Tests if the tab index is in a warning state. In this case, show a warning icon.
        :param tab_index: tab's index.
        """
        if self.tabs.widget(tab_index).is_in_warning_state():
            self.tabs.setTabIcon(tab_index, QIcon.fromTheme("dialog-warning"))
        else:
            self.tabs.setTabIcon(tab_index, QIcon())

    def manage_types(self):
        """
        Launches a new types management dialog.
        """
        type_dialog = QtTypeDialog()
        type_dialog.center()
        type_dialog.show()

    def manage_nodes(self):
        """
        Launches a new nodes management dialog.
        """
        node_dialog = NodeDialog()
        node_dialog.center()
        node_dialog.show()

    def stop_all(self):
        """
        Stops all scanning threads of each tab object.
        """
        for tabIndex in range(self.tabs.count()):
            self.tabs.widget(tabIndex).stop()

    def closeEvent(self, evt):
        self.stop_all()
        QMainWindow.closeEvent(self, evt)

    def exit(self):
        """
        Stops all and exits.
        """
        self.stop_all()
        self.close()
