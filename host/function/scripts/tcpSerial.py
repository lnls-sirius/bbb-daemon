#!/usr/bin/python3
import argparse
import logging
import logging.handlers
import socket
import struct
import select

from serial import Serial

if __name__ == '__main__':

    parser = argparse.ArgumentParser("TCP - Serial Bind")
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument("--port","-p", default=4161,type=int, help='TCP Server port', dest="port")
    parser.add_argument("--tcp-buffer","-tcpb", default=1024,type=int, help='TCP recv buffer', dest="tcp_buffer")
    parser.add_argument("--baudrate","-b", default=115200,type=int, help='Serial port baudrate', dest="baudrate")
    parser.add_argument("--ser-buffer","-serb", default=1024,type=int, help='Serial port read buffer', dest="ser_buffer")
    parser.add_argument("--timeout","-t", default=0.1, type=float, help='Serial port timeout', dest="timeout")
    parser.add_argument("--device","-d", default='/dev/ttyUSB0', help='Serial port full path', dest="device")
    parser.add_argument("--zero-bytes","-zb", default='ZB', help='What to return when a zero lengh response is returned from the serial port.', dest="zero_bytes")
    args = parser.parse_args()

    zb = args.zero_bytes.encode('utf-8')

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
            format='[%(levelname)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger()

    socketHandler = logging.handlers.SocketHandler('10.128.255.5', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    logger.addHandler(socketHandler)

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
                        conn.sendall(res if res else zb)
                        logger.debug('In=%s Out=%s len=%s' % (data, res, len(res)))
            except ConnectionError:
                logger.exception('Connection Error !')
