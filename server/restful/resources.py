from flask import request, json
from flask.json import jsonify
from flask_restful import Resource, reqparse

from flask_restful import reqparse, abort, Api, Resource

from common.entity.entities import NodeState, Sector
from common.serialization.models import dump_node, dump_type
from server.control.controller import ServerController

controller = ServerController.get_instance()

# node_schema = NodeSchema()
# nodes_schema = NodeSchema(many=True)

# type_schema = TypeSchema()
# types_schema = TypeSchema(many=True)

parser = reqparse.RequestParser()
parser.add_argument('ip', type=str, help='Node\'s IP address.')
parser.add_argument('new_ip', type=str, help='Node\'s new IP.')
parser.add_argument('new_mask', type=str, help='Node\'s new Mask.')
parser.add_argument('new_gateway', type=str, help='Node\'s new Gateway.')

class Action(Resource):
    "Actions ..."
    pass

class Sectors(Resource):
    def get(self):
        return controller.get_sectors_dict()

class Nodes(Resource):
    def get(self):
        return controller.get_ping_nodes()

class Types(Resource):
    def get(self):
        return controller.get_types()

class Node(Resource):
    def get(self):
        pass

    def post(self, command):
        args = parser.parse_args()
        if not command:
            abort(404, message="Command is required")

        if command == 'reboot':
            controller.reboot_node(ip=args['ip'])

        return 'Message received. Command: {} args: {}'.format(command,args)
