from flask import Flask, jsonify, request
from routes.partners import partners_bp
from routes.branches import branches_bp
from routes.menus import menus_bp
from routes.items import items_bp
from routes.tables import tables_bp
from pymongo import MongoClient
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
#TODO fix with env
CORS(app, origins=["https://kfc.ater-vpn.ru"])
CORS(app, origins=["https://kfc-menu.ater-vpn.ru"])
CORS(app, origins=["http://localhost:3000"])

# MongoDB setup

client = MongoClient("mongodb+srv://atergrid:Ag0384802@cluster0.sbou2sr.mongodb.net/?retryWrites=true&w=majority")

db = client["menu"]
partners_collection = db["partners"]
app.config['DB'] = db
# Register Blueprints
app.register_blueprint(partners_bp, url_prefix='/partners')
app.register_blueprint(branches_bp, url_prefix='/branches')
app.register_blueprint(menus_bp, url_prefix='/menus')
app.register_blueprint(items_bp, url_prefix='/items')
app.register_blueprint(tables_bp, url_prefix='/tables')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)


