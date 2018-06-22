from flask import request, json
from flask.json import jsonify
from flask_restful import Resource

from common.entity.entities import NodeState, Sector
from common.serialization.models import NodeSchema, TypeSchema
from control.controller import MonitorController

node_schema = NodeSchema()
nodes_schema = NodeSchema(many=True)

type_schema = TypeSchema()
types_schema = TypeSchema(many=True)


class RestBBB(Resource):
    """
    Restful service. Communication with a specific beaglebone is made thought here !
    The client must send a post with an 'action' attribute inside a json
    """

    def post(self):
        suported_actions = ['reboot', 'switch']
        action = request.form.get('action', default=None)
        status, message = False, 'Supported Actions are {}'.format(suported_actions)
        if action:
            action = action.lower()
            if action == 'reboot':
                # reboot a BBB. Must pass its ip, sector and configured (true or false)
                bbb_ip = request.form.get('ip', None)
                bbb_sector = request.form.get('sector', None)
                configured = request.form.get('configured', None)
                status, message = RestBBB.reboot_bbb(ip=bbb_ip, sector=bbb_sector, configured=configured)
            elif action == 'switch':
                # Switch two different BBBs. One must be a configured node and other don't
                data = request.form.get('data', None)
                status, message = RestBBB.switch_bbb(data=data)

        return jsonify(status=status, message=message)

    @staticmethod
    def switch_bbb(data=None):
        # @todo: Implement this in a way that is more robust !
        if not data:
            return False, 'Not OK'
        data = json.loads(data)

        c_bbb = data['c_bbb']
        u_bbb = data['u_bbb']

        c_node = MonitorController.monitor_controller.getConfiguredNode(c_bbb['ip'], c_bbb['sector'])
        # u_node = MonitorController.monitor_controller.getConfiguredNode(u_bbb_ip, u_bbb_sector)

        if c_node and u_bbb['ip'] != '':
            MonitorController.monitor_controller.updateNode(oldNodeAddr=u_bbb['ip'], newNode=c_node)
            return True, 'Node Switched'

        return False, 'Not OK'

    @staticmethod
    def reboot_bbb(ip=None, sector=None, configured=None):
        # @todo: implement the right way !
        # json.loads(a)
        status, message = False, 'Not Ok!'
        if ip and sector and configured:
            if configured == 'true':
                node = MonitorController.monitor_controller.getConfiguredNode(ip, sector)
                if node:
                    MonitorController.monitor_controller.rebootNode(node, configured=configured)
                    status, message = True, 'Node {} rebooted '.format(node)
            elif configured == 'true':
                node = MonitorController.monitor_controller.getUnconfiguredNode(ip, sector)
                if node:
                    MonitorController.monitor_controller.rebootNode(node, configured=configured)
                    status, message = True, 'Node {} rebooted '.format(node)

        return status, message


class RestNode(Resource):
    """
        Restful service ...
        The client sends a data request to the server via post.
        The data should come in a json object named 'data' and this object must contain the
        action that the server should take.

        example:

        data :{
            action: 'a supported action'
        }
    """
    def post(self):
        """
        This isn't a fully restful implementation.
        :return: A json response according to the action sent.
        """
        suported_actions = ['all', 'sectors', 'sector', 'name', 'ip', 'conf', 'uconf', 'conf_uconf', 's_c_u']
        action = request.form.get('action', default=None)
        status, message = False, 'Supported Actions are {}'.format(suported_actions)
        if action:
            action = action.lower()
            if action == 'all':
                # All nodes
                status, message = False, 'Not implemented  ... :('
            elif action == 'sectors':
                # All sectors
                return jsonify(sectors=Sector.SECTORS)

            elif action == 'sector':
                # All nodes from sector
                sector = request.form.get('sector', default=None)
                return RestNode.get_nodes_sector(sector=sector)

            elif action == 'name':
                # Node by name (name is a primary key sort of ...)
                name = request.form.get('name', default=None)
                return RestNode.get_node_by_name(n_name=name)

            elif action == 'ip':
                # Node by ip
                ip = request.form.get('ip', default=None)
                return RestNode.get_node_by_ip(ip=ip)

            elif action == 'conf':
                # All configured nodes from a sector
                sector = request.form.get('sector', None)
                return RestNode.get_conf_from_sector(sector=sector)

            elif action.lower() == 'uconf':
                # All not configured nodes from a sector
                sector = request.form.get('sector', None)
                return RestNode.get_uconf_from_sector(sector=sector)

            elif action == 'conf_uconf':
                # conf and uconf nodes
                sector = request.form.get('sector', None)
                return RestNode.get_conf_uconf(sector=sector)

            elif action == 's_c_u':
                # Get all sectors, connected nodes, disconnect/misconfigured nodes
                return RestNode.get_sectors_connected_faulty()
            else:

                return jsonify(suported_actions)

        return jsonify(status=status, message=message)

    @staticmethod
    def get_node_by_name(n_name: str = None):
        node = MonitorController.monitor_controller.getNode(node_name=n_name)
        if node:
            return jsonify(node=node_schema.dump(node))
        else:
            return {}

    @staticmethod
    def get_node_by_ip(ip: str = None):
        node = MonitorController.monitor_controller.getNodeByAddr(ipAddress=ip)
        if node:
            return jsonify(node=node_schema.dump(node))
        else:
            return {}

    @staticmethod
    def get_conf_uconf(sector=None):
        """
        Json. The nodes which are configured, including the disconnected ones and also returns the not configured nodes in a
        separated list.
        The full json of the Node entity.
        :return: json {configured_nodes:[], unconfigured_nodes:[] }
        """
        if not sector:
            return {}
        u_nodes = []
        c_nodes = []

        if request.method == 'POST':
            c_nodes = MonitorController.monitor_controller.nodes[sector]["configured"]
            u_nodes = MonitorController.monitor_controller.nodes[sector]["unconfigured"]

        return jsonify(configured_nodes=nodes_schema.dump(c_nodes),
                       unconfigured_nodes=nodes_schema.dump(u_nodes))

    @staticmethod
    def get_sectors_connected_faulty():
        """
        Json. Gets the Connected nodes quantity in a list and not configured/disconnected ones on another.
        :return: (list with all the sectors), (number of connected nodes), (number of all disconnected/ not configured nodes)
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

    @staticmethod
    def get_conf_from_sector(sector: str = None):
        """
        Json. conf nodes from a sector.
        :return:
        """
        if not sector:
            return {}

        c_nodes = MonitorController.monitor_controller.nodes[sector]["configured"]
        return jsonify(configured_nodes=nodes_schema.dump(c_nodes))

    @staticmethod
    def get_uconf_from_sector(sector: str = None):
        """
        Json. uconf nodes from a sector.
        :return:
        """
        if not sector:
            return {}

        u_nodes = MonitorController.monitor_controller.nodes[sector]["unconfigured"]
        return jsonify(unconfigured_nodes=nodes_schema.dump(u_nodes))

    @staticmethod
    def get_nodes_sector(sector=None):
        """
        All nodes from a sector !
        nodes
        :param sector:
        :return:
        """
        if not sector:
            return {}
        nodes = MonitorController.monitor_controller.fetchNodesFromSector(sector=sector)
        return jsonify(nodes=nodes_schema.dump(nodes))


class RestType(Resource):
    """
    @todo: all !
    """
    pass
