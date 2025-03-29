from .auth_routes import auth_bp
from .user_routes import user_bp
from .wallet_routes import wallet_bp
from .goal_routes import goal_bp
from .category_routes import category_bp
from .transaction_routes import transaction_bp
from .budget_routes import budget_bp

# Danh sách các Blueprint
all_blueprints = [
    auth_bp,
    user_bp,
    wallet_bp,
    goal_bp,
    category_bp,
    transaction_bp,
    budget_bp
]