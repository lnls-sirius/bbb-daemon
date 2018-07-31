import argparse
import os

CONFIG_PATH = "/root/bbb-daemon/bbb.bin"
TYPE_RC_LOCAL_PATH = "init/rc.local"
RC_LOCAL_DESTINATION_PATH = "/etc/rc.local"
FTP_SERVER_PORT = 1026

# This info should contain a '/'
FTP_DESTINATION_FOLDER = '/root/'
SERVER_ADDR = "10.0.6.44"
PING_PORT = 9876
BIND_PORT = 9877
BOOT_PORT = 9878

# CLONE_PATH = "../"  # remember to place the forward slash !

if __name__ == '__main__':

    parser = argparse.ArgumentParser("A program to manage and monitor each "
                                     "Beaglebone host in the Controls Group's network")

    parser.add_argument("--server-addr", "-s", nargs='?', default=SERVER_ADDR,
                        help="The server's IP address.", dest="server_address")

    parser.add_argument("--command-port", "-c", nargs='?', default=BIND_PORT,
                        help="The port from which command requests are received.", dest="command_port")

    parser.add_argument("--ping-port", "-p", nargs='?', default=PING_PORT,
                        help='The port to which ping request are sent.', dest="ping_port")

    parser.add_argument("--boot-port", "-b", nargs='?', default=BOOT_PORT,
                        help='The port that a BBB used when it booted to load the project it must run',
                        dest="boot_port")

    parser.add_argument("--ftp-server-addr", "-S", nargs='?', default=SERVER_ADDR,
                        help="The FTP server's IP address", dest="ftp_server")

    parser.add_argument("--ftp-server-port", "-P", nargs='?', default=FTP_SERVER_PORT,
                        help="The FTP server's listening port", dest="ftp_port")

    parser.add_argument("--ftp-destination-folder", '-F', nargs='?', default=FTP_DESTINATION_FOLDER,
                        help="The path which the project will be copied to", dest="ftp_destination")

    parser.add_argument("--configuration-path", "-C", nargs='?', default=CONFIG_PATH,
                        help="The configuration file's location", dest="configuration_path")

    parser.add_argument("--project-rc-local", "-r", nargs='?', default=TYPE_RC_LOCAL_PATH,
                        help="RC.local path inside the project repository.", dest="project_rc_local")

    parser.add_argument("--node-rc-local", "-R", nargs='?', default=RC_LOCAL_DESTINATION_PATH,
                        help="A node's RC.local path.", dest="node_rc_local")

    args = vars(parser.parse_args())

    if not args['ftp_destination'].endswith('/'):
        args['ftp_destination'] = args['ftp_destination'] + '/'

    if not os.path.exists(args['ftp_destination']):
        os.makedirs(args['ftp_destination'])

    Daemon(server_address=args['server_address'],
           ping_port=args['ping_port'],
           bind_port=args['command_port'],
           boot_port=args['boot_port'],
           path=args['configuration_path'],
           rc_local_dest_path=args['node_rc_local'],
           ftp_destination_folder=args['ftp_destination'])
