from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Bảng Người dùng
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    wallets = db.relationship('Wallet', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Bảng Ví tiền
class Wallet(db.Model):
    __tablename__ = 'wallets'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Numeric(15,2), default=0)
    currency = db.Column(db.String(10), default='VND')
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    transactions = db.relationship('Transaction', backref='wallet', lazy=True)

# Bảng Mục tiêu tài chính
class Goal(db.Model):
    __tablename__ = 'goals'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    target_amount = db.Column(db.Numeric(15,2), nullable=False)
    saved_amount = db.Column(db.Numeric(15,2), default=0)
    deadline = db.Column(db.Date, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    transactions = db.relationship('Transaction', backref='goal', lazy=True)

# Bảng Danh mục giao dịch
class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    transactions = db.relationship('Transaction', backref='category', lazy=True)

# Bảng Giao dịch
class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    amount = db.Column(db.Numeric(15,2), nullable=False)
    transaction_type = db.Column(db.Enum('Income', 'Expense', name='transaction_type_enum'), nullable=False)
    note = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

# Bảng Ngân sách
class Budget(db.Model):
    __tablename__ = 'budgets'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(15,2), nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    end_date = db.Column(db.Date, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, user_id, category_id, start_date=None, end_date=None):
        self.user_id = user_id
        self.category_id = category_id
        self.start_date = start_date if start_date else datetime.date.today()
        self.end_date = end_date if end_date else (self.start_date + datetime.timedelta(days=30))

