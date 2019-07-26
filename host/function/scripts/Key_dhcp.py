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
    if (GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 0): #Check if the keys are set to the DHCP position     |dP|
        logger.info("Configurando DHCP")
        dhcp()								                                        #   |12|
        led()
