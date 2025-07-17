from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from pydantic import BaseModel, ValidationError
from typing import List

menus_bp = Blueprint('menus', __name__)

# Models
class CategoryModel(BaseModel):
    id: str
    name: str
    itemIds: List[str]

class MenuModel(BaseModel):
    name: str
    categories: List[CategoryModel]

# Create or update menu tabs for a branch
@menus_bp.route('/menu-tabs', methods=['POST'])
def save_menu_tabs():
    """
    Pushes new menu tabs to an existing branch-specific document.
    Accepts JSON: { "branchId": "123", "AM": [...], "RU": [...] }
    """
    db = current_app.config['DB']
    data = request.get_json()

    branch_id = data.get("branchId")
    am_tabs = data.get("AM", [])
    ru_tabs = data.get("RU", [])

    if not branch_id or not isinstance(am_tabs, list) or not isinstance(ru_tabs, list):
        return jsonify({"error": "Invalid data structure"}), 400

    existing = db.menu_tabs.find_one({"branchId": branch_id})
    if existing:
        db.menu_tabs.update_one(
            {"branchId": branch_id},
            {
                "$addToSet": {
                    "AM": {"$each": am_tabs},
                    "RU": {"$each": ru_tabs}
                }
            }
        )
        return jsonify({"message": "Tabs updated"})
    else:
        result = db.menu_tabs.insert_one({
            "branchId": branch_id,
            "AM": am_tabs,
            "RU": ru_tabs
        })
        return jsonify({"message": "Tabs created", "inserted_id": str(result.inserted_id)})

# Get menu tabs for a branch
@menus_bp.route('/menu-tabs', methods=['GET'])
def get_menu_tabs():
    """
    Returns tabs for a specific branchId
    Example: /menu-tabs?branchId=123
    """
    db = current_app.config['DB']
    branch_id = request.args.get("branchId")
    if not branch_id:
        return jsonify({"error": "Missing branchId"}), 400

    tabs = db.menu_tabs.find_one({"branchId": branch_id})
    if tabs:
        tabs['_id'] = str(tabs['_id'])
    return jsonify(tabs or {})

# Get full menu by ID
@menus_bp.route('/menu/<menu_id>', methods=['GET'])
def get_menu(menu_id):
    db = current_app.config['DB']
    try:
        menu = db.menus.find_one({"_id": ObjectId(menu_id)})
        if menu:
            menu['_id'] = str(menu['_id'])
            return jsonify(menu)
    except Exception:
        pass
    return jsonify({"error": "Not found"}), 404

# Update a menu by ID
@menus_bp.route('/menu/<menu_id>', methods=['PUT'])
def update_menu(menu_id):
    db = current_app.config['DB']
    try:
        data = MenuModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    try:
        db.menus.update_one({"_id": ObjectId(menu_id)}, {"$set": data.model_dump()})
        return jsonify({"message": "Menu updated"})
    except Exception:
        return jsonify({"error": "Invalid menu ID"}), 400

# Delete a menu by ID
@menus_bp.route('/menu/<menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    db = current_app.config['DB']
    try:
        db.menus.delete_one({"_id": ObjectId(menu_id)})
        return jsonify({"message": "Menu deleted"})
    except Exception:
        return jsonify({"error": "Invalid menu ID"}), 400
