import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the root directory of the project to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.deployment_service import DeploymentService
from app.models.models import Deployment, Cluster, User

@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@patch('app.services.deployment_service.Cluster.query')
def test_create_deployment_cluster_not_found(mock_cluster_query, app):
    with app.app_context():
        mock_cluster_query.filter_by.return_value.first.return_value = None

        with pytest.raises(ValueError) as excinfo:
            DeploymentService.create_deployment(
                name="Test Deployment",
                ram=512,
                cpu=2,
                gpu=1,
                priority=1,
                docker_path="path/to/docker",
                cluster_name="Nonexistent Cluster",
                created_by=1
            )
        assert str(excinfo.value) == "Cluster not found"