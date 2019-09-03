import socket
from time import sleep
from common.entity.entities import Command
from common.network.utils import NetUtils

if __name__ == "__main__":
    close()

command =''

def connection(ip):
	global command
	command = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 	# Inicia um comando Socket com a BBB	
	command.connect((ip,9877))		    			# Conecta no Socket da BBB
	return(None)

def set_name(ip, name = ''):
	global command
	if name != '':
		connection(ip)
		print('set name: ' + name)
		NetUtils.send_command(command, Command.SET_HOSTNAME)
		NetUtils.send_object(command,str(name))				#Altera o Hostname da BBB		
		return()

def set_ip(ip, room, new_ip = ''):

	if new_ip != '':	
		connection(ip)
		print(new_ip)
		NetUtils.send_command(command, Command.SET_IP)			#Altera o IP da BBB
		NetUtils.send_object(command,'manual')
		NetUtils.send_object(command,str(new_ip))
		NetUtils.send_object(command,'255.255.0.0')
		NetUtils.send_object(command,'10.0.6.1') #'10.128.'+room+'.1')
	
		
		
		
