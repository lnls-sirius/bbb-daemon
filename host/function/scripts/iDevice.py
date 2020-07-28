#!/usr/bin/python-sirius
from xlrd import open_workbook
import subprocess
import json
import re
from host.daemon.bbb import BBB

AUTOCONFIG = True
DEVICE_TYPE_COLUMN = "DEVICE_TYPE"
DEVICE_ID_COLUMN = "DEVICE_ID"
BBB_IP_COLUMN = "BBB_IP"
BBB_HOSTNAME_COLUMN = "BBB_HOSTNAME"

Device_Type = { 0:"Undefined",
                1: "PowerSupply",
                2: "CountingPRU",
                3: "Thermo",
                4: "MBTemp",
                5: "4UHV",
                6: "MKS",
                7: "SPIxCONV"}


class GetData():
    def __init__(self, datafile="IA-xx.xlsx", subnet = ""):
        try:
            _sheet = open_workbook(datafile).sheet_by_name(subnet)
            keys = [_sheet.cell(0, col_index).value for col_index in range(_sheet.ncols)]
            self.data = {}

            for row_index in range(1,_sheet.nrows):
                dev_type = _sheet.cell(row_index, keys.index(DEVICE_TYPE_COLUMN)).value
                if dev_type == '':
                    continue
                info = {keys[col_index]: _sheet.cell(row_index, col_index).value for col_index in range(_sheet.ncols)}
                if dev_type in self.data:
                    self.data[dev_type].append(info)
                else:
                    self.data[dev_type] = [info]
        except:
            self.data = {}

if __name__ == '__main__':
    if(AUTOCONFIG):
        mybeagle_config = ''

        # Get device.json from whoami.py and get identified equipment
        mybbb = BBB()
        mydevice_type = Device_Type[mybbb.node.type.code]
        myids = [int(s) for s in re.findall(r'\d+', mybbb.node.details.split('\t')[0])]
        subnet = str(mybbb.get_ip_address()[0]).split('.')[2]
        subnet='121'
        print(subnet)

        # Get devices from this subnet from the ConfigurationTable
        beagles = GetData(datafile="IA-xx.xlsx", subnet=subnet)

        # Check if current BBB (type and devices found is on ConfigurationTable)
        if beagles.data:
            for bbb in beagles.data[mydevice_type]:
                if(any(id in [int(s) for s in re.findall(r'\d+', bbb[DEVICE_ID_COLUMN])] for id in myids)):
                    mybeagle_config = bbb
 
        # If BBB config is found, proceed with configuration from datafile
        if mybeagle_config:
            IP_AVAILABLE = subprocess.call(['ping', '-c', '1', mybeagle_config[BBB_IP_COLUMN]], stdout=subprocess.DEVNULL)
            # CONFIGURAR BBB DE ACORDO COM INFO ENCONTRADA!
            if IP_AVAILABLE:
                mybbb.update_hostname(mybeagle_config[BBB_HOSTNAME_COLUMN])
                print(mybeagle_config[BBB_HOSTNAME_COLUMN])


        # If BBB not found, keep DHCP and raise a flag!
        else:
            # GET OLD CONFIG
            print("BBB not found ! Keeping DHCP")
        
