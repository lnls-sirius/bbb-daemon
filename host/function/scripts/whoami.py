#!/usr/bin/python
# -*- coding: utf-8 -*-
from serial import Serial
from os import environ
from persist import persist_info

from consts import *

from devices import  mbtemp, counting_pru, no_tty,\
    power_supply_pru, thermo_probe, mks9376b, agilent4uhv, spixconv


no_tty()
counting_pru()
power_supply_pru()
thermo_probe()
mbtemp()
mks9376b()
agilent4uhv()
spixconv()
