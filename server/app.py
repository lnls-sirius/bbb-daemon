#!/usr/bin/python3
import logging

from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, json
from flask_restful import Api
from flask_cors import CORS

from common.entity.entities import Sector, Type, Node, NodeState  
from server.network.db import DataNotFoundError 
from server.restful.resources import Nodes,Node as rNode, Types, Sectors

logger = logging.getLogger()

app = Flask(__name__)
app.secret_key = "4dbae3052d7e8b16ebcfe8752f70a4efe68d2ae0558b4a1b25c5fd902284e52e"
cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

api.add_resource(Nodes, '/nodes')
api.add_resource(rNode, '/node/<command>')
api.add_resource(Types, '/types')
api.add_resource(Sectors, '/sectors') 

def start_webserver(port):
    app.run(debug=False, use_reloader=False, port=port, host="0.0.0.0")

application = app
