import argparse
import logging
import os
import signal

from server.network.commandinterface import ServerCommandInterface
from server.network.daemoninterface import DaemonHostListener
from server.sftp.sftp import FTPServerManager
from server.control.controller import ServerController
from server.network.db import RedisPersistence 

args = {}
args['redis_ip'] = os.environ.get('REDIS_SERVER_IP', '0.0.0.0')
args['redis_port'] = int(os.environ.get('REDIS_SERVER_PORT', 6379))

args['bbb_udp'] = int(os.environ.get('BBB_UDP', 9876))
args['bbb_tcp'] = int(os.environ.get('BBB_TCP', 9877))

args['command_port'] = int(os.environ.get('COM_INTERFACE_TCP', 6789))
args['workers'] = int(os.environ.get('WORKERS_NUM', 10))
args['web_port'] = int(os.environ.get('FLASK_PORT', 4850))
args['ftp_port'] = int(os.environ.get('FTP_SERVER_PORT', 21))
args['ftp_path'] = os.environ.get('FTP_HOME_DIR', '../types_repository/') 

args['log_path'] = os.environ.get('LOG_PATH','./server.log')

def signal_handler(signum, frame):

    print("Shutting everything down")

    ServerController.get_instance().stop_all()
    ServerCommandInterface.get_instance().stop_all()
    DaemonHostListener.get_instance().stop_all()
    FTPServerManager.get_instance().stop_ftp_server()

    print("Bye bye")

logging.basicConfig(filename=args['log_path'], level=logging.INFO,
                    format='%(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if not os.path.exists(args['ftp_path']):
    os.mkdir(args['ftp_path'])

# Start FTP server
ftp = FTPServerManager(ftp_home_dir=args['ftp_path'], ftp_port=args['ftp_port'])

db = RedisPersistence(host=args['redis_ip'], port=args['redis_port'])

server = ServerController(sftp_home_dir=args['ftp_path'])

daemon = DaemonHostListener(bbb_udp_port=args['bbb_udp'], bbb_tcp_port=args['bbb_tcp'], workers=args['workers'])

command = ServerCommandInterface(comm_interface_port=args['command_port'])

from app import app as wsgi_app
