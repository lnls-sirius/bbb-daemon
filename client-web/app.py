from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from entity.entities import Node, Type

from forms import EditNodeForm, EditTypeForm

nodes = []
types = []
for i in range(10):
    nodes.append(Node())
    types.append(Type())

app = Flask("client-web")
app.secret_key = "4dbae3052d7e8b16ebcfe8752f70a4efe68d2ae0558b4a1b25c5fd902284e52e"

Bootstrap(app)
nav = Nav(app)

nav.register_element('my_navbar', Navbar('Navigation Bar',
                                         View('Home', 'home'),
                                         View('Nodes', 'edit_nodes'),
                                         View('Types', 'edit_types')))


@app.route("/nodes/", methods=['GET', 'POST'])
def edit_nodes():
    edit_nodes_form = EditNodeForm(obj=types)
    edit_nodes_form.type.choices = [(t.name, f"{t.name}\t{t.repoUrl}") for t in types]

    if edit_nodes_form.validate_on_submit():
        flash(f"Successfully edited node {edit_nodes_form.ip_address.data} {edit_nodes_form.name.data}!", "success")
        return redirect(url_for("home"))

    return render_template("edit_node.html", node=None, form=edit_nodes_form)


@app.route("/")
@app.route("/home/", methods=['GET', 'POST'])
def home():
    return render_template("index.html", nodes=nodes)


@app.route("/types/", methods=['GET', 'POST'])
def edit_types():
    edit_types_form = EditTypeForm()
    return render_template("edit_type.html", type=None, form=edit_types_form)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
