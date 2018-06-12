from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

from common.entity.entities import Sector, Type, Node
from control.controller import MonitorController
from forms import EditNodeForm, EditTypeForm

app = Flask("server")
app.secret_key = "4dbae3052d7e8b16ebcfe8752f70a4efe68d2ae0558b4a1b25c5fd902284e52e"

Bootstrap(app)
nav = Nav(app)


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
    refresh_url = url_for('refresh_active_nodes')
    reboot_bbb_url = url_for('reboot_bbb')
    switch_bbb_url = url_for('switch_bbb')
    return render_template('index.html', refresh_url=refresh_url, switch_bbb_url=switch_bbb_url,
                           reboot_bbb_url=reboot_bbb_url, sectors=sectors_list)


@app.route('/refresh_active_nodes/', methods=['POST', 'GET'])
def refresh_active_nodes():
    u_nodes = []
    c_nodes = []

    if request.method == 'POST':
        sector = request.form.get('sector', 'Conectividade')
        c_nodes = monitor_controller.nodes[sector]["configured"]
        u_nodes = monitor_controller.nodes[sector]["unconfigured"]

    return render_template("refresh_tables.html", configured_nodes=c_nodes, unconfigured_nodes=u_nodes)


@app.route('/reboot_bbb/', methods=['POST'])
def reboot_bbb():
    bbb_ip = request.form.get('bbb_ip', '')
    bbb_sector = request.form.get('bbb_sector', '')

    print('id={} sector={}'.format(bbb_ip, bbb_sector))
    if bbb_ip != '' and bbb_sector != '':
        node = monitor_controller.getConfiguredNode(bbb_ip, bbb_sector)
        if node:
            monitor_controller.rebootNode(node)
            return 'Node Rebooted'

    return 'Not OK'


@app.route('/switch_bbb/', methods=['POST'])
def switch_bbb():
    c_bbb_ip = request.form.get('c_bbb_ip', '')
    c_bbb_sector = request.form.get('c_bbb_sector', '')

    u_bbb_ip = request.form.get('u_bbb_ip', '')
    u_bbb_sector = request.form.get('u_bbb_sector', '')

    if c_bbb_ip != '' and c_bbb_sector != '' and u_bbb_ip != '' and u_bbb_sector != '':

        c_node = monitor_controller.getConfiguredNode(c_bbb_ip, c_bbb_sector)
        u_node = monitor_controller.getConfiguredNode(u_bbb_ip, u_bbb_sector)

        if c_node and u_node:
            monitor_controller.updateNode(c_node, u_node)
            return 'Node Switched'

    return 'Not OK'


@app.route('/list_nodes/', methods=['POST'])
def list_nodes():
    sector = request.form.get('sector', 'Conectividade')
    nodes = monitor_controller.fetchNodesFromSector(sector)
    return render_template("node/refresh_nodes.html", nodes=nodes)


@app.route("/view_nodes/", methods=['GET', 'POST'])
def view_nodes():
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'DELETE':
            node_name = request.form.get('node_name', '')
            node = monitor_controller.getNode(node_name)
            if node:
                if monitor_controller.removeNodeFromSector(node):
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
    types = monitor_controller.fetchTypes()
    edit_nodes_form = EditNodeForm()
    edit_nodes_form.type.choices = [(t.name, "Type Name: {}\t\tType Url: {}".
                                     format(t.name, t.repoUrl)) for t in types]
    edit_nodes_form.sector.choices = [(s, "{}".
                                       format(s)) for s in Sector.SECTORS]

    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == '':
            if edit_nodes_form.validate_on_submit():
                type = monitor_controller.findTypeByName(edit_nodes_form.type.data)
                node = Node(
                    name=edit_nodes_form.name.data,
                    ip=edit_nodes_form.ip_address.data,
                    sector=edit_nodes_form.sector.data,
                    pvPrefix=edit_nodes_form.pv_prefix.data,
                    typeNode=type)
                monitor_controller.appendNode(node)
                flash('Successfully edited node {} !'.format(node), 'success')
                return redirect(url_for("view_nodes"))
        elif action == 'VALIDATE':
            pass

    if request.method == 'GET':
        print("GET {}".format(request.args))
        node_name = request.args.get('node_name', '')
        node = monitor_controller.getNode(node_name)
        if node:
            edit_nodes_form.set_initial_values(node)

    return render_template("node/edit_node.html", node=node, form=edit_nodes_form)


@app.route('/list_types/', methods=['POST'])
def list_types():
    types = monitor_controller.fetchTypes()
    return render_template("type/refresh_types.html", types=types)


@app.route("/view_types/", methods=['GET', 'POST'])
def view_types():
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'DELETE':
            type_name = request.form.get('type_name', '')
            if type_name == '':
                return 'Invalid type name'

            type_to_delete = monitor_controller.findTypeByName(type_name)
            if type_to_delete is not None:
                print('{}'.format(type_to_delete))
                monitor_controller.removeType(type_to_delete.name)
                return 'Type deleted'
            else:
                return 'Type not found'

    types = monitor_controller.fetchTypes()
    refresh_url = url_for('list_types')
    edit_url = url_for('edit_types')

    return render_template("type/view_types.html", edit_url=edit_url, refresh_url=refresh_url, types=types)


@app.route("/edit_types/", methods=['GET', 'POST'])
def edit_types(type=None):
    edit_types_form = EditTypeForm()

    if request.method == 'GET':
        type_name = request.args.get('type_name', '')
        if type_name is not '':
            type = monitor_controller.findTypeByName(type_name)
            edit_types_form.set_initial_values(type)

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'VALIDATE':

            rc_path = request.form.get('rcPath')
            git_url = request.form.get('gitUrl')

            success, message = monitor_controller.validateRepository(rc_path=rc_path, git_url=git_url)

            return jsonify(success=success, message=message)

        elif action == '':
            if edit_types_form.validate_on_submit():
                new_type = Type(
                    name=edit_types_form.name.data,
                    repoUrl=edit_types_form.repo_url.data,
                    rcLocalPath=edit_types_form.rc_local_path.data,
                    description=edit_types_form.description.data)
                monitor_controller.appendType(new_type)

                flash('Successfully edited type {} !'.format(new_type), 'success')
                return redirect(url_for("view_types"))
        else:
            return 'Invalid Command'

    return render_template("type/edit_type.html", type=type, form=edit_types_form, url=url_for('edit_types'))


def set_controller(c: MonitorController = None):
    global monitor_controller
    monitor_controller = c


def get_wsgi_app():
    return app


def start_webserver(port: int = 5000):
    app.run(debug=False, use_reloader=False, port=port, host="0.0.0.0")
