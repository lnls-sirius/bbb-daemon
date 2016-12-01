#!/usr/bin/python-sirius
# -*- coding: utf-8 -*-
import logging
import time
import argparse

from sys import argv
from serial import Serial
from os import environ, path, remove
from common.function.persist import persist_info
from common.function.consts import *
from common.database.redisbbb import RedisDatabase

from devices import  mbtemp, counting_pru, no_tty,\
    power_supply_pru, thermo_probe, mks9376b, agilent4uhv, spixconv, reset

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('Whoami')

if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()


    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.reset:
        logger.info('Disable external connections for Redis DB!')
        RedisDatabase('localhost').disable_external_connections()
        logger.info('Reseting json file...')
        reset()

        exit(0)
    try:
        remove(RES_FILE)
    except :
        pass
    try:
        remove(BAUDRATE_FILE)
    except :
        pass

    # Loop until detect something
    while not path.isfile(RES_FILE) or not path.isfile(BAUDRATE_FILE):
            try:
                spixconv()

                #@todo: This should be more robust !
                counting_pru()

                power_supply_pru()
                thermo_probe()
                mbtemp()
                agilent4uhv()
                mks9376b()
                # no_tty()
            except SystemExit:
                exit()
            except:
                logger.exception('Something wrong happened !')

            time.sleep(2.)

    print('End of the identification Script ...')
    logger.info('End of the identification Script ...')
