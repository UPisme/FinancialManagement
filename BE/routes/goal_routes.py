from flask import Blueprint, request, jsonify
from services.jwt_service import jwt_required
from services.goal_service import GoalService

goal_bp = Blueprint('goal', __name__, url_prefix='/goals')


# Tạo mục tiêu mới
@goal_bp.route('/create', methods=['POST'])
@jwt_required
def create_goal(current_user):
    data = request.get_json()
    result = GoalService.create_goal_service(int(current_user), data)

    # Nếu cần xác nhận khôi phục
    if result.get("restore_suggestion"):
        return jsonify(result), 409
    
    return jsonify(result), result.get('status_code', 200)
    
    
# Lấy danh sách mục tiêu
@goal_bp.route('/', methods=['GET'])
@jwt_required
def get_goals(current_user):  
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)  
    result = GoalService.get_goals_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy danh sách mục tiêu đã xoá
@goal_bp.route('/deleted', methods=['GET'])
@jwt_required
def get_deleted_goals(current_user):  
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)  
    result = GoalService.get_deleted_goals_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy thông tin mục tiêu
@goal_bp.route('/<int:goal_id>', methods=['GET'])
@jwt_required
def get_goal(current_user, goal_id):
    result = GoalService.get_goal_service(int(current_user), goal_id)
    return jsonify(result), result.get('status_code', 200)


# Cập nhật thông tin mục tiêu
@goal_bp.route('/update/<int:goal_id>', methods=['PUT'])
@jwt_required
def update_goal(current_user, goal_id):
    data = request.get_json()
    result = GoalService.update_goal_service(int(current_user), goal_id, data)
    return jsonify(result), result.get('status_code', 200)
    

# Xoá mục tiêu
@goal_bp.route('/delete/<int:goal_id>', methods=['DELETE'])
@jwt_required
def delete_goal(current_user, goal_id):
    result = GoalService.delete_goal_service(int(current_user), goal_id)
    return jsonify(result), result.get('status_code', 200)


# Trạng thái mục tiêu
@goal_bp.route('/status/<int:goal_id>', methods=['GET'])
@jwt_required
def goal_status(current_user, goal_id):
    result = GoalService.get_goal_status_service(int(current_user), goal_id)
    return jsonify(result), result.get('status_code', 200)


# Xoá tạm thời
@goal_bp.route('/soft_delete/<int:goal_id>', methods=['PATCH'])
@jwt_required
def soft_delete_goal(current_user, goal_id):
    result = GoalService.soft_delete_goal_service(int(current_user), goal_id)
    return jsonify(result), result.get('status_code', 200)


# Khôi phục
@goal_bp.route('/restore/<int:goal_id>', methods=['PATCH'])
@jwt_required
def restore_goal(current_user, goal_id):
    result = GoalService.restore_goal_service(int(current_user), goal_id)
    return jsonify(result), result.get('status_code', 200)