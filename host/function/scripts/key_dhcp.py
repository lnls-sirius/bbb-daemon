#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import system
from time import sleep
from commands import getoutput
import serial

import logging
import Adafruit_BBIO.GPIO as GPIO

from PRUserial485 import PRUserial485_address

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('key_dhcp')

AUTOCONFIG = serial.Serial("/dev/ttyUSB0").cts


def dhcp():		#Set IP to DHCP
     service = ""
     while(service == ""):
         service = getoutput("(connmanctl services |awk '{print $3}')")
     logger.info("Ethernet service {}".format(service))
     system("connmanctl config {} --ipv4 dhcp".format(service))

def led():		#Shows the user that the IP has been configured
    for i in range(20):
        GPIO.output("P8_28", GPIO.HIGH)
        sleep(0.05)
        GPIO.output("P8_28", GPIO.LOW)
        sleep(0.05)

if __name__ == '__main__':
    logger.info("Verificando condicao DHCP em Hardware")

    device_addr = PRUserial485_address()

    GPIO.setup("P8_28", GPIO.OUT)    #Led configuration
    GPIO.output("P8_28", GPIO.LOW)

    if device_addr == 0:
        logger.info("Contadora detectada")

        for en_FF in ["P8_43", "P8_44", "P8_45", "P8_46", "P9_29", "P9_31"]: #Enable Flip-Flops
            sleep(0.05)
            GPIO.setup(en_FF, GPIO.OUT)
            sleep(0.05)
            GPIO.output(en_FF, GPIO.HIGH)

        sleep(1) #Sleep until FF set its output, frequency of input oscillator must be higher than 1 Hz
        state = ''
        for pin in ["P8_39", "P8_40", "P8_41", "P8_42", "P9_28", "P9_30"]:
            GPIO.setup(pin, GPIO.IN)
            sleep(0.05)
            state += str(GPIO.input(pin))

        if state == '101010':
            logger.info("Configurando DHCP")
            dhcp()
            led()
    else:
        #for pin in ["P8_11", "P8_12"]:
        #    GPIO.setup(pin, GPIO.IN)		#Pin out configurations
                                                                                                                #   |on|
        #if (GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 0): #Check if the keys are set to the DHCP position |dP|
        if (AUTOCONFIG):
            logger.info("AUTOCONFIG enabled. Configuring DHCP")
            dhcp()
            led()















#!/usr/bin/python

import os
import logging
import commands
import Adafruit_BBIO.GPIO as GPIO
from time import sleep

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('Key_dhcp')


def dhcp():		#Set IP to DHCP
     service = ""
     while(service == ""):
         service = commands.getoutput("(connmanctl services |awk '{print $3}')")
     logger.info("Ethernet service {}".format(service))
     os.system("connmanctl config {} --ipv4 dhcp".format(service))

def led():		#Shows the user that the IP has been configured
     for i in range(20):
          GPIO.output("P8_28", GPIO.HIGH)
          sleep(0.05)
          GPIO.output("P8_28", GPIO.LOW)
          sleep(0.05)

if __name__ == '__main__':
    logger.info("Verificando condicao DHCP em Hardware")

    GPIO.setup("P8_11", GPIO.IN)		#Pin out configurations
    GPIO.setup("P8_12", GPIO.IN)
    GPIO.setup("P8_28", GPIO.OUT)
    GPIO.output("P8_28", GPIO.LOW)
                                                                                                                #   |on|
    # if (GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 0): #Check if the keys are set to the DHCP position     |dP| 
    if (AUTOCONFIG):
        logger.info("AUTOCONFIG enabled. Configuring DHCP")
        dhcp()								                                        #   |12|
        led()
