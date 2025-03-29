from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()  # Lấy user_id từ token
        except:
            return jsonify({'message': 'Token is invalid or missing'}), 401
        return f(current_user, *args, **kwargs)
    return decorated_function
