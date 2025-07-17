from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId

branches_bp = Blueprint("branchesApi", __name__)

@branches_bp.route("", methods=["GET"])
def get_branches():
    db = current_app.config["DB"]
    restaurant_id = request.headers.get("X-Restaurant-Id")  # optional, for multi-tenant filtering
    query = {"restaurantId": restaurant_id} if restaurant_id else {}
    branches = list(db.branches.find(query))
    for b in branches:
        b["_id"] = str(b["_id"])
    return jsonify(branches)

@branches_bp.route("", methods=["POST"])
def create_branch():
    db = current_app.config["DB"]
    data = request.json
    if not data.get("name") or not data.get("address"):
        return jsonify({"error": "Missing name or address"}), 400
    branch = {
        "name": data["name"],
        "address": data["address"],
        "restaurantId": request.headers.get("X-Restaurant-Id")
    }
    result = db.branches.insert_one(branch)
    branch["_id"] = str(result.inserted_id)
    return jsonify(branch), 201

@branches_bp.route("/<branch_id>", methods=["PUT"])
def update_branch(branch_id):
    db = current_app.config["DB"]
    data = request.json
    if not data.get("name") or not data.get("address"):
        return jsonify({"error": "Missing name or address"}), 400
    db.branches.update_one(
        {"_id": ObjectId(branch_id)},
        {"$set": {"name": data["name"], "address": data["address"]}}
    )
    return jsonify({"message": "Branch updated"})

@branches_bp.route("/<branch_id>", methods=["DELETE"])
def delete_branch(branch_id):
    db = current_app.config["DB"]
    db.branches.delete_one({"_id": ObjectId(branch_id)})
    return jsonify({"message": "Branch deleted"})
