import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.cluster_service import ClusterService
from app.models.models import Cluster

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

@patch('app.services.cluster_service.db.session')
@patch('app.services.cluster_service.Cluster.query')
def test_create_cluster_success(mock_cluster_query, mock_db_session, app):
    with app.app_context():
        mock_cluster_query.filter_by.return_value.first.return_value = None
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None

        new_cluster = ClusterService.create_cluster(
            name="Test Cluster",
            total_ram=1024,
            total_cpu=4,
            total_gpu=1,
            created_by=1,
            organization_id=1
        )

        assert new_cluster.name == "Test Cluster"
        assert new_cluster.total_ram == 1024
        assert new_cluster.total_cpu == 4
        assert new_cluster.total_gpu == 1
        assert new_cluster.created_by == 1
        assert new_cluster.organization_id == 1
        mock_db_session.add.assert_called_once_with(new_cluster)
        mock_db_session.commit.assert_called_once()

@patch('app.services.cluster_service.Cluster.query')
def test_create_cluster_organization_not_joined(mock_cluster_query, app):
    with app.app_context():
        with pytest.raises(ValueError) as excinfo:
            ClusterService.create_cluster(
                name="Test Cluster",
                total_ram=1024,
                total_cpu=4,
                total_gpu=1,
                created_by=1,
                organization_id=None
            )
        assert str(excinfo.value) == "You need to join an organization to create a cluster"