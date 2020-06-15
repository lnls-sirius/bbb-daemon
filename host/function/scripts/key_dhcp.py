#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import system
from time import sleep
from commands import getoutput
from consts import RES_FILE, BAUDRATE_FILE

import logging
import Adafruit_BBIO.GPIO as GPIO

from PRUserial485 import PRUserial485_address

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger('Key_dhcp')

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

    for teste in ["P8_43", "P8_44", "P8_45", "P8_46", "P9_29", "P9_31"]:
        sleep(0.05)
        GPIO.setup(teste, GPIO.OUT)
        sleep(0.05)
        GPIO.output(teste, GPIO.HIGH)
        sleep(0.05)

    if device_addr == 0:
        logger.info("Contadora detectada")

        for teste in ["P8_43", "P8_44", "P8_45", "P8_46", "P9_29", "P9_31"]: #Enable Flip-Flops
            sleep(0.05)
            GPIO.setup(teste, GPIO.OUT)
            sleep(0.05)
            GPIO.output(teste, GPIO.HIGH)

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
        for pin in ["P8_11", "P8_12"]:
            GPIO.setup(pin, GPIO.IN)		#Pin out configurations
                                                                                                                #   |on|
        if (GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 0): #Check if the keys are set to the DHCP position |dP|
            logger.info("Configurando DHCP")								                                    #   |12|
            dhcp()
            led()

