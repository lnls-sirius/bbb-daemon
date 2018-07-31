import argparse
import logging
import os
import signal

# import server.app as app

from server.network.commandinterface import ServerCommandInterface
from server.network.daemoninterface import DaemonHostListener
from server.sftp.sftp import FTPServerManager
from server.control.controller import ServerController
from server.network.db import RedisPersistence
from waitress import serve

REDIS_SERVER_IP = '0.0.0.0'
REDIS_SERVER_PORT = 6379
BBB_UDP = 9876
BBB_TCP = 9877
WEB_CLIENT_SERVER_PORT = 4850
COM_INTERFACE_TCP = 6789
WORKERS_NUM = 2
FTP_SERVER_PORT = 1026
FTP_HOME_DIR = '/root/bbb-daemon/types_repository/'


def signal_handler(signum, frame):

    print("Shutting everything down")

    ServerController.get_instance().stop_all()
    ServerCommandInterface.get_instance().stop_all()
    DaemonHostListener.get_instance().stop_all()
    FTPServerManager.get_instance().stop_ftp_server()

    print("Bye bye")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Controls group host management server.')

    parser.add_argument('--redis-ip', '-R', nargs='?', default=REDIS_SERVER_IP,
                        help="Redis database's IP address.", dest="redis_ip")

    parser.add_argument('--redis-port', '-P', nargs='?', default=REDIS_SERVER_PORT,
                        help="Redis database's socket port number.", dest='redis_port')

    parser.add_argument('--ping-port', '-p', nargs='?', default=BBB_UDP,
                        help='UDP port for ping requests coming from the hosts.', dest='bbb_udp')

    parser.add_argument('--config-port', '-b', nargs='?', default=BBB_TCP,
                        help="TCP port used by host to request their configuration.", dest='bbb_tcp')

    parser.add_argument('--web-port', '-w', nargs='?', default=WEB_CLIENT_SERVER_PORT,
                        help='Server port listening HTTP requests.', dest='web_port')

    parser.add_argument('--command-port', '-c', nargs='?', default=COM_INTERFACE_TCP,
                        help='Command port.', dest="command_port")

    parser.add_argument('--workers', '-W', nargs='?', default=WORKERS_NUM,
                        help='Number of threads that should be used to process host requests.', dest='workers')

    parser.add_argument('--ftp-port', '-f', nargs='?', default=FTP_SERVER_PORT,
                        help='Server port listening FTP requests.', dest='ftp_port')

    parser.add_argument('--ftp-path', '-F', nargs='?', default=FTP_HOME_DIR,
                        help='FTP root path.', dest='ftp_path')

    parser.add_argument('--log-path', '-l', nargs='?', default='./server.log',
                        help="Server's log file location.", dest='log_path')

    args = vars(parser.parse_args())

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

    # serve(app.get_wsgi_app(), host='0.0.0.0', port=args['web_port'])
