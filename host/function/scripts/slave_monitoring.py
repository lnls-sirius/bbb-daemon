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


    # Connect to local Redis DB (SLAVE)
    slave_db = RedisDatabase("localhost", 6379)

    # Connect to remote Redis DB (MASTER)
    master_db = RedisDatabase(slave_db.getMasterIP(), 6379)


    while True:

        logger.info('Master monitoring has started!')
        while master_db.is_available(retries=1, log = False):
            sleep(0.05)

        logger.info('Master is down, tell server Slave will get control!')
        slave_db.setNodeController("SLAVE")
        slave_db.publishNodeController("SLAVE")

        logger.info('Wait Master recovery')
        while not master_db.is_available(retries=1, log = False):
            sleep(0.1)


        while master_db.getNodeController() == "SLAVE" or master_db.getNodeController() != "MASTER":
            sleep(1)

        logger.info('Master is up and ready, tell server Master will get control!')
        slave_db.setNodeController("MASTER")
        slave_publisher.publishNodeController("MASTER")
