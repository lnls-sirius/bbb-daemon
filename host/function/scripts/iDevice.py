#!/usr/bin/python-sirius
# # -*- coding: utf-8 -*-
import logging
import subprocess
import json
import re
from xlrd import open_workbook
from host.daemon.bbb import BBB


AUTOCONFIG = True
DEVICE_TYPE_COLUMN = "DEVICE_TYPE"
DEVICE_ID_COLUMN = "DEVICE_ID"
BBB_IP_COLUMN = "BBB_IP"
BBB_HOSTNAME_COLUMN = "BBB_HOSTNAME"
CONFIG_FILE = '/root/BBB-CONFIG.json'

Device_Type = { 0:"Undefined",
                1: "PowerSupply",
                2: "CountingPRU",
                3: "Thermo",
                4: "MBTemp",
                5: "4UHV",
                6: "MKS",
                7: "SPIxCONV"}

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('iDevice')

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
                info[DEVICE_ID_COLUMN] = [int(s) for s in re.findall(r'\d+', info[DEVICE_ID_COLUMN])]
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

        # Get devices from this subnet from the ConfigurationTable
        beagles = GetData(datafile="IA-xx.xlsx", subnet=subnet)

        # Check if current BBB (type and devices found is on ConfigurationTable)
        if beagles.data:
            for bbb in beagles.data[mydevice_type]:
                if(any(id in bbb[DEVICE_ID_COLUMN] for id in myids)): #[int(s) for s in re.findall(r'\d+', bbb[DEVICE_ID_COLUMN])] for id in myids)):
                    mybeagle_config = bbb
 
        # If BBB config is found, proceed with configuration from datafile
        if mybeagle_config:
            logger.info("Found a compatible device in spreadsheet: {}. Proceed with BBB configuration!".format(mybeagle_config))

            # Save found config into a json file
            with open(CONFIG_FILE, 'w') as fp:
                json.dump(mybeagle_config, fp)

            # Update hostname
            logger.info("BBB hostname: {}".format(mybeagle_config[BBB_HOSTNAME_COLUMN]))
            mybbb.update_hostname(mybeagle_config[BBB_HOSTNAME_COLUMN])

            IP_AVAILABLE = subprocess.call(['ping', '-c', '1', '-W', '1', mybeagle_config[BBB_IP_COLUMN]], stdout=subprocess.DEVNULL)
            # Update IP, if available
            if IP_AVAILABLE:
                logger.info("BBB IP {}".format(mybeagle_config[BBB_IP_COLUMN]))
                mybbb.update_hostname(mybeagle_config[BBB_HOSTNAME_COLUMN])
            else:
                logger.info("Desired IP {} is currently in use by another device.".format(mybeagle_config[BBB_IP_COLUMN]))
                

        # If BBB not found, keep DHCP and raise a flag!
        else:
            logger.info("A compatible device was NOT found in spreadsheet. Verify if there is a config file at {}.".format(mybeagle_config))
            
            try:
                # Get previous config
                with open(CONFIG_FILE, 'w') as fp:
                    file_config = json.loads(mybeagle_config, fp)

                # Configure hostname
                logger.info("BBB hostname: {}".format(file_config[BBB_HOSTNAME_COLUMN]))
                mybbb.update_hostname(file_config[BBB_HOSTNAME_COLUMN])

                # If same subnet and desided IP is available, proceed with IP configuration
                IP_AVAILABLE = subprocess.call(['ping', '-c', '1', '-W', '1', file_config[BBB_IP_COLUMN]], stdout=subprocess.DEVNULL)
                if subnet == file_config[BBB_IP_COLUMN].split('.')[2] \
                    and IP_AVAILABLE:
                    logger.info("BBB IP {}".format(file_config[BBB_IP_COLUMN]))
                    mybbb.update_hostname(file_config[BBB_HOSTNAME_COLUMN])
                else:
                    if not IP_AVAILABLE:
                        logger.info("Desired IP {} is currently in use by another device.".format(file_config[BBB_IP_COLUMN]))
                    else:
                        logger.info("Cannot change to IP {}, subnet is not compatible to current one ({}).".format(file_config[BBB_IP_COLUMN].split('.')[2], subnet))
                
            except:
                logger.info("BBB configuration not found ! Keeping DHCP")
        
