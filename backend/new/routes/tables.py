from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from pydantic import BaseModel, ValidationError
from typing import Optional

tables_bp = Blueprint('tables', __name__)

class TableModel(BaseModel):
    branchId: str
    partnerId: str
    capacity: int
    assigned_waiter: Optional[str] = ""
    is_booked: bool = False
    is_busy: bool = False
    is_active: bool = True
    is_calling: bool = False

@tables_bp.route('', methods=['POST'])
def add_table():
    db = current_app.config['DB']
    try:
        data = TableModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    result = db.tables.insert_one(data.model_dump())
    return jsonify({"inserted_id": str(result.inserted_id)})

@tables_bp.route('/<table_id>', methods=['GET'])
def get_table(table_id):
    db = current_app.config['DB']
    table = db.tables.find_one({"_id": ObjectId(table_id)})
    if table:
        table['_id'] = str(table['_id'])
        return jsonify(table)
    return jsonify({"error": "Not found"}), 404

@tables_bp.route('/<table_id>', methods=['PUT'])
def update_table(table_id):
    db = current_app.config['DB']
    try:
        data = TableModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db.tables.update_one({"_id": ObjectId(table_id)}, {"$set": data.model_dump()})
    return jsonify({"message": "Table updated"})

@tables_bp.route('/<table_id>', methods=['DELETE'])
def delete_table(table_id):
    db = current_app.config['DB']
    db.tables.delete_one({"_id": ObjectId(table_id)})
    return jsonify({"message": "Table deleted"})
