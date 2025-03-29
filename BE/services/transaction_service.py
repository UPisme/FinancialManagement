from extensions import db
from models import Transaction, Wallet, Goal, Category, Budget
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from .wallet_service import WalletService


# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionService:
    # Tạo transaction mới
    def create_transaction_service(user_id, data):
        logger.info(f'Creating transaction for user ID {user_id}')

        try:
            # Kiểm tra trường bắt buộc
            required_fields = ['wallet_id', 'amount', 'transaction_type']
            if not all(field in data for field in required_fields):
                logger.warning('Missing required fields')
                return {'message': 'Missing required fields', 'status_code': 400}
            
            # User phải chọn dùng tiền từ ví hay goal
            if 'wallet_id' not in data and 'goal_id' not in data:
                logger.warning('Must specify either wallet_id or goal_id')
                return {'message': 'Must specify either wallet_id or goal_id', 'status_code': 400}
            
            # Kiểm tra người dùng chỉ được nhập một trong hai: wallet_id hoặc goal_id
            if 'wallet_id' in data and 'goal_id' in data:
                logger.warning('Cannot specify both wallet_id and goal_id')
                return {'message': 'Cannot specify both wallet_id and goal_id', 'status_code': 400}
            
            # Kiểm tra ví tiền
            wallet = WalletService.existence_check(Wallet, data['wallet_id'], user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {data["wallet_id"]} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            # Kiểm tra goal
            goal = WalletService.existence_check(Goal, data['goal_id'], user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {data["goal_id"]} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            # Cảnh báo nếu người dùng sử dụng tiền từ mục tiêu
            if 'goal_id' in data:
                return {
                    'message': 'You are using money from your savings goal. Are you sure you want to continue?',
                    'requires_confirmation': True,  # Yêu cầu xác nhận từ frontend
                    'status_code': 200
                }
                
            # Kiểm tra danh mục
            category = WalletService.existence_check(Category, data['category_id'], user_id, is_deleted=False)
            if not category:
                logger.warning(f'Category ID {data["category_id"]} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Kiểm tra số tiền
            if data['amount'] <= 0:
                logger.warning(f'Amount must be greater than 0 VND')
                return {'message': 'Amount must be greater than 0 VND', 'status_code': 400}
            
            # Kiểm tra loại giao dịch
            if data['transaction_type'] not in ['Income', 'Expense']:
                logger.warning(f'Invalid transaction type: {data["transaction_type"]}')
                return {"message": "Invalid transaction type", 'status_code': 400}

            # Tạo transaction
            new_transaction = Transaction (
                user_id = user_id,
                wallet_id=data.get('wallet_id'),
                goal_id=data.get('goal_id'),
                category_id = data.get('category_id'),
                amount = data['amount'],
                transaction_type = data['transaction_type'],
                note = data.get('note', ''),
                date = datetime.strptime(data.get('date'), '%Y-%m-%d %H:%M:%S') if data.get('date') else datetime.utcnow(),
                is_deleted = False,
                deleted_at = None
            )

            # Thêm vào db
            db.session.add(new_transaction)

            # Cập nhật tiền trong wallet/goal
            if 'wallet_id' in data:
                if data['transaction_type'] == 'Income':
                    wallet.balance += data['amount']
                else:
                    if wallet.balance < data['amount']:
                        logger.warning(f'Insufficient balance in wallet ID {data["wallet_id"]}')
                        return {'message':'Insufficient balance', 'status_code': 400}
                    wallet.balance -= data['amount']
            elif 'goal_id' in data:
                if data['transaction_type'] == 'Income':
                    goal.saved_amount += data['amount']
                else:
                    if goal.saved_amount < data['amount']:
                        logger.warning(f'Insufficient saved amount in goal ID {data["goal_id"]}')
                        return {'message': 'Insufficient saved amount', 'status_code': 400}
                    goal.saved_amount -= data['amount']

            # Cập nhật ngân sách
            budget = Budget.query.filter_by(user_id=user_id, category_id=data['category_id'], is_deleted=False).first()
            if budget and data['transaction_type'] == 'Expense':
                if budget.amount < data['amount']:
                    logger.warning(f'Budget exceeded for category ID {data["category_id"]}. Current budget: {budget.amount}, Transaction amount: {data["amount"]}')
                budget.amount -= data['amount']
                logger.info(f'Budget for category ID {data["category_id"]} updated: Remaining budget = {budget.amount}')
            elif not budget:
                logger.warning(f'Budget of category ID {data["category_id"]} not found for user ID {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}

            # Commit và trả về kết quả
            db.session.commit()
            logger.info(f'Transaction created successfully for user ID {user_id}')
            return {
                'message': 'Transaction created successfully',
                'transaction': {
                    'id': new_transaction.id,
                    'wallet_id': new_transaction.wallet_id,
                    'category_id': new_transaction.category_id,
                    'amount': float(new_transaction.amount),
                    'transaction_type': new_transaction.transaction_type,
                    'note': new_transaction.note,
                    'date': new_transaction.date.isoformat()
                },
                'status_code': 201
            }
    
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating transaction for user ID {user_id}: {e}")
            return {"message": "An error occurred while creating transaction", 'status_code': 500}
        

    # Lấy danh sách transaction
    def get_transactions_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            transactions = Transaction.query.filter_by(user_id=user_id, is_deleted=False).paginate(page=page, per_page=per_page, error_out=False)
            transactions_list = [{
                'id': t.id,
                'amount': float(t.amount),
                'transaction_type': t.transaction_type,
                'date': t.date.isoformat()
            } for t in transactions.items]
            
            # Trả về danh sách transaction
            return {
                'transactions': transactions_list,
                'page': transactions.page,
                'per_page': transactions.per_page,
                'total_pages': transactions.pages,
                'total_items': transactions.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving transactions for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving transactions', 'status_code': 500}
        

    # Lấy danh sách transaction đã xoá
    def get_deleted_transactions_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            deleted_transactions = Transaction.query.filter_by(user_id=user_id, is_deleted=True).paginate(page=page, per_page=per_page, error_out=False)
            deleted_transactions_list = [{
                'id': t.id,
                'amount': float(t.amount),
                'transaction_type': t.transaction_type,
                'date': t.date.isoformat()
            } for t in deleted_transactions.items]
            
            # Trả về danh sách transaction đã xoá
            return {
                'transactions': deleted_transactions_list,
                'page': deleted_transactions.page,
                'per_page': deleted_transactions.per_page,
                'total_pages': deleted_transactions.pages,
                'total_items': deleted_transactions.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving deleted transactions for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving deleted transactions', 'status_code': 500}
        

    # Lấy thông tin transaction
    def get_transaction_service(user_id, transaction_id):
        try:
            # Kiểm tra tồn tại
            transaction = WalletService.existence_check(Transaction, transaction_id, user_id, is_deleted=False)
            if not transaction_id:
                logger.warning(f'Transaction ID {transaction_id} not found for user_id {user_id}')
                return {'message': 'Transaction not found', 'status_code': 404}
            
            # Trả về thông tin transaction
            return {
                'id': transaction.id,
                'wallet_id': transaction.wallet_id,
                'category_id': transaction.category_id,
                'amount': float(transaction.amount),
                'transaction_type': transaction.transaction_type,
                'note': transaction.note,
                'date': transaction.date.isoformat(),
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving transaction for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving transaction', 'status_code': 500}
        

    # Cập nhật transaction
    def update_transaction_service(user_id, transaction_id, data):
        logger.info(f'Updating transaction ID {transaction_id} for user ID {user_id} with data {data}')
        
        try:
            transaction = WalletService.existence_check(Transaction, transaction_id, user_id, is_deleted=False)
            if not transaction:
                logger.warning(f'Transaction ID {transaction_id} not found for user ID {user_id}')
                return {'message': 'Transaction not found', 'status_code': 404}
            
            # Lấy wallet/goal trong transaction muốn update và budget để hoàn tác số dư trước khi thay đổi
            wallet = WalletService.existence_check(Wallet, transaction.wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {transaction.wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            goal = WalletService.existence_check(Goal, transaction.goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {transaction.goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            budget = Budget.query.filter_by(user_id=user_id, category_id=transaction.category_id, is_deleted=False).first()
            if not budget:
                logger.warning(f'Budget of category ID {transaction.category_id} not found for user ID {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Hoàn tác tiền cho wallet/goal và budget
            if transaction.transaction_type == 'Income':
                if transaction.wallet_id:
                    wallet.balance -= transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount -= transaction.amount
            else:
                budget.amount += transaction.amount
                if transaction.wallet_id:
                    wallet.balance += transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount += transaction.amount

            # Cập nhật transaction
            # Kiểm tra wallet
            if 'wallet_id' in data:
                new_wallet = WalletService.existence_check(Wallet, data['wallet_id'], user_id, is_deleted=False)
                if not new_wallet:
                    logger.warning(f'Wallet ID {data["wallet_id"]} not found for user ID {user_id}')
                    return {'message': 'Wallet not found', 'status_code': 404}
                
                transaction.wallet_id = data['wallet_id']

            # Kiểm tra goal
            if 'goal_id' in data:
                new_goal = WalletService.existence_check(Goal, data['goal_id'], user_id, is_deleted=False)
                if not new_goal:
                    logger.warning(f'Goal ID {data["goal_id"]} not found for user ID {user_id}')
                    return {'message': 'Goal not found', 'status_code': 404}
                
                transaction.goal_id = data['goal_id']

            # Kiểm tra category
            if 'category_id' in data:
                new_category = WalletService.existence_check(Category, data['category_id'], user_id, is_deleted=False)
                if not new_category:
                    logger.warning(f'Category ID {data["category_id"]} not found for user ID {user_id}')
                    return {'message': 'Category not found', 'status_code': 404}
                
                transaction.category_id = data['category_id']
                new_budget = Budget.query.filter_by(user_id=user_id, category_id=data['category_id'], is_deleted=False).first()

            # Kiểm tra amount
            if 'amount' in data:
                if data['amount'] <= 0:
                    logger.warning(f'Amount must be greater than 0 VND')
                    return {'message': 'Amount must be greater than 0 VND', 'status_code': 400}
                
                transaction.amount = data['amount']

            # Kiểm tra transaction type
            if 'transaction_type' in data:
                if data['transaction_type'] not in ['Income', 'Expense']:
                    logger.warning(f'Invalid transaction type: {data["transaction_type"]}')
                    return {"message": "Invalid transaction type", 'status_code': 400}
                
                transaction.transaction_type = data['transaction_type']

            # Kiểm tra note
            if 'note' in data:
                transaction.note = data['note']

            # Kiểm tra date
            if 'date' in data:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')

            # Cập nhật lại số dư
            if transaction.transaction_type == 'Income':
                if transaction.wallet_id:
                    new_wallet.balance += transaction.amount
                elif transaction.goal_id:
                    new_goal.saved_amount += transaction.amount
            else:
                new_budget.amount -= transaction.amount
                if transaction.wallet_id:
                    if new_wallet.balance < transaction.amount:
                        logger.warning(f'Insufficient balance in wallet ID {transaction.wallet_id}')
                        return {'message': 'Insufficient balance', 'status_code': 400}
                    new_wallet.balance -= transaction.amount
                elif transaction.goal_id:
                    if new_goal.saved_amount < transaction.amount:
                        logger.warning(f'Insufficient saved amount in goal ID {transaction.goal_id}')
                        return {'message': 'Insufficient saved amount', 'status_code': 400}
                    new_goal.saved_amount -= transaction.amount

            # Commit vào db và trả về kết quả
            db.session.commit()
            logger.info(f'Transaction ID {transaction_id} updated successfull for {user_id}')
            return {
                'message': 'Transaction updated successfully',
                'transaction': {
                    'id': transaction.id,
                    'wallet_id': transaction.wallet_id,
                    'category_id': transaction.category_id,
                    'amount': float(transaction.amount),
                    'transaction_type': transaction.transaction_type,
                    'note': transaction.note,
                    'date': transaction.date.isoformat()
                },
                'status_code': 200
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error updating transaction ID {transaction_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while updating transaction', 'status_code': 500}
        

    # Xoá transaction vĩnh viễn
    def delete_transaction_service(user_id, transaction_id):
        logger.info(f'Deleting transaction ID {transaction_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            transaction = WalletService.existence_check(Transaction, transaction_id, user_id, is_deleted=False)
            if not transaction:
                logger.warning(f'Transaction ID {transaction_id} not found for user ID {user_id}')
                return {'message': 'Transaction not found', 'status_code': 404}
            
            wallet = WalletService.existence_check(Wallet, transaction.wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {transaction.wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            goal = WalletService.existence_check(Goal, transaction.goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {transaction.goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            budget = Budget.query.filter_by(user_id=user_id, category_id=transaction.category_id, is_deleted=False).first()
            if not budget:
                logger.warning(f'Budget of category ID {transaction.category_id} not found for user ID {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Hoàn tác tiền cho wallet/goal và budget
            if transaction.transaction_type == 'Income':
                if transaction.wallet_id:
                    wallet.balance -= transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount -= transaction.amount
            else:
                budget.amount += transaction.amount
                if transaction.wallet_id:
                    wallet.balance += transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount += transaction.amount

            # Xoá khỏi db
            db.session.delete(transaction)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Transaction ID {transaction_id} deleted successfully for user ID {user_id}')
            return {'message': 'Transaction deleted successfully', 'status_code': 200}
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error deleting transaction ID {transaction_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while deleting transaction', 'status_code': 500}
        

    # Xoá transaction tạm thời
    def soft_delete_transaction_service(user_id, transaction_id):
        logger.info(f'Soft deleting transaction ID {transaction_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            transaction = WalletService.existence_check(Transaction, transaction_id, user_id, is_deleted=False)
            if not transaction:
                logger.warning(f'Transaction ID {transaction_id} not found for user ID {user_id}')
                return {'message': 'Transaction not found', 'status_code': 404}
            
            wallet = WalletService.existence_check(Wallet, transaction.wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {transaction.wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            goal = WalletService.existence_check(Goal, transaction.goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {transaction.goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            budget = Budget.query.filter_by(user_id=user_id, category_id=transaction.category_id, is_deleted=False).first()
            if not budget:
                logger.warning(f'Budget of category ID {transaction.category_id} not found for user ID {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Hoàn tác tiền cho wallet/goal và budget
            if transaction.transaction_type == 'Income':
                if transaction.wallet_id:
                    wallet.balance -= transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount -= transaction.amount
            else:
                budget.amount += transaction.amount
                if transaction.wallet_id:
                    wallet.balance += transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount += transaction.amount

            # Cập nhật db
            transaction.is_deleted = True
            transaction.deleted_at = datetime.utcnow()
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Transaction ID {transaction_id} soft deleted successfully for user ID {user_id}')
            return {'message': 'Transaction soft deleted successfully', 'status_code': 200}
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error soft deleting transaction ID {transaction_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while soft deleting transaction', 'status_code': 500}
        

    # Khôi phục transaction
    def restore_transaction_service(user_id, transaction_id):
        logger.info(f'Restoring transaction ID {transaction_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            transaction = WalletService.existence_check(Transaction, transaction_id, user_id, is_deleted=True)
            if not transaction:
                logger.warning(f'Transaction ID {transaction_id} not found for user ID {user_id}')
                return {'message': 'Transaction not found', 'status_code': 404}
            
            wallet = WalletService.existence_check(Wallet, transaction.wallet_id, user_id, is_deleted=False)
            if not wallet:
                logger.warning(f'Wallet ID {transaction.wallet_id} not found for user ID {user_id}')
                return {'message': 'Wallet not found', 'status_code': 404}
            
            goal = WalletService.existence_check(Goal, transaction.goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {transaction.goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            budget = Budget.query.filter_by(user_id=user_id, category_id=transaction.category_id, is_deleted=False).first()
            if not budget:
                logger.warning(f'Budget of category ID {transaction.category_id} not found for user ID {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Cập nhật tiền cho wallet/goal và budget
            if transaction.transaction_type == 'Income':
                if transaction.wallet_id:
                    wallet.balance += transaction.amount
                elif transaction.goal_id:
                    goal.saved_amount += transaction.amount
            else:
                budget.amount -= transaction.amount
                if transaction.wallet_id:
                    if wallet.balance < transaction.amount:
                        logger.warning(f'Insufficient balance in wallet ID {transaction.wallet_id}')
                        return {'message':'Insufficient balance', 'status_code': 400}
                    wallet.balance -= transaction.amount
                elif transaction.goal_id:
                    if goal.saved_amount < transaction.amount:
                        logger.warning(f'Insufficient saved amount in goal ID {transaction.goal_id}')
                        return {'message': 'Insufficient saved amount', 'status_code': 400}
                    goal.saved_amount -= transaction.amount

            # Cập nhật db
            transaction.is_deleted = False
            transaction.deleted_at = None
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Transaction ID {transaction_id} restored successfully for user ID {user_id}')
            return {'message': 'Transaction restored successfully', 'status_code': 200}
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error restoring transaction ID {transaction_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while restoring transaction', 'status_code': 500}