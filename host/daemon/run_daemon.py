#!/usr/bin/python3
import argparse
import logging
import os
import time

from logging.handlers import RotatingFileHandler

from host.daemon.daemon import Daemon

parser = argparse.ArgumentParser("A program to manage and monitor each "
                                    "Beaglebone host in the Controls Group's network")

parser.add_argument("--ping-port", "-p", nargs='?', default=9876,type=int,
                    help='The port to which ping request are sent.', dest="ping_port")

parser.add_argument("--command-port", "-c", nargs='?', default=9877, type=int,
                    help="The port from which command requests are received.", dest="command_port")

parser.add_argument('--ping-candidates', '-pc', default='10.0.6.44;10.0.6.48;10.128.255.5',
                    help="Ping IP, separated by a space.", dest='ping_candidates')

parser.add_argument("--configuration-path", "-C", nargs='?', default='/var/tmp/bbb.bin',
                    help="The configuration file's location", dest="configuration_path")

parser.add_argument('--log-path', '-l', nargs='?', default='/var/log/bbb-daemon.log',
                    help="Daemon's log file location.", dest='log_path')

args = vars(parser.parse_args())

PING_CANDIDATES = args['ping_candidates'].split(';')

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(asctime)-15s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger()

if __name__ == '__main__':
    logger.info('Init params: {}'.format(args))
    Daemon(ping_port=args['ping_port'],
           bind_port=args['command_port'],
           path=args['configuration_path'],
           ping_candidates=PING_CANDIDATES)
    while True:
        time.sleep(1.0)
