import csv
import socket
import os
import time
import sys
sys.path.append(os.path.abspath("../.."))
from common.network.utils import NetUtils
from common.entity.entities import Command


itens = {}
with open('test.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=';')
    first_line = True
    for row in readCSV:
        if not first_line:
            itens[row[0]] = {"NewHostname":row[1], "NewIP":row[2]}
        else:
            first_line = False


for beagle in itens:
    print(beagle, itens[beagle])
    if itens[beagle]["NewHostname"] != "":
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((beagle, 9877))
        NetUtils.send_command(s, Command.SET_HOSTNAME)
        NetUtils.send_object(s, itens[beagle]["NewHostname"])
        s.close()
        time.sleep(1)

    if itens[beagle]["NewIP"] != "":
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((beagle, 9877))
        NetUtils.send_command(s, Command.SET_IP)
        NetUtils.send_object(s, "manual")
        NetUtils.send_object(s, itens[beagle]["NewIP"])
        NetUtils.send_object(s, "255.255.255.0")
        NetUtils.send_object(s, "")
        s.close()
        time.sleep(1)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((beagle, 9877))
        NetUtils.send_command(s, Command.REBOOT)
        s.close()
        time.sleep(1)
