from functools import wraps
from flask import jsonify, request
from utils.jwt_utils import decode_jwt_from_request

def jwt_required_and_partner_check(get_partner_id_from_path=True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            decoded = decode_jwt_from_request()
            if not decoded:
                return jsonify({ "error": "Unauthorized" }), 401

            role = decoded.get("role")
            if role not in ["partner", "admin"]:
                return jsonify({ "error": "Forbidden role" }), 403

            if get_partner_id_from_path:
                partner_id = kwargs.get("partner_id")
                if decoded.get("restaurantId") != partner_id and role != "admin":
                    return jsonify({ "error": "Forbidden" }), 403

            request.user = decoded  # attach user info
            return f(*args, **kwargs)
        return wrapper
    return decorator
