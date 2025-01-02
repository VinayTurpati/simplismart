import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_sqlalchemy import SQLAlchemy
import sys
import os

# Ensure the app module is correctly imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.jwt_utils import init_jwt, generate_token, protected_route
from app.models.models import User  # Import your User model

from app import db

class TestJWTUtils(unittest.TestCase):

    def setUp(self):
        # Set up Flask app with necessary configurations
        self.app = Flask(__name__)
        self.app.config['JWT_SECRET_KEY'] = 'test_secret_key'
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize extensions
        db.init_app(self.app)
        self.jwt = JWTManager(self.app)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create database tables
        with self.app.app_context():
            db.create_all()

        # Define the test route
        @self.app.route('/protected', methods=['GET'])
        @protected_route
        def protected(current_user):
            return jsonify({"message": "Success", "user_id": current_user.id})

    def tearDown(self):
        # Drop all tables and clean up the application context
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def test_init_jwt(self):
        jwt = init_jwt(self.app)
        self.assertIsInstance(jwt, JWTManager)

    def test_generate_token(self):
        token = generate_token(identity=1)
        self.assertIsInstance(token, str)
    
    @patch('app.jwt_utils.User.query.get')
    def test_protected_route_user_not_found(self, mock_get):
        mock_get.return_value = None

        access_token = create_access_token(identity=1)
        headers = {'Authorization': f'Bearer {access_token}'}

        response = self.client.get('/protected', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "User not found"})

if __name__ == '__main__':
    unittest.main()
