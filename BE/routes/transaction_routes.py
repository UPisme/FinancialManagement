from flask import Blueprint, request, jsonify
from services.jwt_service import jwt_required
from services.transaction_service import TransactionService


transaction_bp = Blueprint('transaction', __name__, url_prefix='/transactions')

# Tạo giao dịch mới
@transaction_bp.route('/create', methods=['POST'])
@jwt_required
def create_transaction(current_user):
    data = request.get_json()
    result = TransactionService.create_transaction_service(int(current_user), data)

    # Kiểm tra nếu yêu cầu xác nhận từ frontend
    if result.get('requires_confirmation'):
        return jsonify(result), 200  # Yêu cầu xác nhận với trạng thái 200
    
    return jsonify(result), result.get('status_code', 200)
    

# Lấy danh sách giao dịch
@transaction_bp.route('/', methods=['GET'])
@jwt_required
def get_transactions(current_user):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = TransactionService.get_transactions_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy danh sách giao dịch đã xoá
@transaction_bp.route('/deleted', methods=['GET'])
@jwt_required
def get_deleted_transactions(current_user):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = TransactionService.get_deleted_transactions_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy thông tin giao dịch
@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required
def get_transaction(current_user, transaction_id):
    result = TransactionService.get_transaction_service(int(current_user), transaction_id)
    return jsonify(result), result.get('status_code', 200)


# Cập nhật thông tin giao dịch
@transaction_bp.route('/update/<int:transaction_id>', methods=['PUT'])
@jwt_required
def update_transaction(current_user, transaction_id):
    data = request.get_json()
    result = TransactionService.update_transaction_service(int(current_user), transaction_id, data)
    return jsonify(result), result.get('status_code', 200)
    

# Xoá giao dịch vĩnh viễn
@transaction_bp.route('/delete/<int:transaction_id>', methods=['DELETE'])
@jwt_required
def delete_transaction(current_user, transaction_id):
    result = TransactionService.delete_transaction_service(int(current_user), transaction_id)
    return jsonify(result), result.get('status_code', 200)


# Xoá giao dịch tạm thời
@transaction_bp.route('/soft_delete/<int:transaction_id>', methods=['PATCH'])
@jwt_required
def soft_delete_transaction(current_user, transaction_id):
    result = TransactionService.soft_delete_transaction_service(int(current_user), transaction_id)
    return jsonify(result), result.get('status_code', 200)


# Khôi phục giao dịch
@transaction_bp.route('/restore/<int:transaction_id>', methods=['PATCH'])
@jwt_required
def restore_transaction(current_user, transaction_id):
    result = TransactionService.restore_transaction_service(int(current_user), transaction_id)
    return jsonify(result), result.get('status_code', 200)