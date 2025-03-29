from extensions import db
from models import User
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
import re, logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    # Kiểm tra định dạng email
    def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None


    # Kiểm tra độ mạnh của password
    def is_valid_password(password):
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or \
        not re.search(r'\d', password) or not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?/~`-]', password):
            return False
        return True


    # Đăng ký tài khoản
    def user_register(data):
        logger.info(f'Received registration request: {data}')

        try:
            # Kiểm tra trường bắt buộc
            if not data.get('username'):
                logger.warning('Missing username field')
                return {'message': 'Username is required', 'status_code': 400}

            if not data.get('email'):
                logger.warning('Missing email field')
                return {'message': 'Email is required', 'status_code': 400}

            if not data.get('password'):
                logger.warning('Missing password field')
                return {'message': 'Password is required', 'status_code': 400}

            # Kiểm tra định dạng email
            if not AuthService.is_valid_email(data['email']):
                logger.warning(f'Invalid email format: {data["email"]}')
                return {'message': 'Invalid email format', 'status_code': 400}
            
            # Kiểm tra trùng email
            if User.query.filter_by(email=data['email']).first():
                logger.warning(f'Email {data["email"]} already exists')
                return {'message': 'Email already exists', 'status_code': 409}

            # Kiểm tra password
            if not AuthService.is_valid_password(data['password']):
                logger.warning(f'Invalid password format: {data["password"]}')
                return {'message': 'Password must be at least 8 characters, contain uppercase, lowercase, number, and special character', 'status_code': 400}
            
            # Tạo user mới
            new_user = User(username=data['username'], email=data['email'])
            new_user.set_password(data['password'])

            # Thêm vào db
            db.session.add(new_user)
            db.session.commit()

            # Trả về kết quả
            logger.info(f'User registration successfully')
            return {'message': 'User registered successfully', 'status_code': 201}
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error while registering user {data["username"]}: {e}')
            return {'message': 'An error occurred while registering', 'status_code': 500}
        
    
    # Đăng nhập
    def user_login(data):
        logger.info(f'Received login request: {data}')
        
        try:
            # Kiểm tra trường bắt buộc
            if not data or not data.get('email') or not data.get('password'):
                logger.warning(f'Missing required fields')
                return {'message': 'Missing required fields', 'status_code': 400}

            # Kiểm tra identifier (username hoặc email) và password
            user = User.query.filter_by(email=data.get('email')).first()
            if not user or not user.check_password(data.get('password')):
                logger.warning(f'Invalid email or password')
                return {'message': 'Invalid email or password', 'status_code': 401}
            
            # Nếu user đã yêu cầu xoá nhưng vẫn đăng nhập trong 30 ngày thì khôi phục tài khoản
            if not user.active and user.deleted_at:
                days_since_deleted = (datetime.utcnow() - user.deleted_at).days
                if days_since_deleted < 30:
                    user.active = True
                    user.deleted_at = None
                    db.session.commit()

            # Tạo jwt khi user đăng nhập
            token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=30))

            logger.info(f'Log in successfully')
            return {
                'token': token, 
                'message': 'User logged in successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'status_code': 200
            }

        except Exception as e:
            logger.error(f'Error while login: {e}')
            return {'message': 'An error occured while login', 'status_code': 500}
        
        
