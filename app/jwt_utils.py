import datetime, os
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request
from functools import wraps
from app.models.models import User

def init_jwt(app):
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', default='test')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8760)
    jwt = JWTManager(app)
    return jwt

def generate_token(identity):
    return create_access_token(identity=identity)

def protected_route(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({"message": "User not found"}), 404
        return fn(current_user=current_user, *args, **kwargs)
    return wrapper