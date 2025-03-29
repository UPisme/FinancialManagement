from extensions import db
from models import Category, Transaction
import logging
from sqlalchemy.exc import SQLAlchemyError
from .wallet_service import WalletService
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryService:
    # Tạo category mới
    def create_category_service(user_id, data):
        logger.info(f'Creating category for user ID {user_id}')

        try:
            # Kiểm tra các trường bắt buộc
            if not data or not data.get('name'):
                logger.warning(f'Missing required fields')
                return {'message': 'Category name is required', 'status_code': 400}
            
            # Kiểm tra trùng tên danh mục
            existing_category = Category.query.filter_by(user_id=user_id, name=data['name'], is_deleted=False).first()
            if existing_category:
                logger.warning(f'Category name {data["name"]} already exists')
                return {'message': 'Category name already exists', 'status_code': 409}
            
            # Kiểm tra category đã soft delete
            deleted_category = Category.query.filter_by(user_id=user_id, name=data['name'], is_deleted=True).first()
            if deleted_category:
                logger.info(f'Category {data["name"]} was soft deleted. Automatically restoring it.')
                # Khôi phục danh mục
                deleted_category.is_deleted = False
                deleted_category.deleted_at = None
                db.session.commit()

                return {
                    'message': 'Category was previously deleted but has been restored successfully',
                    'id': deleted_category.id,
                    'name': deleted_category.name,
                    'status_code': 200
                }

            # Tạo category
            new_category = Category (
                user_id = user_id,
                name = data['name']
            )
        
            # Thêm dữ liệu vào db
            db.session.add(new_category)
            db.session.commit()

            # Trả về category vừa tạo
            logger.info(f'Category created successfully for user ID {user_id}')
            return {
                'message': 'Category created successfully',
                'id': new_category.id,
                'name': new_category.name,
                'status_code': 201
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating category for user ID {user_id}: {e}")
            return {"message": "An error occurred while creating category", 'status_code': 500}
        
    
    # Lấy danh sách category
    def get_categories_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            categories = Category.query.filter_by(user_id=user_id, is_deleted=False).paginate(page=page, per_page=per_page, error_out=False)
            categories_list = [{'id': c.id, 'name': c.name} for c in categories.items]
            
            # Trả về danh sách category
            return {
                'categories': categories_list,
                'page': categories.page,
                'per_page': categories.per_page,
                'total_pages': categories.pages,
                'total_items': categories.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving categories for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving categories', 'status_code': 500}
        

    # Lấy danh sách category đã xoá
    def get_deleted_categories_service(user_id, page=1, per_page=10):
        try:
            # Phân trang
            categories = Category.query.filter_by(user_id=user_id, is_deleted=True).paginate(page=page, per_page=per_page, error_out=False)
            categories_list = [{'id': c.id, 'name': c.name} for c in categories.items]
            
            # Trả về danh sách category đã xoá
            return {
                'categories': categories_list,
                'page': categories.page,
                'per_page': categories.per_page,
                'total_pages': categories.pages,
                'total_items': categories.total,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving categories for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving categories', 'status_code': 500}
        
    
    # Lấy thông tin category
    def get_category_service(user_id, category_id):
        try:
            # Kiểm tra tồn tại
            category = WalletService.existence_check(Category, category_id, user_id, is_deleted=False)
            if not category:
                logger.warning(f'Category ID {category_id} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Trả về thông tin category
            return {
                'id': category.id,
                'name': category.name,
                'status_code': 200
            }
        
        except (SQLAlchemyError, ValueError) as e:
            logger.error(f'Error retrieving category for user ID {user_id}: {e}')
            return {'message': 'An error occurred while retrieving category', 'status_code': 500}
        

    # Cập nhật category
    def update_category_service(user_id, category_id, data):
        logger.info(f'Updating category ID {category_id} for user ID {user_id} with data {data}')

        try:
            # Kiểm tra tồn tại
            category = WalletService.existence_check(Category, category_id, user_id, is_deleted=False)
            if not category:
                logger.warning(f'Category ID {category_id} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Kiểm tra goal đã bị xóa chưa
            if category.is_deleted:
                logger.warning(f'Category ID {category_id} is deleted and cannot be updated')
                return {'message': 'Category is deleted and cannot be updated', 'status_code': 400}

            # Kiểm tra trùng tên            
            if 'name' in data:
                existing_category = Category.query.filter(Category.user_id == user_id, Category.name == data['name'], Category.is_deleted == False, Category.id != category_id).first()
                if existing_category:
                    logger.warning(f'Category name {data["name"]} already exists')
                    return {'message': 'Category name already exists', 'status_code': 409}
            
                category.name = data['name']

            # Commit vào db và trả về
            db.session .commit()
            logger.info(f'Category ID {category_id} updated successfully for user ID {user_id}')
            return {
                'message': 'Category updated successfully',
                'id': category.id,
                'name': category.name,
                'status_code': 200
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error updating category ID {category_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while updating category', 'status_code': 500}
        

    # Xoá category
    def delete_category_service(user_id, category_id):
        logger.info(f'Received request to delete category ID {category_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            category = WalletService.existence_check(Category, category_id, user_id, is_deleted=False)
            if not category:
                logger.warning(f'Category ID {category_id} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Xoá khỏi db
            db.session.delete(category)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Category ID {category_id} deleted successfully for user ID {user_id}')
            return {'message': 'Category deleted successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error deleting category ID {category_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while deleting category', 'status_code': 500}
        

    # Xoá tạm thời
    def soft_delete_category_service(user_id, category_id):
        logger.info(f'Soft deleting category ID {category_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            category = WalletService.existence_check(Category, category_id, user_id, is_deleted=False)
            if not category:
                logger.warning(f'Category ID {category_id} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Cập nhật db
            category.is_deleted = True
            category.deleted_at = datetime.utcnow()
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Category ID {category_id} soft deleted successfully for user ID {user_id}')
            return {'message': 'Category soft deleted successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error soft deleting category ID {category_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while soft deleting category', 'status_code': 500}
        

    # Khôi phục
    def restore_category_service(user_id, category_id):
        logger.info(f'Restoring category ID {category_id} for user ID {user_id}')

        try:
            # Kiểm tra tồn tại
            category = WalletService.existence_check(Category, category_id, user_id, is_deleted=True)
            if not category:
                logger.warning(f'Category ID {category_id} not found for user ID {user_id}')
                return {'message': 'Category not found', 'status_code': 404}
            
            # Cập nhật db
            category.is_deleted = False
            category.deleted_at = None
            db.session.commit()

            # Trả về kết quả
            logger.info(f'Category ID {category_id} restored successfully for user ID {user_id}')
            return {'message': 'Category restored successfully', 'status_code': 200}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error restoring category ID {category_id} for user ID {user_id}: {e}')
            return {'message': 'An error occurred while restoring category', 'status_code': 500}