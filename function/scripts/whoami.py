#!/usr/bin/python
# -*- coding: utf-8 -*-
from serial import Serial
from os import environ
from persist import persist_info

from consts import *

from devices import  mbtemp, counter_pru, no_tty,\
    power_suppply_pru, thermo_probe, mks9376b, agilent4uhv, spixcon


no_tty()
counter_pru()
power_suppply_pru()
thermo_probe()
mbtemp()
mks9376b()
agilent4uhv()
spixcon()
