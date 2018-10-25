#!/usr/bin/python3
import argparse
import logging
import os

from host.daemon import Daemon
  
CONFIG_PATH = os.environ.get('CONFIG_PATH', '/root/bbb-daemon/bbb.bin')
SERVER_ADDR = os.environ.get('SERVER_ADDR','10.0.6.44')
BIND_PORT = int(os.environ.get('BIND_PORT', 9877))
PING_PORT = int(os.environ.get('PING_PORT', 9876))
PING_CANDIDATES = os.environ.get('PING_CANDIDATES','10.0.6.44 10.0.6.48 10.0.6.51').split(' ')

if not SERVER_ADDR in PING_CANDIDATES:
    PING_CANDIDATES.append(SERVER_ADDR)

if __name__ == '__main__':

    parser = argparse.ArgumentParser("A program to manage and monitor each "
                                     "Beaglebone host in the Controls Group's network")

    parser.add_argument("--server-addr", "-s", nargs='?', default=SERVER_ADDR,
                        help="The server's IP address.", dest="server_address")

    parser.add_argument("--command-port", "-c", nargs='?', default=BIND_PORT,
                        help="The port from which command requests are received.", dest="command_port")

    parser.add_argument("--ping-port", "-p", nargs='?', default=PING_PORT,
                        help='The port to which ping request are sent.', dest="ping_port")

    parser.add_argument("--ftp-server-addr", "-S", nargs='?', default=SERVER_ADDR,
                        help="The FTP server's IP address", dest="ftp_server")

    parser.add_argument("--configuration-path", "-C", nargs='?', default=CONFIG_PATH,
                        help="The configuration file's location", dest="configuration_path")

    parser.add_argument('--log-path', '-l', nargs='?', default='./daemon.log',
                        help="Daemon's log file location.", dest='log_path')

    args = vars(parser.parse_args())

    logging.basicConfig(filename=args['log_path'], level=logging.INFO,
                        format='%(asctime)-15s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    Daemon(server_address=args['server_address'],
           ping_port=args['ping_port'],
           bind_port=args['command_port'],
           path=args['configuration_path'],
           ping_candidates=PING_CANDIDATES)

