from flask import Blueprint, request, jsonify
from services.jwt_service import jwt_required
from services.wallet_service import WalletService

wallet_bp = Blueprint('wallet', __name__, url_prefix='/wallets')


# Tạo ví tiền mới
@wallet_bp.route('/create', methods=['POST'])
@jwt_required
def create_wallet(current_user):
    data = request.get_json()
    result = WalletService.create_wallet_service(int(current_user), data)

    # Nếu cần xác nhận khôi phục
    if result.get("restore_suggestion"):
        return jsonify(result), 409
    
    return jsonify(result), result.get('status_code', 200)
    

# Lấy danh sách ví tiền của user
@wallet_bp.route('/', methods=['GET'])
@jwt_required
def get_wallets(current_user):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)    
    result = WalletService.get_wallets_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy danh sách ví tiền đã xoá của user
@wallet_bp.route('/deleted', methods=['GET'])
@jwt_required
def get_deleted_wallets(current_user):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)    
    result = WalletService.get_deleted_wallets_service(int(current_user), page, per_page)
    return jsonify(result), result.get('status_code', 200)


# Lấy thông tin ví tiền
@wallet_bp.route('/<int:wallet_id>', methods=['GET'])
@jwt_required
def get_wallet(current_user, wallet_id):
    result = WalletService.get_wallet_service(int(current_user), wallet_id)
    return jsonify(result), result.get('status_code', 200)


# Cập nhật thông tin ví tiền
@wallet_bp.route('/update/<int:wallet_id>', methods=['PUT'])
@jwt_required
def update_wallet(current_user, wallet_id):
    data = request.get_json()
    result = WalletService.update_wallet_service(int(current_user), wallet_id, data)
    return jsonify(result), result.get('status_code', 200)
    

# Xoá ví tiền
@wallet_bp.route('/delete/<int:wallet_id>', methods=['DELETE'])
@jwt_required
def delete_wallet(current_user, wallet_id):
    result = WalletService.delete_wallet_service(int(current_user), wallet_id)
    return jsonify(result), result.get('status_code', 200)


# Kiểm tra số dư
@wallet_bp.route('/<int:wallet_id>/balance', methods=['GET'])
@jwt_required
def get_wallet_balance(current_user, wallet_id):
    result = WalletService.get_balance_service(int(current_user), wallet_id)
    return jsonify(result), result.get('status_code', 200)


# Xoá tạm thời
@wallet_bp.route('/soft_delete/<int:wallet_id>', methods=['PATCH'])
@jwt_required
def soft_delete_wallet(current_user, wallet_id):
    result = WalletService.soft_delete_wallet_service(int(current_user), wallet_id)
    return jsonify(result), result.get('status_code', 200)


# Khôi phục ví tiền
@wallet_bp.route('/restore/<int:wallet_id>', methods=['PATCH'])
@jwt_required
def restore_wallet(current_user, wallet_id):
    result = WalletService.restore_wallet_service(int(current_user), wallet_id)
    return jsonify(result), result.get('status_code', 200)