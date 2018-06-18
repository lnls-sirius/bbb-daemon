from flask import request
from flask.json import jsonify
from flask_restful import Resource
from common.entity.entities import NodeState, Sector
from control.controller import MonitorController

'''
    Restful service ...
'''


class RestNode(Resource):
    def post(self):

        action = request.get_json(force=True).get('command', default=None)
        if action:
            if action.lower() == 'all':
                # All nodes
                pass
            elif action.lower() == 'sectors':
                # All sectors
                return jsonify(sectors=Sector.SECTORS)
            elif action.lower() == 'sector':
                # All nodes from sector
                sector = request.post.get('sector', default=None)
                if sector:
                    pass
            elif action.lower() == 'conf':
                # All configured nodes
                pass
            elif action.lower() == 'uconf':
                # All not configured nodes
                pass
            elif action.lower() == 'name':
                # Node by name (name is a primary key sort of ...)
                name = request.post.get('name', default=None)
                if name:
                    pass
            elif action.lower() == 's_c_u':
                # Get all sectors, connected nodes, disconnect/misconfigured nodes
                return get_s_c_u()

        return {}


def get_s_c_u():
    """
        Json. Gets the Connected nodes in a list and misconfigured/disconnected ones on another.
    :return: (list with all the sectors), (all connected nodes), (all disconnected/misconfigured nodes)
    """
    sectors_lbls = Sector.SECTORS
    c_vals = []
    u_vals = []

    for sector in Sector.SECTORS:
        c = 0
        u = len(MonitorController.monitor_controller.nodes[sector]['unconfigured'])

        for node in MonitorController.monitor_controller.nodes[sector]['configured']:
            if node.state == NodeState.CONNECTED:
                c = c + 1
            else:
                u = u + 1
        c_vals.append(c)
        u_vals.append(u)

    return jsonify(lbls=sectors_lbls, c_vals=c_vals, u_vals=u_vals)