from extensions import db
from models import Wallet, Transaction
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WalletService:
    # Kiểm tra sự tồn tại
    def existence_check(model, model_id, user_id, is_deleted=None):
        query = model.query.filter_by(id=model_id, user_id=user_id)
        if is_deleted is not None:  # Kiểm tra trạng thái is_deleted nếu được chỉ định
            query = query.filter_by(is_deleted=is_deleted)
        instance = query.first()
        return instance

    
    
    # Tạo wallet mới
    def create_wallet_service(user_id, data, force_create=False):
        logger.info(f'Creating wallet for user ID {user_id}')

        try:
            # Kiểm tra các trường bắt buộc
            if not data or not data.get('name'):
                logger.warning(f'Missing required fields')
                return {'message': 'Wallet name is required', 'status_code': 400}
            
            # Kiểm tra trùng tên ví
            existing_wallet = Wallet.query.filter_by(user_id=user_id, name=data['name'], is_deleted=False).first()
            if existing_wallet:
                logger.warning(f'Wallet name {data["name"]} already exists')
                return {'message': 'Wallet name already exists', 'status_code': 409}
            
            # Kiểm tra currency hợp lệ
            valid_currencies = ['VND', 'USD', 'CNY', 'KRW']
            if 'currency' in data and data['currency'] not in valid_currencies:
                logger.warning(f'Invalid currency')
                return {'message': 'Invalid currency', 'status_code': 400}
            
            # Kiểm tra các ví đã soft delete
            deleted_wallet = Wallet.query.filter_by(user_id=user_id, name=data['name'], is_deleted=True).first()

            if deleted_wallet and not force_create:
                logger.info(f'Wallet "{data["name"]}" was soft deleted, asking user for restore')
                return {
                    'message': 'Wallet previously deleted. Do you want to restore it?',
                    'status_code': 409,  # Conflict
                    'restore_suggestion': True,
                    'wallet_id': deleted_wallet.id
                }

            # Tạo wallet
            new_wallet = Wallet (
                user_id = user_id,
                name = data['name'],
                balance = data.get('balance', 0),
                currency = data.get('currency', 'VND'),
                is_deleted = False,
                deleted_at = None
            )

            # Thêm dữ liệu vào db
            db.session.add(new_wallet)
            db.session.commit()
            
            # Trả về kết quả
            logger.info(f'Wallet created successfully for user ID {user_id}')
            return {
                'message': 'Wallet created successfully',
                'wallet': {
                    'name': new_wallet.name,
                    'balance': float(new_wallet.balance),
                    'currency': new_wallet.currency
                },
                'status_code': 201
            }
        
        except (SQLAlchemyError, ValueError, KeyError) as e:
            db.session.rollback()
            logger.error(f"Error creating wallet for user ID {user_id} with {data}: {e}")
            return {"message": "An error occurred while creating wallet", 'status_code': 500}
        

    # Lấy danh sách wallet
    def get_wallets_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            wallets = Wallet.query.filter_by(user_id=user_id, is_deleted=False).paginate(page=page, per_page=per_page, error_out=False)
            wallets_list = [{
                'id': w.id,
                'name': w.name,
                'balance': w.balance,
                'currency': w.currentcy
            } for w in wallets.items]
            
            # Trả về danh sách ví
            return {
                'wallets': wallets_list,
                'page': wallets.page,
                'per_page': wallets.per_page,
                'total_pages': wallets.pages,
                'total_items': wallets.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving wallets for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving wallets', 'status_code': 500}
        

    # Lấy danh sách wallet đã bị xoá
    def get_deleted_wallets_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            deleted_wallets = Wallet.query.filter_by(user_id=user_id, is_deleted=True).paginate(page=page, per_page=per_page, error_out=False)
            deleted_wallets_list = [{
                'id': w.id,
                'name': w.name,
                'balance': w.balance,
                'currency': w.currentcy
            } for w in deleted_wallets.items]
            
            # Trả về danh sách ví đã xoá
            return {
                'deleted wallets': deleted_wallets_list,
                'page': deleted_wallets.page,
                'per_page': deleted_wallets.per_page,
                'total_pages': deleted_wallets.pages,
                'total_items': deleted_wallets.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving deleted wallets for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving deleted wallets', 'status_code': 500}
        
    
    # Lấy thông tin wallet
    def get_wallet_service(user_id, wallet_id):
        try:
            # Kiểm tra tồn tại
            wallet = WalletService.existence_check(Wallet, wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {wallet_id} not found for user_id {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            # Trả về thông tin ví
            return {
                'id': wallet.id,
                'name': wallet.name,
                'balance': float(wallet.balance),
                'currency': wallet.currency,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving wallet for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving wallet', 'status_code': 500}
        

    # Cập nhật thông tin wallet
    def update_wallet_service(user_id, wallet_id, data):
        logger.info(f'Updating wallet ID {wallet_id} for user ID {user_id} with data {data}')
    
        try:
            # Kiểm tra tồn tại
            wallet = WalletService.existence_check(Wallet, wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {wallet_id} not found for user_id {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}

            # Kiểm tra trùng tên ví
            if 'name' in data:
                existing_wallet = Wallet.query.filter(Wallet.user_id == user_id, Wallet.name == data['name'], Wallet.is_deleted == False, Wallet.id != wallet_id).first()
                if existing_wallet:
                    logger.warning(f'Wallet name {data["name"]} already exists')
                    return {'message': 'Wallet name already exists', 'status_code': 409}
            
                wallet.name = data['name']

            # Kiểm tra currency hợp lệ
            if 'currency' in data:
                valid_currencies = ['VND', 'USD', 'CNY', 'KRW']
                if data['currency'] not in valid_currencies:
                    logger.warning(f'Invalid currency')
                    return {'message': 'Invalid currency', 'status_code': 400}
                
                wallet.currency = data['currency']

            # Commit vào db và trả về
            db.session.commit()
            logger.info(f'Wallet ID {wallet_id} updated successfully for user ID {user_id}')
            return {
                'message': 'Wallet updated successfully',
                'wallet': {
                    'id': wallet.id,
                    'name': wallet.name,
                    'balance': float(wallet.balance),
                    'currency': wallet.currency
                },
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError, KeyError) as e:
            db.session.rollback()
            logger.error(f'Error updating wallet ID {wallet_id} for user ID {user_id} with {data}: {e}')
            return {'message': 'An error occurred while updating wallet', 'status_code': 500}
        
    
    # Xoá wallet
    def delete_wallet_service(user_id, wallet_id):
        logger.info(f'Deleting wallet ID {wallet_id} for user ID {user_id}')
    
        try:
            # Kiểm tra tồn tại
            wallet = WalletService.existence_check(Wallet, wallet_id, user_id)
            if not wallet:
                logger.warning(f'Wallet ID {wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            # Kiểm tra giao dịch liên quan
            transactions = Transaction.query.filter_by(wallet_id=wallet_id).first()
            if transactions:
                logger.warning(f'Cannot delete wallet ID {wallet_id} because it has associated transactions')
                return {'message': 'Cannot delete wallet with associated transactions', 'status_code': 400}
    
            # Xoá dữ liệu trong db
            db.session.delete(wallet)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Wallet ID {wallet_id} deleted successfully for user ID {user_id}')
            return {'message': 'Wallet deleted successfully', 'status_code': 200}
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error deleting wallet ID {wallet_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while deleting wallet', 'status_code': 500}
        

    # Kiểm tra số dư ví
    def get_balance_service(user_id, wallet_id):
        try:
            # Kiểm tra tồn tại
            wallet = WalletService.existence_check(Wallet, wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            # Kiểm tra ví đã bị xóa chưa
            if wallet.is_deleted:
                logger.warning(f'Wallet ID {wallet_id} is deleted')
                return {'message': 'Wallet is deleted', 'status_code': 400}
            
            # Trả về thông tin số dư
            return {
                'name': wallet.name,
                'balance': float(wallet.balance),
                'status_code': 200
            }

        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving wallet balance for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving wallet balance', 'status_code': 500}
        

    # Xoá tạm thời
    def soft_delete_wallet_service(user_id, wallet_id):
        logger.info(f'Soft deleting wallet ID {wallet_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            wallet = WalletService.existence_check(Wallet, wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
    
            # Cập nhật vào db
            wallet.is_deleted = True
            wallet.deleted_at = datetime.utcnow()
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Wallet ID {wallet_id} soft deleted successfully for user ID {user_id}')
            return {'message': 'Wallet soft deleted successfully', 'status_code': 200}
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error soft deleting wallet ID {wallet_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while soft deleting wallet', 'status_code': 500}
        

    # Khôi phục wallet
    def restore_wallet_service(user_id, wallet_id):
        logger.info(f'Soft restoring wallet ID {wallet_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            wallet = WalletService.existence_check(Wallet, wallet_id, user_id, is_deleted=True)
            if not wallet:
                logger.warning(f'Wallet ID {wallet_id} not found or not soft deleted for user ID {user_id}')
                return {'message': 'Wallet not found or not soft deleted', 'status_code': 404}

            # Cập nhật vào db
            wallet.is_deleted = False
            wallet.deleted_at = None
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Wallet ID {wallet_id} restored successfully for user ID {user_id}')
            return {'message': 'Wallet restored successfully', 'status_code': 200}
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error restoring wallet ID {wallet_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while restoring wallet', 'status_code': 500}