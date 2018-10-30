# -*- coding: utf-8 -*-
import logging
import time

from serial import Serial
<<<<<<< HEAD
from os import environ, path
=======
from os import environ
from os import path
#!/usr/bin/python
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2
from persist import persist_info


from consts import *

from devices import  mbtemp, counting_pru, no_tty,\
    power_supply_pru, thermo_probe, mks9376b, agilent4uhv, spixconv

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

logger = logging.getLogger('Whoami')
<<<<<<< HEAD
logger.info('Iterating through possible devices ...')

# Loop until detect something
while not path.isfile(RES_FILE) or not path.isfile(BAUDRATE_FILE):
=======

while path.:
    pass
    logger.info('Iterating through possible devices ...')
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2
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

<<<<<<< HEAD
    time.sleep(2.)
=======
>>>>>>> 2fd49ea74b703db0ef4e4cb3e8dc96092c1883d2

logger.info('End of the identification Script ...')
