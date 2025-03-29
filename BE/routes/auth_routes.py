from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Đăng ký
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result = AuthService.user_register(data)
    return jsonify(result), result.get('status_code', 200)


# Đăng nhập
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result = AuthService.user_login(data)
    return jsonify(result), result.get('status_code', 200)
