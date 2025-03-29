from extensions import db
from models import Budget, Category
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from .wallet_service import WalletService

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BudgetService:
    # Tạo budget mới
    def create_budget_service(user_id, data, force_create=False):
        logger.info(f'Creating budget for user ID {user_id} with data {data}')

        try:
            # Kiểm tra giá trị thiếu
            if not data or not data.get('category_id') or not data.get('amount'):
                logger.warning('Missing required fields')
                return {'message': 'Missing required fields', 'status_code': 400}
            
            # Kiểm tra category
            category = WalletService.existence_check(Category, data['category_id'], user_id)
            if not category:
                logger.warning(f'Category ID {data["category_id"]} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Kiểm tra amount
            if data['amount'] <= 0:
                logger.warning(f'Amount must be greater than 0 VND')
                return {'message': 'Amount must be greater than 0 VND', 'status_code': 400}
            
            # Kiểm tra ngày
            start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else datetime.now().date()
            end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else start_date + timedelta(days=30)

            if end_date <= start_date:
                logger.warning(f'End_date {end_date} must be after start_date {start_date}')
                return {'message': 'End date must be after start date', 'status_code': 400}
            
            # Kiểm tra budget đã soft delete
            deleted_budget = Budget.query.filter_by(user_id=user_id, category_id=data['category_id'], is_deleted=True).first()
            if deleted_budget or not force_create:
                logger.info(f'Budget {data["category_id"]} was soft deleted, asking user for restore')
                return {
                    'message': 'Budget previously deleted. Do you want to restore it?',
                    'status_code': 409,  # Conflict
                    'restore_suggestion': True,
                    'goal_id': deleted_budget.id
                }
            
            # Tạo budget
            new_budget = Budget (
                user_id = user_id,
                category_id = data['category_id'],
                amount = data['amount'],
                start_date = start_date,
                end_date = end_date,
                is_deleted = False,
                deleted_at = None
            )

            # Thêm vào db
            db.session.add(new_budget)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Budget created successfully for user ID {user_id}')
            return {
                'message': 'Budget created successfully',
                'budget': {
                    'id': new_budget.id,
                    'category_id': new_budget.category_id,
                    'amount': float(new_budget.amount),
                    'start_date': new_budget.start_date.isoformat(),
                    'end_date': new_budget.end_date.isoformat()
                },
                'status_code': 201
            }
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating budget for user ID {user_id}: {e}")
            return {"message": "An error occurred while creating budget", 'status_code': 500}
        

    # Lấy danh sách budget
    def get_budgets_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            budgets = Budget.query.filter_by(user_id=user_id, is_deleted=False).paginate(page=page, per_page=per_page, error_out=False)
            budgets_list = [{
                'id': b.id,
                'category_id': b.category_id,
                'amount': float(b.amount),
                'start_date': b.start_date.isoformat(),
                'end_date': b.end_date.isoformat()
            } for b in budgets.items]
            
            # Trả về danh sách budget
            return {
                'budgets': budgets_list,
                'page': budgets.page,
                'per_page': budgets.per_page,
                'total_pages': budgets.pages,
                'total_items': budgets.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving budgets for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving budgets', 'status_code': 500}
        

    # Lấy danh sách budget đã xoá
    def get_deleted_budgets_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            deleted_budgets = Budget.query.filter_by(user_id=user_id, is_deleted=True).paginate(page=page, per_page=per_page, error_out=False)
            deleted_budgets_list = [{
                'id': b.id,
                'category_id': b.category_id,
                'amount': float(b.amount),
                'start_date': b.start_date.isoformat(),
                'end_date': b.end_date.isoformat()
            } for b in deleted_budgets.items]
            
            # Trả về danh sách budget
            return {
                'budgets': deleted_budgets_list,
                'page': deleted_budgets.page,
                'per_page': deleted_budgets.per_page,
                'total_pages': deleted_budgets.pages,
                'total_items': deleted_budgets.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving deleted budgets for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving deleted budgets', 'status_code': 500}
        

    # Lấy thông tin budget
    def get_budget_service(user_id, budget_id):
        try:
            # Kiểm tra tồn tại
            budget = WalletService.existence_check(Budget, budget_id, user_id, is_deleted=False)
            if not budget:
                logger.warning(f'Budget ID {budget_id} not found for user_id {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Trả về thông tin ví
            return {
                'id': budget.id,
                'category_id': budget.category_id,
                'amount': float(budget.amount),
                'start_date': budget.start_date.isoformat(),
                'end_date': budget.end_date.isoformat(),
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving budget ID {budget_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving budget', 'status_code': 500}
        
    
    # Cập nhật budget
    def update_budget_service(user_id, budget_id, data):
        logger.info(f'Updating budget ID {budget_id} for user ID {user_id} with data {data}')

        try:
            # Kiểm tra tồn tại
            budget = WalletService.existence_check(Budget, budget_id, user_id, is_deleted=False)
            if not budget:
                logger.warning(f'Budget ID {budget_id} not found for user_id {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            if 'category_id' in data:
                category = WalletService.existence_check(Category, data['category_id'], user_id)
                if not category:
                    logger.warning(f'Category ID {data["category_id"]} not found for user ID {user_id}')
                    return {'message': 'Category not found', 'status_code': 404}
                
                budget.category_id = data['category_id']

            if 'amount' in data:
                if data['amount'] <= 0:
                    logger.warning(f'Amount must be greater than 0 VND')
                    return {'message': 'Amount must be greater than 0 VND', 'status_code': 400}
                
                budget.amount = data['amount']

            # Lấy giá trị hiện tại của start_date và end_date
            start_date = budget.start_date
            end_date = budget.end_date

            if 'start_date' in data:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                budget.start_date = start_date

            if 'end_date' in data:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                budget.end_date = end_date

            # Kiểm tra điều kiện end_date > start_date
            if end_date <= start_date:
                logger.warning(f'End_date {end_date} must be after start_date {start_date}')
                return {'message': 'End date must be after start date', 'status_code': 400}
            
            # Commit vào db
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Budget ID {budget_id} updated successfully for user ID {user_id}')
            return {
                'message': 'Budget updated successfully',
                'budget': {
                    'id': budget.id,
                    'category_id': budget.category_id,
                    'amount': float(budget.amount),
                    'start_date': budget.start_date.isoformat(),
                    'end_date': budget.end_date.isoformat()
                },
                'status_code': 201
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error updating budget ID {budget_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while updating budget', 'status_code': 500}
        

    # Xoá budget vĩnh viễn
    def delete_budget_service(user_id, budget_id):
        logger.info(f'Deleting budget ID {budget_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            budget = WalletService.existence_check(Budget, budget_id, user_id, is_deleted=False)
            if not budget:
                logger.warning(f'Budget ID {budget_id} not found for user_id {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Xoá khỏi db
            db.session.delete(budget)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Budget ID {budget_id} deleted successfully for user ID {user_id}')
            return {'message': 'Budget deleted successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting budget ID {budget_id} for user ID {user_id}: {e}")
            return {'message': 'An error occurred while deleting budget', 'status_code': 500}
        

    # Xoá budget tạm thời
    def soft_delete_budget_service(user_id, budget_id):
        logger.info(f'Soft deleting budget ID {budget_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            budget = WalletService.existence_check(Budget, budget_id, user_id, is_deleted=False)
            if not budget:
                logger.warning(f'Budget ID {budget_id} not found for user_id {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Cập nhật db
            budget.is_deleted = True
            budget.deleted_at = datetime.utcnow()
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Budget ID {budget_id} soft deleted successfully for user ID {user_id}')
            return {'message': 'Budget soft deleted successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error soft deleting budget ID {budget_id} for user ID {user_id}: {e}")
            return {'message': 'An error occurred while soft deleting budget', 'status_code': 500}
        

    # Khôi phục budget
    def restore_budget_service(user_id, budget_id):
        logger.info(f'Restoring budget ID {budget_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            budget = WalletService.existence_check(Budget, budget_id, user_id, is_deleted=True)
            if not budget:
                logger.warning(f'Budget ID {budget_id} not found for user_id {user_id}')
                return {'message': 'Budget not found', 'status_code': 404}
            
            # Cập nhật db
            budget.is_deleted = False
            budget.deleted_at = None
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Budget ID {budget_id} restored successfully for user ID {user_id}')
            return {'message': 'Budget restored successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error restoring budget ID {budget_id} for user ID {user_id}: {e}")
            return {'message': 'An error occurred while restoring budget', 'status_code': 500}

