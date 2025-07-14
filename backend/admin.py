import hashlib
import html
import random
import uuid
from bs4 import BeautifulSoup
from bson import ObjectId
from flask import Flask, abort, json, request, jsonify, send_from_directory
from flask_cors import CORS
import jwt
from pymongo import MongoClient
import traceback
import os
import requests
import boto3
from botocore.client import Config
from datetime import datetime, timedelta

from werkzeug.utils import secure_filename

from html import unescape
# import csv
from functools import wraps
import re

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, origins=["http://localhost:3001"])

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# MongoDB setup (use your own credentials or environment variables)
MONGO_URI = 'mongodb+srv://atergrid:Ag0384802@cluster0.sbou2sr.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client['menu']
tabs_collection = db['menuTabs']
admin_collection = db['admins']
items_collection = db['items']
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB
# --- Telegram Bot Integration ---
# Replace with your actual Telegram Bot Token
# TELEGRAM_BOT_TOKEN = '8053579909:AAH85DDtqdUgm-f5motmn872jhwH7chLtDM'
# TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

def sanitize_name(name):
    return re.sub(r'[^a-z0-9_-]', '', name.lower().replace(" ", "-"))

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/api/menu-tabs", methods=["GET"])
def get_menu_tabs():
    doc = tabs_collection.find_one({}, {"_id": 0})  # exclude _id

    print("Returning menu tabs:", doc)
    return jsonify(doc or {"AM": [], "RU": []})
# === POST new tab structure ===

@app.route("/api/menu-tabs", methods=["POST"])
def update_tabs_collection():
    try:
        data = request.get_json(force=True)

        # Save the data
        tabs_collection.delete_many({})
        result = tabs_collection.insert_one(data)

        # Append the inserted _id if you want
        return jsonify({"success": True, "_id": str(result.inserted_id)})

    except Exception as e:
        print("Error in /api/menu-tabs:", e)
        return jsonify({"error": str(e)}), 500
# === GET menu items for a tab ===
@app.route("/api/menu-items", methods=["GET"])
def get_menu_items():
    tab_id = request.args.get("tab")
    items = list(items_collection.find({"tabId": tab_id}))
    for item in items:
        item["_id"] = str(item["_id"])
    return jsonify(items)


