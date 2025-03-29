from flask import Blueprint, request, jsonify
from services.jwt_service import jwt_required
from services.budget_service import BudgetService


budget_bp = Blueprint('budget', __name__, url_prefix='/budgets')


# Tạo ngân sách mới
@budget_bp.route('/create', methods=['POST'])
@jwt_required
def create_budget(current_user):
    data = request.get_json()
    result = BudgetService.create_budget_service(int(current_user), data)

    # Nếu cần xác nhận khôi phục
    if result.get("restore_suggestion"):
        return jsonify(result), 409
    
    return jsonify(result), result.get('status_code', 200)


# Lấy danh sách ngân sách
@budget_bp.route('/', methods=['GET'])
@jwt_required
def get_budgets(current_user):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = BudgetService.get_budgets_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy danh sách ngân sách đã xoá
@budget_bp.route('/deleted', methods=['GET'])
@jwt_required
def get_deleted_budgets(current_user):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = BudgetService.get_deleted_budgets_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy thông tin ngân sách
@budget_bp.route('/<int:budget_id>', methods=['GET'])
@jwt_required
def get_budget(current_user, budget_id):
    result = BudgetService.get_budget_service(int(current_user), budget_id)
    return jsonify(result), result.get('status_code', 200)


# Cập nhật ngân sách
@budget_bp.route('/update/<int:budget_id>', methods=['PUT'])
@jwt_required
def update_budget(current_user, budget_id):
    data = request.get_json()
    result = BudgetService.update_budget_service(int(current_user), budget_id, data)
    return jsonify(result), result.get('status_code', 200)


# Xoá ngân sách
@budget_bp.route('/delete/<int:budget_id>', methods=['DELETE'])
@jwt_required
def delete_budget(current_user, budget_id):
    result = BudgetService.delete_budget_service(int(current_user), budget_id)
    return jsonify(result), result.get('status_code', 200)


# Xoá ngân sách tạm thời 
@budget_bp.route('/soft_delete/<int:budget_id>', methods=['PATCH'])
@jwt_required
def soft_delete_budget(current_user, budget_id):
    result = BudgetService.soft_delete_budget_service(int(current_user), budget_id)
    return jsonify(result), result.get('status_code', 200)


# Khôi phục ngân sách
@budget_bp.route('/restore/<int:budget_id>', methods=['PATCH'])
@jwt_required
def restore_budget(current_user, budget_id):
    result = BudgetService.restore_budget_service(int(current_user), budget_id)
    return jsonify(result), result.get('status_code', 200)