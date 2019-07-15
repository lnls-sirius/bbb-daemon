#!/usr/bin/env python
#

import os
import commands
import Adafruit_BBIO.GPIO as GPIO
from time import sleep

os.system("echo 'Verificando condição DHCP em Hardware'")

def dhcp():		#Set IP to DHCP
     service = commands.getoutput("(connmanctl services |awk '{print $3}')")
     os.system("connmanctl config %s --ipv4 dhcp" %(service))
     return()

def led():		#Shows the user that the IP has been configured
     for i in range(20):
          GPIO.output("P8_28", GPIO.HIGH)
          sleep(0.05)
          GPIO.output("P8_28", GPIO.LOW)
          sleep(0.05)
     return()


GPIO.setup("P8_11", GPIO.IN)		#Pin out configurations
GPIO.setup("P8_12", GPIO.IN)
GPIO.setup("P8_28", GPIO.OUT)
GPIO.output("P8_28", GPIO.LOW)
									                                 #   |on|
if (GPIO.input("P8_11") == 1 and GPIO.input("P8_12") == 0): #Check if the keys are set to the DHCP position  |dP|
    os.system("echo 'Configurando DHCP'")
     dhcp()								                                 #   |12|
     led()
