from flask import Blueprint, jsonify, request
from services.jwt_service import jwt_required
from services.user_service import UserService

user_bp = Blueprint('users', __name__, url_prefix='/users')


# # Lấy danh sách user
# @user_bp.route('/', methods=['GET'])
# @jwt_required
# def get_users():
#     result = UserService.get_users_service()
#     return jsonify(result), result.get('status_code', 200)


# Lấy thông tin user
@user_bp.route('/me', methods=['GET'])
@jwt_required
def get_profile(current_user):
    result = UserService.get_profile_service(int(current_user))
    return jsonify(result), result.get('status_code', 200)


# Cập nhật thông tin user
@user_bp.route('/update', methods=['PUT'])
@jwt_required
def update_user(current_user):
    data = request.get_json()
    result = UserService.update_user_service(int(current_user), data)
    return jsonify(result), result.get('status_code', 200)
    

# Xoá user vĩnh viễn
@user_bp.route('/delete', methods=['DELETE'])
@jwt_required
def delete_user(current_user):
    result = UserService.delete_user_service(int(current_user))
    return jsonify(result), result.get('status_code', 200)


# Xoá user tạm thời
@user_bp.route('/soft_delete', methods=['PATCH'])
@jwt_required
def soft_delete_user(current_user):
    result = UserService.soft_delete_category_service(int(current_user))
    return jsonify(result), result.get('status_code', 200)