from flask import Blueprint, request, jsonify
from services.jwt_service import jwt_required
from services.category_service import CategoryService


category_bp = Blueprint('category', __name__, url_prefix='/categories')

# Tạo danh mục mới
@category_bp.route('/create', methods=['POST'])
@jwt_required
def create_category(current_user):
    data = request.get_json()
    result = CategoryService.create_category_service(int(current_user), data)
    return jsonify(result), result.get('status_code', 200)
    

# Lấy danh sách danh mục của user
@category_bp.route('/', methods=['GET'])
@jwt_required
def get_categories(current_user):    
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = CategoryService.get_categories_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy danh sách danh mục đã xoá của user
@category_bp.route('/deleted', methods=['GET'])
@jwt_required
def get_deleted_categories(current_user):    
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = CategoryService.get_deleted_categories_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy thông tin danh mục
@category_bp.route('/<int:category_id>', methods=['GET'])
@jwt_required
def get_category(current_user, category_id):
    result = CategoryService.get_category_service(int(current_user), category_id)
    return jsonify(result), result.get('status_code', 200)


# Cập nhật danh mục
@category_bp.route('/update/<int:category_id>', methods=['PUT'])
@jwt_required
def update_category(current_user, category_id):
    data = request.get_json()
    result = CategoryService.update_category_service(int(current_user), category_id, data)
    return jsonify(result), result.get('status_code', 200)
        

# Xoá danh mục
@category_bp.route('/delete/<int:category_id>', methods=['DELETE'])
@jwt_required
def delete_category(current_user, category_id):
    result = CategoryService.delete_category_service(int(current_user), category_id)
    return jsonify(result), result.get('status_code', 200)
    
    
# Xoá tạm thời
@category_bp.route('/soft_delete/<int:category_id>', methods=['PATCH'])
@jwt_required
def soft_delete_category(current_user, category_id):
    result = CategoryService.soft_delete_category_service(int(current_user), category_id)
    return jsonify(result), result.get('status_code', 200)


# Khôi phục
@category_bp.route('/restore/<int:category_id>', methods=['PATCH'])
@jwt_required
def restore_category(current_user, category_id):
    result = CategoryService.restore_category_service(int(current_user), category_id)
    return jsonify(result), result.get('status_code', 200)