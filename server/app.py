from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from server.config import DevelopmentConfig
from server.models import db, bcrypt
from server.routes.auth import auth_bp
from server.routes.admin import admin_bp
from server.routes.professor import professor_bp
from server.routes.aluno import aluno_bp
from server.routes.code import code_bp

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(professor_bp)
app.register_blueprint(aluno_bp)
app.register_blueprint(code_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
