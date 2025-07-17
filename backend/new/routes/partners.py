from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from pydantic import BaseModel, ValidationError
from typing import List

partners_bp = Blueprint('partners', __name__)

class PartnerModel(BaseModel):
    name: str
    branchIds: List[str]

@partners_bp.route('', methods=['POST'])
def add_partner():
    db = current_app.config['DB']
    try:
        data = PartnerModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    result = db.partners.insert_one(data.model_dump())
    return jsonify({"inserted_id": str(result.inserted_id)})

@partners_bp.route('', methods=['GET'])
def get_partners():
    db = current_app.config['DB']
    partners = list(db.partners.find())
    for p in partners:
        p['_id'] = str(p['_id'])
    return jsonify(partners)

@partners_bp.route('/<partner_id>', methods=['GET'])
def get_partner(partner_id):
    db = current_app.config['DB']
    partner = db.partners.find_one({"_id": ObjectId(partner_id)})
    if partner:
        partner['_id'] = str(partner['_id'])
        return jsonify(partner)
    return jsonify({"error": "Not found"}), 404

@partners_bp.route('/<partner_id>', methods=['PUT'])
def update_partner(partner_id):
    db = current_app.config['DB']
    try:
        data = PartnerModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db.partners.update_one({"_id": ObjectId(partner_id)}, {"$set": data.model_dump()})
    return jsonify({"message": "Partner updated"})

@partners_bp.route('/<partner_id>', methods=['DELETE'])
def delete_partner(partner_id):
    db = current_app.config['DB']
    db.partners.delete_one({"_id": ObjectId(partner_id)})
    return jsonify({"message": "Partner deleted"})
