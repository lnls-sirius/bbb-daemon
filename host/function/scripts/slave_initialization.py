#!/usr/bin/python-sirius
# -*- coding: utf-8 -*-
import logging
import time
import argparse
import redis
import netifaces
import json
from time import sleep

from common.function.consts import *
from common.database.redisbbb import RedisDatabase
from common.function.persist import persist_info


logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('Whoami')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()


    # Define IP connections
    slave_ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    ip = slave_ip.split('.')
    #master_ip = "{}.{}.{}.{}".format(ip[0], ip[1], int(ip[2])-100, ip[3])
    master_ip = '10.0.6.51'

    # Connect to local Redis DB (SLAVE)
    slave_db = RedisDatabase(slave_ip, 6379)
    slave_db.setMasterIP(master_ip)
    slave_db.setSlaveIP(slave_ip)

    # Connect to remote Redis DB (MASTER)
    master_db = RedisDatabase(master_ip, 6379)


    # Wait MASTER availability
    while(not master_db.is_available(delay = 5)):
        continue













        # SLAVE AVAILABLE, BUT NOT CONTROLLING
        print(slave_db.getNodeController().decode())
        if (slave_db.getNodeController().decode().upper() != "SLAVE"):
            master_db.setNodeController("MASTER")
            slave_db.setNodeController("MASTER")
            logger.info('Slave connected but not configured. Proceed with equipment identification...')

        # SLAVE CONTROLLING! GET INFO FROM IT
        else:
            master_db.setNodeController("SLAVE")
            info = json.loads(slave_db.getJSON())
            logger.info('Got info from BBB Slave, persisting to file...')
            persist_info(info['device'], info['baudrate'], info['details'], info['time'])

    else:
        logger.info('No BBB Slave detected. Proceed with equipment identification...')
