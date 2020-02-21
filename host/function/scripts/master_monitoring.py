#!/usr/bin/python-sirius
# -*- coding: utf-8 -*-
import logging
import argparse
import redis
from time import sleep

from common.database.redisbbb import RedisDatabase


logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('Whoami')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()


    # Connect to local Redis DB (MASTER) and enable external connections
    master_db = RedisDatabase("localhost", 6379)
    master_db.enable_external_connections()

    # Connect to remote Redis DB (MASTER)
    slave_db = RedisDatabase(master_db.getSlaveIP(), 6379)
    sleep(5)


    if (slave_db.getNodeController() == "SLAVE"):
        logger.info('Master applications have been launched! Tell Slave that Master is ready for controlling')
        master_db.setNodeController("MASTER")
        master_db.publishNodeController("MASTER")


    while True:
        sleep(5)
