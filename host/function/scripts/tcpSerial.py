#!/usr/bin/python3
import argparse
import logging
import socket
import struct
import select

from serial import Serial

if __name__ == '__main__':

    parser = argparse.ArgumentParser("TCP - Serial Bind")
    parser.add_argument("--port","-p", default=4161,type=int, help='TCP Server port', dest="port")
    parser.add_argument("--tcp-buffer","-tcpb", default=1024,type=int, help='TCP recv buffer', dest="tcp_buffer")
    parser.add_argument("--baudrate","-b", default=115200,type=int, help='Serial port baudrate', dest="baudrate")
    parser.add_argument("--ser-buffer","-serb", default=1024,type=int, help='Serial port read buffer', dest="ser_buffer")
    parser.add_argument("--timeout","-t", default=0.1, type=float, help='Serial port timeout', dest="timeout")
    parser.add_argument("--device","-d", default='/dev/ttyUSB0', help='Serial port full path', dest="device")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s [%(levelname)s] %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger()


    ser = Serial(args.device, args.baudrate, timeout=args.timeout)
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', args.port))
            s.listen()
            logger.info('Listening ...')
            conn, addr = s.accept()
            try:
                with conn:
                    logger.info('Connected {} {}'.format(conn, addr))
                    while True:
                        data = conn.recv(args.tcp_buffer)
                        ser.write(data)
                        res = ser.read(args.ser_buffer)
                        if not data:
                            logger.info('No data...')
                            break
                        conn.sendall(res)
                        logger.info('In %s Out %s %s' % (data, res, len(res)))
            except ConnectionError:
                logger.exception('Connection Error !')