def mongo_converter(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc
import os

@app.route("/api/menu-items", methods=["POST"])
def create_menu_item():
    tab_id = request.form.get("tabId")
    titleAM = request.form.get("titleAM")
    titleRU = request.form.get("titleRU")
    AM = request.form.get("AM")
    RU = request.form.get("RU")
    price = request.form.get("price")
    image_file = request.files.get("image")

    if not all([tab_id, titleAM, titleRU, AM, RU, price, image_file]):
        return jsonify({ "error": "Missing fields" }), 400

    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join("./static/uploads/menu", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image_file.save(path)

    new_item = {
        "tabId": tab_id,
        "title": { "AM": titleAM, "RU": titleRU },
        "description": { "AM": AM, "RU": RU },
        "price": price,
        "photoUrl": f"/static/uploads/menu/{filename}"
    }

    result = items_collection.insert_one(new_item)
    new_item["_id"] = str(result.inserted_id)
    return jsonify(new_item), 201

@app.route("/api/menu-items", methods=["PUT"])
def update_menu_item():
    item_id = request.form.get("itemId")
    titleAM = request.form.get("titleAM")
    titleRU = request.form.get("titleRU")
    AM = request.form.get("AM")
    RU = request.form.get("RU")
    price = request.form.get("price")
    image_file = request.files.get("image")

    if not item_id:
        return jsonify({ "error": "Missing item _id" }), 400

    update_data = {
        "title": { "AM": titleAM, "RU": titleRU },
        "description": { "AM": AM, "RU": RU },
        "price": price
    }

    if image_file:
        # Ensure directory exists
        upload_dir = "./static/uploads/menu"
        os.makedirs(upload_dir, exist_ok=True)

        # Save new image
        filename = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(upload_dir, filename)
        image_file.save(image_path)

        # Store URL path
        update_data["photoUrl"] = f"/static/uploads/menu/{filename}"

    result = items_collection.update_one(
        { "_id": ObjectId(item_id) },
        { "$set": update_data }
    )

    if result.modified_count == 1:
        return jsonify({ "success": True })
    else:
        return jsonify({ "error": "Item not updated" }), 500


@app.route("/api/menu-items/<item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    result = items_collection.delete_one({ "_id": ObjectId(item_id) })
    if result.deleted_count:
        return jsonify({ "status": "deleted" })
    else:
        return jsonify({ "error": "Item not found" }), 404

JWT_SECRET='9d8f74a2efb06f94a80e23dfb9c2f68c5b54f74cb519fc3ab9d4510d3787be98'
# LOGIN part
@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    code = data.get("code")
    login = data.get("login")

    admin = admin_collection.find_one({
        "$or": [
            {"telegram_id": login},
            {"username": login}
        ],
        "login_code": code
    })

    if not admin or admin.get("code_expires_at") < datetime.utcnow():
        return jsonify({"success": False, "message": "Invalid or expired code"}), 401

    token = jwt.encode({
        "sub": str(admin["_id"]),
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, JWT_SECRET, algorithm="HS256")

    # Optionally clear code
    admin_collection.update_one({"_id": admin["_id"]}, {"$unset": {"login_code": "", "code_expires_at": ""}})

    return jsonify({"success": True, "token": token})


@app.route('/request-login', methods=['POST'])
def request_login():
    data = request.json
    username_or_id = data.get("login")

    admin = admin_collection.find_one({
        "$or": [
            {"telegram_id": username_or_id},
            {"username": username_or_id}
        ]
    })

    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404

    code = str(random.randint(100000, 999999))
    admin_collection.update_one({"_id": admin["_id"]}, {"$set": {"login_code": code, "code_expires_at": datetime.utcnow() + timedelta(minutes=5)}})

    # send via Telegram bot
    send_telegram_message(admin["telegram_id"], f"🔐 Ваш код входа: {code}")

    return jsonify({"success": True})

BOT_TOKEN = "8053579909:AAH85DDtqdUgm-f5motmn872jhwH7chLtDM"

def send_telegram_message(telegram_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": telegram_id,
        "text": message
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            print(f"❌ Failed to send message: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Telegram send error: {e}")


# Settings part

# Decode and extract current admin
def get_current_admin(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        admin = admin_collection.find_one({"_id": ObjectId(payload["sub"])})
        return admin
    except:
        return None

# Middleware to protect routes
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        admin = get_current_admin(token)
        if not admin:
            return jsonify({"error": "Unauthorized"}), 401
        request.admin = admin
        return f(*args, **kwargs)
    return wrapper

# Superadmin-only guard
def require_superadmin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.admin.get("role") != "superadmin":
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return wrapper

# Get all admins
@app.route('/admins', methods=['GET'])
@require_auth
def get_admins():
    admins = list(admin_collection.find({}, {"login_code": 0}))
    for a in admins:
        a["_id"] = str(a["_id"])
    return jsonify({
        "admins": admins,
        "currentUserRole": request.admin.get("role")
    })

# Add admin
@app.route('/admins', methods=['POST'])
@require_auth
@require_superadmin
def add_admin():
    data = request.json
    if not data.get("telegram_id") or not data.get("username"):
        return jsonify({"error": "Missing fields"}), 400
    admin_collection.insert_one({
        "telegram_id": data["telegram_id"],
        "username": data["username"],
        "role": data.get("role", "admin"),
        "created_at": datetime.utcnow()
    })
    return jsonify({"success": True})

# Update admin
@app.route('/admins/<admin_id>', methods=['PUT'])
@require_auth
@require_superadmin
def update_admin(admin_id):
    data = request.json
    admin_collection.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": {"role": data["role"]}}
    )
    return jsonify({"success": True})

# Delete admin
@app.route('/admins/<admin_id>', methods=['DELETE'])
@require_auth
@require_superadmin
def delete_admin(admin_id):
    admin_collection.delete_one({"_id": ObjectId(admin_id)})
    return jsonify({"success": True})
    
if __name__ == '__main__':
    # Ensure the uploads directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True) # Set debug=True for development