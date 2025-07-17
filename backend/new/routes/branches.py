from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from pydantic import BaseModel, ValidationError
from typing import List, Optional

branches_bp = Blueprint('branches', __name__)

class BranchModel(BaseModel):
    name: str
    address: str
    adminId: str
    menuId: str
    is_active: bool
    working_from: Optional[str] = ""
    working_to: Optional[str] = ""
    languages: List[str]

class LanguageModel(BaseModel):
    language: str

class LanguagesListModel(BaseModel):
    languages: List[str]

@branches_bp.route('', methods=['POST'])
def add_branch():
    db = current_app.config['DB']
    try:
        data = BranchModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    result = db.branches.insert_one(data.dict())
    return jsonify({"inserted_id": str(result.inserted_id)})

@branches_bp.route('', methods=['GET'])
def get_branches():
    db = current_app.config['DB']
    branches = list(db.branches.find())
    for b in branches:
        b['_id'] = str(b['_id'])
    return jsonify(branches)

@branches_bp.route('/<branch_id>', methods=['GET'])
def get_branch(branch_id):
    db = current_app.config['DB']
    branch = db.branches.find_one({"_id": ObjectId(branch_id)})
    if branch:
        branch['_id'] = str(branch['_id'])
        return jsonify(branch)
    return jsonify({"error": "Not found"}), 404

@branches_bp.route('/<branch_id>', methods=['PUT'])
def update_branch(branch_id):
    db = current_app.config['DB']
    try:
        data = BranchModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db.branches.update_one({"_id": ObjectId(branch_id)}, {"$set": data.model_dump()})
    return jsonify({"message": "Branch updated"})

@branches_bp.route('/<branch_id>', methods=['DELETE'])
def delete_branch(branch_id):
    db = current_app.config['DB']
    db.branches.delete_one({"_id": ObjectId(branch_id)})
    return jsonify({"message": "Branch deleted"})

@branches_bp.route('/<branch_id>/languages/add', methods=['PUT'])
def add_language(branch_id):
    db = current_app.config['DB']
    try:
        data = LanguageModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db.branches.update_one(
        {"_id": ObjectId(branch_id)},
        {"$addToSet": {"languages": data.language}}
    )
    return jsonify({"message": "Language added"})

@branches_bp.route('/<branch_id>/languages/remove', methods=['PUT'])
def remove_language(branch_id):
    db = current_app.config['DB']
    try:
        data = LanguageModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db.branches.update_one(
        {"_id": ObjectId(branch_id)},
        {"$pull": {"languages": data.language}}
    )
    return jsonify({"message": "Language removed"})

@branches_bp.route('/<branch_id>/languages/set', methods=['PUT'])
def set_languages(branch_id):
    db = current_app.config['DB']
    try:
        data = LanguagesListModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db.branches.update_one(
        {"_id": ObjectId(branch_id)},
        {"$set": {"languages": data.languages}}
    )
    return jsonify({"message": "Languages set"})
