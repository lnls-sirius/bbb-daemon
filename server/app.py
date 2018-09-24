#!/usr/bin/python3
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, json
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_restful import Api

from common.entity.entities import Sector, Type, Node, NodeState
from common.serialization.models import NodeSchema, TypeSchema
from server.control.controller import ServerController
from forms import EditNodeForm, EditTypeForm
from restful.resources import RestNode, RestBBB

controller = ServerController.get_instance()

app = Flask(__name__)
app.secret_key = "4dbae3052d7e8b16ebcfe8752f70a4efe68d2ae0558b4a1b25c5fd902284e52e"

Bootstrap(app)
nav = Nav(app)
api = Api(app)

api.add_resource(RestNode, '/node/')
api.add_resource(RestBBB, '/bbb/')

@nav.navigation()
def my_navbar():
    return Navbar('BBB Daemon System',
                  View('Monitor Sectors', 'home'),
                  View('View Nodes', 'view_nodes'),
                  View('Insert Node', 'edit_nodes'),
                  View('View Types', 'view_types'),
                  View('Insert Type', 'edit_types'))


@app.route("/")
@app.route("/home/", methods=['GET', 'POST'])
def home():
    sectors_list = Sector.SECTORS
    return render_template('index.html', sectors=sectors_list)


@app.route('/list_nodes/', methods=['POST'])
def list_nodes():
    sector = request.form.get('sector', 'Conectividade')
    nodes = controller.fetch_nodes_from_sector(sector)
    return render_template("node/refresh_nodes.html", nodes=nodes)


@app.route("/view_nodes/", methods=['GET', 'POST'])
def view_nodes():
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'DELETE':
            node_name = request.form.get('node_name', '')
            node = controller.get_node_by_name(node_name)
            if node:
                if controller.remove_node_from_sector(node):
                    return 'Node Deleted !'
                else:
                    return 'Failed to Delete !'
            else:
                return 'Node not found'

    sectors_list = Sector.SECTORS

    refresh_url = url_for('list_nodes')
    edit_url = url_for('edit_nodes')
    return render_template("node/view_nodes.html", refresh_url=refresh_url, edit_url=edit_url, sectors=sectors_list)


@app.route("/edit_nodes/", methods=['GET', 'POST'])
def edit_nodes(node=None):
    types = controller.fetch_types()
    edit_nodes_form = EditNodeForm()
    edit_nodes_form.type.choices = [(t.name, "Type Name: {}\t\tType Url: {}".
                                     format(t.name, t.repoUrl)) for t in types]
    edit_nodes_form.sector.choices = [(s, "{}".
                                       format(s)) for s in Sector.SECTORS]

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'VALIDATE':
            # @todo: implement this !
            # git_url = request.form.get('gitUrl', '')

            # success, message = controller.validateRepository(git_url=git_url)

            # return jsonify(success=success, message=message)
            pass
        elif action == 'EDIT':
            # @todo: implement an edit function.... currently everything goes to action == ''
            pass
        elif action == '':
            # Insert new  node
            if edit_nodes_form.validate_on_submit():
                type = controller.find_type_by_name(edit_nodes_form.type.data)
                if type:

                    res_1, message_1 = controller.validate_repository(
                        rc_path=edit_nodes_form.rc_local_path.data,
                        git_url=type.repoUrl, check_rc_local=True)

                    res_2, message_2 = controller.check_ip_available(
                        ip=edit_nodes_form.ip_address.data,
                        name=edit_nodes_form.name.data)
                    if res_1 and res_2:
                        node = Node(name=edit_nodes_form.name.data,
                                    ip=edit_nodes_form.ip_address.data,
                                    sector=edit_nodes_form.sector.data,
                                    pv_prefixes=Node.get_prefix_array(edit_nodes_form.pv_prefix.data),
                                    type_node=type,
                                    rc_local_path=edit_nodes_form.rc_local_path.data)
                        controller.manage_nodes(node)
                        flash('Successfully edited node {} !'.format(node), 'success')
                        return redirect(url_for("view_nodes"))
                    else:
                        flash("Failed to edit/insert node.", 'danger')
                        if not res_1:
                            flash("{}".format(message_1), 'danger')
                        if not res_2:
                            flash("{}".format(message_2), 'danger')

    if request.method == 'GET':
        print("GET {}".format(request.args))
        node_name = request.args.get('node_name', '')
        node = controller.get_node_by_name(node_name)
        if node:
            edit_nodes_form.set_initial_values(node)

    return render_template("node/edit_node.html", node=node, form=edit_nodes_form)


@app.route('/list_types/', methods=['POST'])
def list_types():
    types = controller.fetch_types()
    return render_template("type/refresh_types.html", types=types)


@app.route("/view_types/", methods=['GET', 'POST'])
def view_types():
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'DELETE':
            type_name = request.form.get('type_name', '')
            if type_name == '':
                return 'Invalid type name'

            type_to_delete = controller.find_type_by_name(type_name)
            if type_to_delete is not None:
                print('{}'.format(type_to_delete))
                controller.remove_type_by_name(type_to_delete.name)
                return 'Type deleted'
            else:
                return 'Type not found'

    types = controller.fetch_types()
    refresh_url = url_for('list_types')
    edit_url = url_for('edit_types')

    return render_template("type/view_types.html", edit_url=edit_url, refresh_url=refresh_url, types=types)


@app.route("/edit_types/", methods=['GET', 'POST'])
def edit_types(type=None):
    edit_types_form = EditTypeForm()

    if request.method == 'GET':
        type_name = request.args.get('type_name', '')
        if type_name is not '':
            type = controller.find_type_by_name(type_name)
            edit_types_form.set_initial_values(type)

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'VALIDATE':

            git_url = request.form.get('gitUrl')

            success, message = controller.validate_repository(git_url=git_url)

            return jsonify(success=success, message=message)

        elif action == '':
            if edit_types_form.validate_on_submit():
                success, message_sha = controller.clone_repository(
                    git_url=edit_types_form.repo_url.data)
                if success:
                    new_type = Type(name=edit_types_form.name.data,
                                    repo_url=edit_types_form.repo_url.data,
                                    description=edit_types_form.description.data, sha=message_sha)
                    controller.manage_types(new_type)

                    flash('Successfully edited type {} !'.format(new_type), 'success')
                    return redirect(url_for("view_types"))
                else:
                    flash('Failed to edit/insert type {} !'.format(message_sha), 'danger')
        else:
            return 'Invalid Command'

    return render_template("type/edit_type.html", type=type, form=edit_types_form, url=url_for('edit_types'))


def get_wsgi_app():
    return app


def start_webserver(port: int = 5000):
    app.run(debug=False, use_reloader=False, port=port, host="0.0.0.0")
