from flask import Flask
from config.config import Config
from extensions import db, jwt
from routes.__init__ import all_blueprints
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app) # Khởi tạo db
jwt.init_app(app)  # Khởi tạo JWT

# Đăng ký tất cả Blueprint
for bp in all_blueprints:
    app.register_blueprint(bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
