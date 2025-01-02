import sys
import os

# Ensure the app module is correctly imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.services.user_service import UserService
from app.models.models import User, Organization

class TestUserService(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

        with self.app.app_context():
            self.db.create_all()

    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()
        self.app_context.pop()

    @patch('app.services.user_service.User.query')
    @patch('app.services.user_service.db.session')
    def test_register_user_success(self, mock_db_session, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = None
        mock_user_query.count.return_value = 0

        new_user = UserService.register_user('testuser', 'testpassword')

        self.assertEqual(new_user.username, 'testuser')
        self.assertEqual(new_user.role, 'ADMIN')
        mock_db_session.add.assert_called_once_with(new_user)
        mock_db_session.commit.assert_called_once()

    @patch('app.services.user_service.User.query')
    def test_register_user_already_exists(self, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = MagicMock()

        with self.assertRaises(ValueError) as context:
            UserService.register_user('testuser', 'testpassword')

        self.assertEqual(str(context.exception), "User already exists")

    @patch('app.services.user_service.User.query')
    @patch('app.services.user_service.db.session')
    def test_register_user_db_exception(self, mock_db_session, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = None
        mock_user_query.count.return_value = 0
        mock_db_session.commit.side_effect = Exception("DB Error")

        with self.assertRaises(Exception) as context:
            UserService.register_user('testuser', 'testpassword')

        self.assertEqual(str(context.exception), "DB Error")

    @patch('app.services.user_service.User.query')
    def test_authenticate_user_success(self, mock_user_query):
        user = MagicMock()
        user.password = 'hashedpassword'
        mock_user_query.filter_by.return_value.first.return_value = user

        with patch('app.services.user_service.check_password_hash', return_value=True):
            authenticated_user = UserService.authenticate_user('testuser', 'testpassword')

        self.assertEqual(authenticated_user, user)

    @patch('app.services.user_service.User.query')
    def test_authenticate_user_invalid_credentials(self, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            UserService.authenticate_user('testuser', 'testpassword')

        self.assertEqual(str(context.exception), "Invalid credentials")

    @patch('app.services.user_service.User.query')
    @patch('app.services.user_service.Organization.query')
    @patch('app.services.user_service.db.session')
    def test_join_organization_success(self, mock_db_session, mock_org_query, mock_user_query):
        user = MagicMock()
        organization = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = user
        mock_org_query.filter_by.return_value.first.return_value = organization

        updated_user = UserService.join_organization(1, 'invitecode')

        self.assertEqual(updated_user.organization_id, organization.id)
        mock_db_session.commit.assert_called_once()

    @patch('app.services.user_service.User.query')
    def test_join_organization_user_not_found(self, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            UserService.join_organization(1, 'invitecode')

        self.assertEqual(str(context.exception), "User not found")

    @patch('app.services.user_service.User.query')
    @patch('app.services.user_service.Organization.query')
    def test_join_organization_invalid_invite_code(self, mock_org_query, mock_user_query):
        user = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = user
        mock_org_query.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            UserService.join_organization(1, 'invitecode')

        self.assertEqual(str(context.exception), "Invalid invite code")

    @patch('app.services.user_service.User.query')
    def test_change_user_role_not_admin(self, mock_user_query):
        # Mock a non-admin user
        user = MagicMock()
        user.role = 'VIEWER'
        mock_user_query.filter_by.return_value.first.return_value = user

        with self.assertRaises(ValueError) as context:
            UserService.change_user_role(1, 2, 'DEVELOPER')

        self.assertEqual(str(context.exception), "Only ADMIN users can change roles")

if __name__ == '__main__':
    unittest.main()