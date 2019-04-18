#!/usr/bin/python3
import argparse
import logging
import os
import sys
import signal

sys.path.append(os.path.abspath(os.path.join('../', __file__)))

from logging.handlers import RotatingFileHandler

args = {}
args['redis_ip'] = os.environ.get('REDIS_SERVER_IP')
args['redis_port'] = int(os.environ.get('REDIS_SERVER_PORT', 6379))

args['command_port'] = int(os.environ.get('COM_INTERFACE_TCP', 6789))
args['bbb_udp'] = int(os.environ.get('BBB_UDP', 9876))
args['bbb_tcp'] = int(os.environ.get('BBB_TCP', 9877))

args['workers'] = int(os.environ.get('WORKERS_NUM', 10))
args['web_port'] = int(os.environ.get('FLASK_PORT', 4850))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger()

from server.network.daemoninterface import DaemonHostListener
from server.control.controller import ServerController
from server.network.db import RedisPersistence

logger.info('Initializing LNLS CONS BBB Daemon Server')

def signal_handler(signum, frame):
    logger.info("Shutting everything down")

    ServerController.get_instance().stop_all()
    DaemonHostListener.get_instance().stop_all()

    logger.info("Bye bye")

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


db = RedisPersistence(host=args['redis_ip'], port=args['redis_port'])

server = ServerController()
daemon = DaemonHostListener(bbb_udp_port=args['bbb_udp'], bbb_tcp_port=args['bbb_tcp'], workers=args['workers'])
