import sys
import redis
import json
import time
import threading
import socket
import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
sys.path.append(os.path.abspath("../.."))
from common.network.utils import NetUtils
from common.entity.entities import Command

r = redis.StrictRedis(host = "10.0.38.59", port = 6379, db = 0)
qtCreatorFile = "redis.ui"
qtCreator_changefile = "change_bbb.ui"


Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
Ui_MainWindow_change, QtBaseClass_change = uic.loadUiType(qtCreator_changefile)



class ChangeBBB(QtWidgets.QMainWindow, Ui_MainWindow_change):
    def __init__(self, bbb_info=""):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow_change.__init__(self)
        self.setupUi(self)

        self.currentIP_value = bbb_info.split(" ")[0]
        self.currentHostname_value = bbb_info.split(" ")[-1]
        self.title.setText(bbb_info)
        self.currentIP.setText(self.currentIP_value)
        self.currentHostname.setText(self.currentHostname_value)

        self.prefixIP_value = self.currentIP_value.rsplit('.',1)[0] + '.'
        self.suffixIP_value = self.currentIP_value.split('.')[-1]

        self.prefixIP.setText(self.prefixIP_value)
        self.suffixIP.setValue(int(self.suffixIP_value))

        self.modeIP.activated.connect(self.IP_buttons)
        self.keepIP.toggled.connect(self.IP_buttons)
        self.keepHostname.toggled.connect(self.Hostname_buttons)

        self.changeButton.clicked.connect(self.updateBBB)


    def updateBBB(self):
        confirmation = QtWidgets.QMessageBox.question(self, 'Confirmation',
                                            "Are you sure?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirmation == QtWidgets.QMessageBox.Yes:
            print("Yes")
            if not self.keepHostname.isChecked():
                if self.newHostname.text() != "" and self.newHostname.text() != self.currentHostname_value:
#                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                    s.connect((self.currentIP_value, 9877))
#                    NetUtils.send_command(s, Command.SET_HOSTNAME)
#                    NetUtils.send_object(s, self.newHostname.text())
#                    s.close()
#                    time.sleep(1)
                    print("HN updated")

            if not self.keepIP.isChecked():
                if "{}".format(self.suffixIP.value()) != self.suffixIP_value:
#                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                    s.connect((self.currentIP_value, 9877))
#                    NetUtils.send_command(s, Command.SET_IP)
#                    NetUtils.send_object(s, self.modeIP.currentText().lower())
#                    if self.modeIP.currentText() == "MANUAL":
#                        NetUtils.send_object(s, self.prefixIP_value + "".format(self.suffixIP.value()))
#                        NetUtils.send_object(s, "255.255.255.0")
#                        NetUtils.send_object(s, prefixIP + "1")
#                    s.close()
#                    time.sleep(1)
                    print("IP updated")

            elif (not self.keepHostname.isChecked()) and self.newHostname.text() != self.currentHostname_value:
#                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                s.connect((self.currentIP_value, 9877))
#                NetUtils.send_command(s, Command.REBOOT)
#                s.close()
#                time.sleep(1)
                print("Reboot")


            self.close()

    def Hostname_buttons(self):
        if not self.keepHostname.isChecked():
            self.newHostname.setEnabled(True)
        else:
            self.newHostname.setEnabled(False)

        if self.keepHostname.isChecked() and self.keepIP.isChecked():
            self.changeButton.setEnabled(False)
        else:
            self.changeButton.setEnabled(True)


    def IP_buttons(self):
        if not self.keepIP.isChecked():
            self.modeIP.setEnabled(True)
            if self.modeIP.currentText() == "MANUAL":
                self.prefixIP.setEnabled(True)
                self.suffixIP.setEnabled(True)
            elif self.modeIP.currentText() == "DHCP":
                self.prefixIP.setEnabled(False)
                self.suffixIP.setEnabled(False)
        else:
            self.prefixIP.setEnabled(False)
            self.suffixIP.setEnabled(False)
            self.modeIP.setEnabled(False)

        if self.keepHostname.isChecked() and self.keepIP.isChecked():
            self.changeButton.setEnabled(False)
        else:
            self.changeButton.setEnabled(True)



class MonitoringBBB(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.items_info = {}
        self.items_state = {}
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.room_number.activated.connect(self.ShowNodes)
        self.find_value.returnPressed.connect(self.ShowNodes)
        self.connected_checkBox.toggled.connect(self.ShowNodes)
        self.disconnected_checkBox.toggled.connect(self.ShowNodes)

        self.deleteButton.clicked.connect(self.DeleteButton)
        self.rebootButton.clicked.connect(self.RebootButton)
        self.changeButton.clicked.connect(self.ChangeButton)

        self.list.setSortingEnabled(True)
        self.list.itemSelectionChanged.connect(self.DisplayButtons)


        self.autoUpdate_timer = QtCore.QTimer(self)
        self.autoUpdate_timer.timeout.connect(self.ShowNodes) 
        self.autoUpdate_timer.setSingleShot(False)
        self.autoUpdate_timer.start(1000) 

    def DeleteButton(self):
        itemsSelected = self.list.selectedItems()

        for item in itemsSelected:
            item_node_name = ("Ping:Node:" + item.text().split(" ")[0]).encode()

            self.items_info.pop(item_node_name)
            self.items_state.pop(item_node_name)

            item_index = self.list.row(item)
            self.list.takeItem(item_index)

    def RebootButton(self):
        itemsSelected = self.list.selectedItems()
        for item in itemsSelected:
            host_ip = item.text().split(" ")[0]
            if(self.items_state["Ping:Node:{}".format(host_ip).encode()] == True):
                print(host_ip)
#                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                s.connect((host_ip, 9877))
#                NetUtils.send_command(s, Command.REBOOT)
#                s.close()
                time.sleep(0.1)

    def ChangeButton(self):
        self.window = ChangeBBB(bbb_info = self.list.selectedItems()[0].text())
        self.window.show()



    def DisplayButtons(self):
        itemsSelected = self.list.selectedItems()

        if itemsSelected:
            self.rebootButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
            if len(itemsSelected) == 1:
                self.changeButton.setEnabled(True)
            else:
                self.changeButton.setEnabled(False)
        else:
            self.rebootButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
            self.changeButton.setEnabled(False)



    def ShowNodes(self):
        # Clear Node States
        for item in self.items_state.keys():
            self.items_state[item] = False

        # Get connected nodes
        self.items = r.keys(pattern = "Ping:Node:10.128.1{}*".format(self.room_number.currentText()))
        for item in self.items:
            self.items_info[item] = json.loads(r.get(item).decode().replace("'m"," am").replace("'","\""))
            self.items_state[item] = True

        for item in self.items_info.keys():
            item_ip = item.split(b'Node:')[1].decode()
            item_ip_name = item_ip + " - {}".format(self.items_info[item]['name'])

            if (self.find_value.text() == "" or self.find_value.text() in item_ip_name) and "10.128.1{}".format(self.room_number.currentText()) in item_ip:
                i = QtWidgets.QListWidgetItem(item_ip_name)
                if self.items_state[item] == False and self.disconnected_checkBox.isChecked():
                    i.setBackground(QtGui.QColor('red'))
                    if not self.list.findItems(item_ip_name, QtCore.Qt.MatchExactly):
                        self.list.addItem(i)

                elif self.items_state[item] == True and self.connected_checkBox.isChecked():
                    if not self.list.findItems(item_ip_name, QtCore.Qt.MatchExactly):
                        self.list.addItem(i)

        # Remove elements
        list_elements = []
        for row in range (self.list.count()):
            list_elements.append(("Ping:Node:"+self.list.item(row).text().split(" ")[0]).encode())

        for bbb in list_elements:
            item_ip = bbb.split(b'Node:')[1].decode()
            item_ip_name = item_ip + " - {}".format(self.items_info[bbb]['name'])
            qlistitem = self.list.findItems(bbb.split(b'Node:')[1].decode(), QtCore.Qt.MatchStartsWith)
            if qlistitem:
                item_index = self.list.row(qlistitem[0])

            if (not "10.128.1{}".format(self.room_number.currentText()) in item_ip) or \
               (not bbb in self.items_info.keys()) or \
               (self.find_value.text() != "" and not self.find_value.text() in item_ip_name):
                self.list.takeItem(item_index)

            if (self.items_state[bbb] == True and not self.connected_checkBox.isChecked()) or \
               (self.items_state[bbb] == False and not self.disconnected_checkBox.isChecked()):
                self.list.takeItem(item_index)

            else:
                if self.items_state[bbb] == False:
                    self.list.item(item_index).setBackground(QtGui.QColor('red'))
                else:
                    self.list.item(item_index).setBackground(QtGui.QColor('white'))


        self.list.sortItems()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonitoringBBB()
    window.show()
    sys.exit(app.exec_())

