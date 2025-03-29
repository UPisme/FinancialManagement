from flask import request
from extensions import db
from models import User
import logging
from sqlalchemy.exc import SQLAlchemyError
from .auth_service import AuthService
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    # # Lấy danh sách users
    # def get_users_service():
    #     try:
    #         # Phân trang
    #         page = request.args.get('page', default=1, type=int)
    #         per_page = request.args.get('per_page', default=10, type=int)
            
    #         users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    #         users_list = [{'id': u.id, 'username': u.username} for u in users.items]
            
    #         return {
    #             'users': users_list,
    #             'page': users.page,
    #             'per_page': users.per_page,
    #             'total_pages': users.pages,
    #             'total_items': users.total,
    #             'status_code': 200
    #         }
        
    #     except (SQLAlchemyError, ValueError) as e:
    #         logger.error(f'Error retrieving users: {e}')
    #         return {'message': 'An error occurred while retrieving users', 'status_code': 500}
    

    # Lấy thông tin user
    def get_profile_service(user_id):
        try:
            # Kiểm tra tồn tại
            user = User.query.get(user_id)
            if not user:
                logger.warning(f'User ID {user_id} not found')
                return {'message': 'User not found', 'status_code': 404}
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving profile for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving user profile', 'status_code': 500}
        

    # Cập nhật profile
    def update_user_service(user_id, data):
        logger.info(f'Updating user ID {user_id} with data {data}')

        try:
            # Kiểm tra tồn tại
            user = User.query.get(user_id)
            if not user:
                logger.warning(f'User ID {user_id} not found')
                return {'message': 'User not found', 'status_code': 404}
            
            # Kiểm tra username
            if 'username' in data:
                user.username = data['username']

            # Kiểm tra định dạng email và trùng email
            if 'email' in data:
                if not AuthService.is_valid_email(data['email']):
                    logger.warning(f'Invalid email format: {data["email"]}')
                    return {'message': 'Invalid email format', 'status_code': 400}
                
                if User.query.filter(User.email == data['email'], User.id != user.id).first():
                    logger.warning(f'Email {data["email"]} already taken')
                    return {'message': 'Email already taken', 'status_code': 409}
                
                user.email = data['email']

            # Kiểm tra password
            if 'password' in data:
                if not AuthService.is_valid_password(data['password']):
                    logger.warning(f'Invalid password format')
                    return {'message': 'Password must be at least 8 characters, contain uppercase, lowercase, number, and special character', 'status_code': 400}
                
                if 'old_password' not in data:
                    logger.warning(f'Old password not provided')
                    return {'message': 'Old password is required', 'status_code': 400}
                
                if not user.check_password(data['old_password']):
                    logger.warning(f'Old password is incorrect')
                    return {'message': 'Old password is incorrect', 'status_code': 401}

                user.set_password(data['password'])

            # Commit vào db
            db.session.commit()

            # Trả về kết quả
            logger.info(f'User ID {user_id} updated successfully with data {data}')
            return {
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'status_code': 200
            }
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error updating user {user_id} with {data}: {e}')
            return {'message': 'An error occurred while updating user', 'status_code': 500}
        
    
    # Xoá user vĩnh viễn
    def delete_user_service(user_id):
        logger.info(f'Deleting user ID {user_id}')
        
        try:
            # Kiểm tra tồn tại
            user = User.query.get(user_id)
            if not user:
                logger.warning(f'User ID {user_id} not found')
                return {'message': 'User not found', 'status_code': 404}
            
            # Xoá trong db
            db.session.delete(user)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'User ID {user_id} deleted successfully')
            return {'message': 'User deleted successfully', 'status_code': 200}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error deleting user ID {user_id}: {e}')
            return {'message': 'An error occurred while deleting user', 'status_code': 500}
        

    # Xoá tạm thời
    def soft_delete_category_service(user_id):
        logger.info(f'Soft deleting user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            user = User.query.get(user_id)
            if not user:
                logger.warning(f'User ID {user_id} not found')
                return {'message': 'User not found', 'status_code': 404}
            
            # Cập nhật vào db
            user.active = False
            user.deleted_at = datetime.utcnow()
            db.session.commit()

            # Trả về kết quả
            logger.info(f'User ID {user_id} soft deleted successfully')
            return {'message': 'User soft deleted successfully', 'status_code': 200}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error soft deleting user ID {user_id}: {e}')
            return {'message': 'An error occurred while soft deleting user', 'status_code': 500}
        

