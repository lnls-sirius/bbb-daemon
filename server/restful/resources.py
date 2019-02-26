import logging

logger = logging.getLogger()

from flask import request, json
from flask.json import jsonify
from flask_restful import Resource, reqparse

from flask_restful import reqparse, abort, Api, Resource
from common.entity.entities import NodeState, Sector
from common.serialization.models import dump_node, dump_type
from server.control.controller import ServerController

controller = ServerController.get_instance()

class Action(Resource):
    "Actions ..."
    pass

class Sectors(Resource):
    def get(self):
        return controller.get_sectors_dict()

class NodesAll(Resource):
    def get(self):
        return controller.get_ping_nodes()

class Nodes(Resource):
    def get(self, command):
        if command == 'all':
            # Return all active nodes
            return controller.get_ping_nodes()
        elif command == 'missing':
            # Return missing nodes.
            return controller.get_missing_nodes()
        elif command == 'expected':
            # Return expected nodes
            return controller.get_expected_nodes()
        else:
            abort(404, message='Command is not supported.')

class Types(Resource):
    def get(self):
        return controller.get_types()

class Node(Resource):
    def get(self):
        pass

    def post(self, command):
        parser = reqparse.RequestParser()
        try:
            parser.add_argument('ip', type=str, help='Node\'s IP address.')

            if not command:
                abort(404, message="Command is required")

            if command == 'reboot':
                args = parser.parse_args()
                controller.reboot_node(args.ip)

            elif command == 'ip':
                parser.add_argument('ip_new', type=str, help='New node\'s IP address.')
                parser.add_argument('ip_network', type=str, help='Node\'s network using the pattern xxxx.xxxx.xxxx.xxxx/xx.')
                parser.add_argument('ip_gateway', type=str, help='Node\'s default gateway.')
                args = parser.parse_args()
                controller.set_ip(args.ip, args.ip_new, args.ip_network, args.ip_gateway)

            elif command == 'hostname':
                parser.add_argument('hostname', type=str, help='New hostname.')
                args = parser.parse_args()
                controller.set_hostname(ip=args.ip, hostname=args.hostname)

            elif command == 'nameservers':
                parser.add_argument('nameservers', type=str, help='Node nameservers separated by spaces.')
                controller.set_nameservers(ip=args.ip, nameservers=args.nameservers)
            return 'Message received. Command: {} args: {}'.format(command,args)
        except:
            logger.exception('RestApi Exception')
            abort(404, message='Failed to execute command {} with args {}.'.format(command, args))