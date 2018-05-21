import os
import shutil
import threading
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from git import RemoteProgress, Repo

from common.entity.entities import Type
from gui.controller import GUIController
from gui.tableModel import TypeTableModel


class TypeDialog(QDialog):
    DIALOG_WIDTH = 800
    DIALOG_HEIGHT = 600

    UPDATE_TIME = 5

    def __init__(self, parent=None, controller: GUIController = None):

        super(TypeDialog, self).__init__(parent)

        self.controller = controller

        self.input = QWidget()

        self.inputLayout = QFormLayout()
        self.inputLayout.setContentsMargins(0, 0, 0, 0)

        self.input.setLayout(self.inputLayout)

        self.namelabel = QLabel("Name:")
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
        self.colorButton.pressed.connect(self.selectColor)

        self.submit = QPushButton("+")
        self.submit.pressed.connect(self.appendType)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(200, 80, 250, 20)

        self.checkUrl = QPushButton("Check Git URL")
        self.checkUrl.pressed.connect(self.checkUrlAction)

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
        self.typeTable.selectionChanged = self.selectionChanged
        self.typeTable.keyPressEvent = self.keyPressEvent
        self.typeTable.resizeRowsToContents()
        self.typeTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.typeTable.setSelectionMode(QAbstractItemView.SingleSelection)

        self.typeTableModel = TypeTableModel(self.typeTable, data=self.controller.fetchTypes())
        self.typeTable.setModel(self.typeTableModel)

        self.typeTable.horizontalHeader().setStretchLastSection(True)
        self.typeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # self.typeTable.setMinimumHeight(800)
        # self.typeTable.setMinimumWidth(500)

        self.labelTable = QLabel("Available types: (press [DEL] to remove)")

        self.inputLayout.addWidget(self.namelabel)
        self.inputLayout.addWidget(self.name)
        self.inputLayout.addWidget(self.repoUrlLabel)
        self.inputLayout.addWidget(self.repoUrl)
        self.inputLayout.addWidget(self.rcLocalPathLabel)
        self.inputLayout.addWidget(self.rcLocalPath)
        self.inputLayout.addWidget(self.descriptionLabel)
        self.inputLayout.addWidget(self.description)

        self.outerLayout.addWidget(self.input)
        self.outerLayout.addWidget(self.buttons)
        self.outerLayout.addWidget(self.labelTable)
        self.outerLayout.addWidget(self.typeTable)

        self.setLayout(self.outerLayout)

        self.setGeometry(500, 500, TypeDialog.DIALOG_WIDTH, TypeDialog.DIALOG_HEIGHT)

        self.setWindowTitle("Types Management")

        self.cdialog = QColorDialog(QColor(255, 255, 0), self)

        self.scanThread = threading.Thread(target=self.scan)
        self.scanning = True
        self.scanThread.start()

    def keyPressEvent(self, evt):

        # Del
        if evt.key() == 16777223 and len(self.typeTable.selectedIndexes()) > 0:

            selectedRow = self.typeTable.selectedIndexes()[0].row()
            typeName = self.typeTableModel.data(self.typeTableModel.index(selectedRow, 0), Qt.DisplayRole)

            self.controller.removeType(typeName)
            self.typeTableModel.setData(self.controller.fetchTypes())
            self.typeTable.clearSelection()

        elif evt.key() == 16777216:

            self.name.clear()
            self.description.clear()
            self.repoUrl.clear()
            self.rcLocalPath.clear()
            self.typeTable.clearSelection()
            self.cdialog.setCurrentColor(QColor(255, 255, 0))

        QTableView.keyPressEvent(self.typeTable, evt)

    def selectionChanged(self, selected, deselected):

        if len(selected.indexes()) > 0:
            selectedRow = selected.indexes()[0].row()
            typeObject = self.typeTableModel.types[selectedRow]

            #print('ob={}'.format(typeObject))
            #print('name={}'.format(typeObject.name))

            self.name.setText(typeObject.name)
            self.repoUrl.setText(typeObject.repoUrl)
            self.rcLocalPath.setText(typeObject.rcLocalPath)
            self.description.setPlainText(typeObject.description)
            self.cdialog.setCurrentColor(QColor(typeObject.color[0], typeObject.color[1], typeObject.color[2]))

        QTableView.selectionChanged(self.typeTable, selected, deselected)

    def checkUrlAction(self):
        success, message = self.checkUrlFunc()
        if success:
            QMessageBox.about(self, "Success!", message)
        else:
            QMessageBox.about(self, "Failure!", message)

    class CloneProgress(RemoteProgress):
        def __init__(self, uiParent):
            super().__init__()
            self.uiParent = uiParent

        def update(self, op_code, cur_count, max_count=None, message=''):
            ratio = cur_count / (max_count or 100.0)
            #print('op_code={} cur_count={} max_count={} ratio={}'.format(op_code, cur_count, max_count,
            #                                                             ratio, message or "NO MESSAGE"))
            self.uiParent.progressBar.setValue(ratio * 100)

    def checkUrlFunc(self):

        repo_name = None
        repo_dir = None

        url = self.repoUrl.displayText().strip()
        typeRcLocalPath = self.rcLocalPath.displayText()
        if typeRcLocalPath is None or typeRcLocalPath.strip() is None or url == "":
            return False, "rc.local is not defined."
        if url is None or url.strip() is None or url == "":
            return False, "URL is not defined."
        if not url.endswith(".git") or (not url.startswith("http://") and not url.startswith("https://")):
            return False, "\'{}\' is not a valid git URL.".format(url)

        try:

            repo_name = url.strip().split('/')[-1].split('.')[0]

            if repo_name is not None:
                repo_dir = os.getcwd() + '/' + repo_name + '/'
                if os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                    shutil.rmtree(repo_dir)
                    time.sleep(1)

            if repo_name is None or repo_dir is None or os.path.exists(repo_dir):
                return False, "Error with the cloned directory {}.".format(repo_dir)

            Repo.clone_from(url=url.strip(), to_path=repo_dir, progress=self.CloneProgress(self))
            if repo_dir.endswith('/') and typeRcLocalPath.startswith('/'):
                typeRcLocalPath = typeRcLocalPath[1:]
            elif not repo_dir.endswith('/') and not typeRcLocalPath.startswith('/'):
                repo_dir = repo_dir + '/'

            if not os.path.isfile(repo_dir + typeRcLocalPath):
                shutil.rmtree(repo_dir)
                return False, "rc.local not found on path. Type the full path including the filename. {}".format(
                    repo_dir + typeRcLocalPath)
            pass

            shutil.rmtree(repo_dir)
            return True, "Successfully cloned the repository."
        except Exception as e:
            if repo_name is not None and os.path.exists(repo_dir) and os.path.isdir(repo_dir):
                shutil.rmtree(repo_dir)
            return False, "Error when cloning the repository. {}.".format(e)

    def selectColor(self):
        self.cdialog.open()

    def appendType(self):
        selectedColor = self.cdialog.currentColor()

        newType = Type(name=self.name.displayText().strip(),
                       description=self.description.toPlainText().strip(),
                       repoUrl=self.repoUrl.displayText().strip(),
                       rcLocalPath=self.rcLocalPath.displayText().strip(),
                       color=(selectedColor.red(), selectedColor.green(), selectedColor.blue()))

        #print("-----------------------------------\n{}\n-----------------------------------".format(newType))
        self.controller.appendType(newType)

        self.typeTableModel.setData(self.controller.fetchTypes())
        self.typeTable.clearSelection()

    def scan(self):
        while self.scanning:
            self.typeTableModel.setData(self.controller.fetchTypes())
            time.sleep(TypeDialog.UPDATE_TIME)

    def closeEvent(self, args):

        self.scanning = False

        QDialog.closeEvent(self, args)
