#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from serial import Serial
from os import environ
from persist import persist_info

from consts import *

from devices import  mbtemp, counting_pru, no_tty,\
    power_supply_pru, thermo_probe, mks9376b, agilent4uhv, spixconv

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

logger = logging.getLogger('Whoami')
logger.info('Iterating through possible devices ...')
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
logger.info('End of the identification Script ...')
