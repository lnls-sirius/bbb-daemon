#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging, time
from sys import argv

from serial import Serial
from os import environ, path, remove
from persist import persist_info

from consts import *

from devices import  mbtemp, counting_pru, no_tty,\
    power_supply_pru, thermo_probe, mks9376b, agilent4uhv, spixconv, reset

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

logger = logging.getLogger('Whoami')

if __name__ == '__main__':
    if len(argv) == 2 and argv[1] == 'reset':
        logger.info('Reseting json file...')
        reset()
    else:
        logger.info('Iterating through possible devices ...')
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
                no_tty()
                counting_pru()
                power_supply_pru()
                thermo_probe()
                mbtemp()
                mks9376b()
                agilent4uhv()
                spixconv()
            except SystemExit:
                pass
            except:
                logger.exception('Something wrong happened !')

            time.sleep(2.)

        logger.info('End of the identification Script ...')
