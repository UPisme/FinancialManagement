from extensions import db
from models import Goal, Transaction
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from .wallet_service import WalletService

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoalService:
    # Tạo goal mới
    def create_goal_service(user_id, data, force_create=False):
        logger.info(f'Creating goal for user ID {user_id}')

        try:
            # Kiểm tra giá trị thiếu
            if not data or not data.get('name') or not data.get('target_amount'):
                logger.warning(f'Missing required fields')
                return {'message': 'Missing required fields', 'status_code': 400}
            
            # Kiểm tra trùng tên
            existing_goal = Goal.query.filter_by(user_id=user_id, name=data['name'], is_deleted=False).first()
            if existing_goal:
                logger.warning(f'Goal name {data["name"]} already exists')
                return {'message': 'Goal name already exists', 'status_code': 409}
            
            # Kiểm tra số tiền
            if data['target_amount'] <= 0:
                logger.warning(f'Target amount must be greater than 0 VND')
                return {'message': 'Target amount must be greater than 0 VND', 'status_code': 400}
            
            if 'saved_amount' in data and data['saved_amount'] < 0:
                logger.warning(f'Saved amount cannot be less than 0 VND')
                return {'message': 'Saved amount cannot be less than 0 VND', 'status_code': 400}
            
            # Kiểm tra ngày hợp lệ
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            if deadline < datetime.now().date():
                logger.warning(f'Invalid deadline')
                return {'message': 'Deadline must be in the future', 'status_code': 400}
            
            # Kiểm tra goal đã soft delete
            deleted_goal = Goal.query.filter_by(user_id=user_id, name=data['name'], is_deleted=True).first()

            if deleted_goal or not force_create:
                logger.info(f'Goal "{data["name"]}" was soft deleted, asking user for restore')
                return {
                    'message': 'Goal previously deleted. Do you want to restore it?',
                    'status_code': 409,  # Conflict
                    'restore_suggestion': True,
                    'goal_id': deleted_goal.id
                }

            # Tạo mới
            new_goal = Goal (
                user_id = user_id,
                name = data['name'],
                target_amount = data['target_amount'],
                saved_amount = data.get('saved_amount', 0),
                deadline = deadline if data.get('deadline') else datetime.now().date(),
                is_deleted = False,
                deleted_at = None
            )
        
            # Thêm vào db
            db.session.add(new_goal)
            db.session.commit()
            
            # Trả về kết quả
            logger.info(f'Goal created successfully for user ID {user_id}')
            return {
                'message': 'Goal created successfully',
                'goal': {
                    'id': new_goal.id,
                    'name': new_goal.name,
                    'target_amount': float(new_goal.target_amount),
                    'saved_amount': float(new_goal.saved_amount),
                    'deadline': new_goal.deadline.isoformat()
                },
                'status_code': 201
            }
        
        except (SQLAlchemyError, ValueError, KeyError) as e:
            db.session.rollback()
            logger.error(f"Error creating goal for user ID {user_id} with {data}: {e}")
            return {"message": "An error occurred while creating goal", 'status_code': 500}


    # Lấy danh sách goal
    def get_goals_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            goals = Goal.query.filter_by(user_id=user_id, is_deleted=False).paginate(page=page, per_page=per_page, error_out=False)
            goals_list = [{
                'id': g.id,
                'name': g.name,
                'target_amount': g.target_amount,
                'saved_amount': g.saved_amount,
                'deadline': g.deadline
            } for g in goals.items]
            
            # Trả về danh sách goal
            return {
                'goals': goals_list,
                'page': goals.page,
                'per_page': goals.per_page,
                'total_pages': goals.pages,
                'total_items': goals.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving goals for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving goals', 'status_code': 500}
        

    # Lấy danh sách goal đã xoá
    def get_deleted_goals_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            deleted_goals = Goal.query.filter_by(user_id=user_id, is_deleted=True).paginate(page=page, per_page=per_page, error_out=False)
            deleted_goals_list = [{
                'id': g.id,
                'name': g.name,
                'target_amount': g.target_amount,
                'saved_amount': g.saved_amount,
                'deadline': g.deadline
            } for g in deleted_goals.items]
            
            # Trả về danh sách goal đã xoá
            return {
                'goals': deleted_goals_list,
                'page': deleted_goals.page,
                'per_page': deleted_goals.per_page,
                'total_pages': deleted_goals.pages,
                'total_items': deleted_goals.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving deleted goals for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving deleted goals', 'status_code': 500}
        

    # Lấy thông tin chi tiết goal
    def get_goal_service(user_id, goal_id):
        try:
            # Kiểm tra tồn tại
            goal = WalletService.existence_check(Goal, goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            # Trả về thông tin goal
            return {
                'id': goal.id,
                'name': goal.name,
                'target_amount': float(goal.target_amount),
                'saved_amount': float(goal.saved_amount),
                'deadline': goal.deadline.isoformat(),
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving goal ID {goal_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving goal', 'status_code': 500}
        

    # Cập nhật thông tin goal
    def update_goal_service(user_id, goal_id, data):
        logger.info(f'Updating goal ID {goal_id} for user ID {user_id} with data {data}')

        try:
            # Kiểm tra tồn tại
            goal = WalletService.existence_check(Goal, goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}

            # Kiểm tra goal đã bị xóa chưa
            if goal.is_deleted:
                logger.warning(f'Goal ID {goal_id} is deleted and cannot be updated')
                return {'message': 'Goal is deleted and cannot be updated', 'status_code': 400}
        
            # Kiểm tra trùng tên
            if 'name' in data:
                existing_goal = Goal.query.filter(Goal.user_id == user_id, Goal.name == data['name'], Goal.is_deleted == False, Goal.id != goal_id).first()
                if existing_goal:
                    logger.warning(f'Goal name {data["name"]} already exists')
                    return {'message': 'Goal name already exists', 'status_code': 409}
                goal.name = data['name']

            # Kiểm tra target amount
            if 'target_amount' in data:
                if data['target_amount'] <= 0:
                    logger.warning(f'Target amount must be greater than 0 VND')
                    return {'message': 'Target amount must be greater than 0 VND', 'status_code': 400}         
                goal.target_amount = data['target_amount']

            # Kiểm tra saved amount
            if 'saved_amount' in data:
                if data['saved_amount'] < 0:
                    logger.warning(f'Saved amount cannot be less than 0 VND')
                    return {'message': 'Target amount cannot be less than 0 VND', 'status_code': 400}           
                goal.saved_amount = data['saved_amount']
                
            # Kiểm tra deadline
            if 'deadline' in data:
                deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
                if deadline < datetime.now().date():
                    logger.warning(f'Invalid deadline')
                    return {'message': 'Deadline must be in the future', 'status_code': 400}          
                goal.deadline = data['deadline']

            # Commit vào db và trả về
            db.session.commit()
            logger.info(f'Goal ID {goal_id} updated successfully for user ID {user_id}')
            return {
                'message': 'Goal updated successfully',
                'goal': {
                    'id': goal.id,
                    'name': goal.name,
                    'target_amount': float(goal.target_amount),
                    'saved_amount': float(goal.saved_amount),
                    'deadline': goal.deadline.isoformat()
                },
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError, KeyError) as e:
            db.session.rollback()
            logger.error(f'Error updating goal ID {goal_id} for user ID {user_id} with {data}: {e}')
            return {'message': 'An error occurred while updating goal', 'status_code': 500}
        

    # Xoá goal
    def delete_goal_service(user_id, goal_id):
        logger.info(f'Deleting goal ID {goal_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            goal = WalletService.existence_check(Goal, goal_id, user_id)
            if not goal:
                logger.warning(f'Goal ID {goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            # Kiểm tra giao dịch liên quan
            transactions = Transaction.query.filter_by(goal_id=goal_id).first()
            if transactions:
                logger.warning(f'Cannot delete goal ID {goal_id} because it has associated transactions')
                return {'message': 'Cannot delete goal with associated transactions', 'status_code': 400}
            
            # Xoá khỏi db
            db.session.delete(goal)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Goal ID {goal_id} deleted successfully for user ID {user_id}')
            return {'message': 'Goal deleted successfully', 'status_code': 200}
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error deleting goal ID {goal_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while deleting goal', 'status_code': 500}
        

    # Trạng thái goal
    def get_goal_status_service(user_id, goal_id):
        try:
            # Kiểm tra tồn tại
            goal = WalletService.existence_check(Goal, goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}

            # Tính toán tiến độ
            progress = (goal.saved_amount / goal.target_amount) * 100
            is_achieved = goal.saved_amount >= goal.target_amount # Đạt mục tiêu hay chưa

            # Tính toán thời gian còn lại
            days_remaining = (goal.deadline - datetime.now().date()).days
            days_remaining = max(days_remaining, 0)  # Đảm bảo không âm

            # Tính toán số tiền cần tiết kiệm mỗi ngày
            amount_remaining = goal.target_amount - goal.saved_amount
            daily_saving = amount_remaining / days_remaining if days_remaining > 0 else 0

            # Trả về kết quả
            return {
                'message': 'Goal status retrieved successfully',
                'goal': {
                    'id': goal.id,
                    'name': goal.name,
                    'target_amount': float(goal.target_amount),
                    'saved_amount': float(goal.saved_amount),
                    'deadline': goal.deadline.isoformat(),
                    'progress': round(progress, 2),  # Tiến độ (%)
                    'is_achieved': is_achieved,  # Đã đạt được mục tiêu chưa
                    'days_remaining': days_remaining,  # Số ngày còn lại
                    'daily_saving': round(float(daily_saving), 2)  # Số tiền cần tiết kiệm mỗi ngày
                },
                'status_code': 200
            }

        except SQLAlchemyError as e:
            logger.error(f'Error retrieving goal status for goal ID {goal_id} and user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving goal status', 'status_code': 500}
        

    # Xoá tạm thời
    def soft_delete_goal_service(user_id, goal_id):
        logger.info(f'Soft deleting goal ID {goal_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            goal = WalletService.existence_check(Goal, goal_id, user_id, is_deleted=False)
            if not goal:
                logger.warning(f'Goal ID {goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            # Cập nhật db
            goal.is_deleted = True
            goal.deleted_at = datetime.utcnow()
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Goal ID {goal_id} soft deleted successfully for user ID {user_id}')
            return {'message': 'Goal soft deleted successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error soft deleting goal ID {goal_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while soft deleting goal', 'status_code': 500}
        

    # Khôi phục
    def restore_goal_service(user_id, goal_id):
        logger.info(f'Restoring goal ID {goal_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            goal = WalletService.existence_check(Goal, goal_id, user_id, is_deleted=True)
            if not goal:
                logger.warning(f'Goal ID {goal_id} not found for user ID {user_id}')
                return {'message': 'Goal not found', 'status_code': 404}
            
            # Cập nhật db
            goal.is_deleted = False
            goal.deleted_at = None
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Goal ID {goal_id} restored successfully for user ID {user_id}')
            return {'message': 'Goal restored successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error restoring goal ID {goal_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while restoring goal', 'status_code': 500}