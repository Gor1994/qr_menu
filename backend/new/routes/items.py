import os
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from pydantic import BaseModel, ValidationError, HttpUrl
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename


items_bp = Blueprint('items', __name__)

class ItemModel(BaseModel):
    tabId: str
    branchId: str
    name: str
    image: str
    title: Dict[str, str]
    description: Dict[str, str]
    price: float
    currencies: Dict[str, str]
    discount: Optional[float] = 0
    discount_available_from: Optional[str] = ""
    discount_available_to: Optional[str] = ""
    is_active: bool = True
    available_from: Optional[str] = ""
    available_to: Optional[str] = ""


@items_bp.route('', methods=['POST'])
def add_item():
    db = current_app.config['DB']
    tab_id = request.form.get("tabId")
    branch_id = request.form.get("branchId")
    price = request.form.get("price")
    title = {"AM": request.form.get("titleAM"), "RU": request.form.get("titleRU")}
    description = {"AM": request.form.get("AM"), "RU": request.form.get("RU")}
    image = request.files.get("image")

    if not all([tab_id, branch_id, price, title["AM"], title["RU"], description["AM"], description["RU"], image]):
        return jsonify({"error": "Missing required fields"}), 400

    # ✅ Ensure folder exists
    upload_folder = ("images")

    # ✅ Save image
    image_path = os.path.join(upload_folder, image.filename)
    image.save(image_path)

    item = {
        "tabId": tab_id,
        "branchId": branch_id,
        "price": float(price),
        "title": title,
        "description": description,
        "photoUrl": f"images/{image.filename}"
    }

    result = db.menu_items.insert_one(item)
    item["_id"] = str(result.inserted_id)
    return jsonify(item), 201

@items_bp.route('/<item_id>', methods=['GET'])
def get_item(item_id):
    db = current_app.config['DB']
    item = db.menu_items.find_one({"_id": ObjectId(item_id)})
    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item)
    return jsonify({"error": "Not found"}), 404

@items_bp.route('', methods=['GET'])
def list_items():
    db = current_app.config['DB']
    tab = request.args.get("tab")
    branch_id = request.args.get("branchId")
    if not tab or not branch_id:
        return jsonify({"error": "Missing tab or branchId"}), 400

    items = list(db.menu_items.find({"tabId": tab, "branchId": branch_id}))
    for item in items:
        item["_id"] = str(item["_id"])
    return jsonify(items)


@items_bp.route('/<item_id>', methods=['PUT'])
def update_item(item_id):
    db = current_app.config['DB']

    # Extract fields
    tab_id = request.form.get("tabId")
    branch_id = request.form.get("branchId")
    name = request.form.get("name")
    title = {
        "AM": request.form.get("titleAM"),
        "RU": request.form.get("titleRU")
    }
    description = {
        "AM": request.form.get("AM"),
        "RU": request.form.get("RU")
    }
    price = float(request.form.get("price") or 0)
    image_url = request.form.get("image")  # fallback from frontend

    # Handle new image upload
    image_file = request.files.get("image")
    if image_file:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join("images", filename)
        image_file.save(image_path)
        image_url = f"images/{filename}"

    full_url = f"https://kfc.ater-vpn.ru/{image_url}" if image_url else ""

    update_data = {
        "tabId": tab_id,
        "branchId": branch_id,
        "name": name,
        "image": full_url,
        "photoUrl": image_url,  # relative path for internal use
        "title": title,
        "description": description,
        "price": price,
        "currencies": { "AMD": "֏" },
        "discount": 0,
        "discount_available_from": "",
        "discount_available_to": "",
        "is_active": True,
        "available_from": "",
        "available_to": ""
    }

    db.menu_items.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
    return jsonify({ "_id": item_id, **update_data })

@items_bp.route('/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    db = current_app.config['DB']
    db.menu_items.delete_one({"_id": ObjectId(item_id)})
    return jsonify({"message": "Item deleted"})
