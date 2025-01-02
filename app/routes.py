from flask import request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.schemas import *
from app.models.models import db, User, Organization, Cluster, Deployment
from app.services.user_service import UserService
from app.services.cluster_service import ClusterService
from app.services.deployment_service import DeploymentService
from app.jwt_utils import init_jwt, generate_token, protected_route
from app.utils import generate_invite_code

import logging

jwt = init_jwt(app)

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/register', methods=['POST'])
def register():
    logger.info("Register endpoint called")
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        RegisterSchema().load(data)
        user = UserService.register_user(data['username'], data['password'])
        logger.info(f"User registered successfully: {user.username}")
        return jsonify({"message": "User registered successfully"}), 201
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        logger.error(f"Error registering user: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    logger.info("Login endpoint called")
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        LoginSchema().load(data)
        user = UserService.authenticate_user(data['username'], data['password'])
        token = generate_token(identity=user.id)
        logger.info(f"User logged in successfully: {user.username}")
        return jsonify({"message": "Logged in successfully", "token": token}), 200
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 401
    except Exception as err:
        logger.error(f"Error logging in user: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/join_organization', methods=['POST'])
@protected_route
def join_organization(current_user):
    logger.info(f"Join organization endpoint called by user: {current_user.username}")
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        JoinOrganizationSchema().load(data)
        user = UserService.join_organization(current_user.id, data['invite_code'])
        logger.info(f"User {current_user.username} joined organization successfully")
        return jsonify({"message": "Joined organization successfully"}), 200
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        logger.error(f"Error joining organization: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/create_cluster', methods=['POST'])
@protected_route
def create_cluster(current_user):
    logger.info(f"Create cluster endpoint called by user: {current_user.username}")
    if(current_user.role == 'VIEWER'):
        logger.warning(f"User {current_user.username} with role VIEWER attempted to create a cluster")
        return jsonify({"message": "Only ADMIN and DEVELOPER can create clusters"}), 403
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        CreateClusterSchema().load(data)
        cluster = ClusterService.create_cluster(data['name'], data['total_ram'], data['total_cpu'], data['total_gpu'], current_user.id, current_user.organization_id)
        logger.info(f"Cluster created successfully: {cluster.name}")
        return jsonify({"message": "Cluster created successfully"}), 201
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        logger.error(f"Error creating cluster: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/create_deployment', methods=['POST'])
@protected_route
def create_deployment(current_user):
    logger.info(f"Create deployment endpoint called by user: {current_user.username}")
    if(current_user.role == 'VIEWER'):
        logger.warning(f"User {current_user.username} with role VIEWER attempted to create a deployment")
        return jsonify({"message": "Only ADMIN and DEVELOPER can create deployment"}), 403
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        CreateDeploymentSchema().load(data)
        deployment, status = DeploymentService.create_deployment(
            data['name'], data['ram'], data['cpu'], data['gpu'], data['priority'], data['docker_path'], data['cluster_name'], current_user.id
        )
        logger.info(f"Deployment created and {status}: {deployment.name}")
        return jsonify({"message": f"Deployment created and {status}"}), 201
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        logger.error(f"Error creating deployment: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/trigger_deployment', methods=['POST'])
@protected_route
def trigger_deployment(current_user):
    logger.info(f"Process queue endpoint called by user: {current_user.username}")
    if(current_user.role == 'VIEWER'):
        logger.warning(f"User {current_user.username} with role VIEWER attempted to process queue")
        return jsonify({"message": "Only ADMIN and DEVELOPER can create deployment"}), 403
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        cluster_id = data.get('cluster_id')
        DeploymentService.trigger_deployment_in_cluster(cluster_id)
        logger.info(f"Queue processed for cluster ID: {cluster_id}")
        return jsonify({"message": "Queue processed"}), 200
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        logger.error(f"Error processing queue: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/clusters', methods=['GET'])
@protected_route
def get_clusters(current_user):
    logger.info(f"Get clusters endpoint called by user: {current_user.username}")
    try:
        clusters = ClusterService.get_all_clusters()
        logger.info(f"Clusters retrieved successfully")
        return jsonify([cluster.to_dict() for cluster in clusters]), 200
    except Exception as err:
        logger.error(f"Error fetching clusters: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/deployments', methods=['GET'])
@protected_route
def get_deployments(current_user):
    logger.info(f"Get deployments endpoint called by user: {current_user.username}")
    try:
        deployments = Deployment.query.all()
        logger.info(f"Deployments retrieved successfully")
        return jsonify([deployment.to_dict() for deployment in deployments]), 200
    except Exception as err:
        logger.error(f"Error fetching deployments: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/create_organization', methods=['POST'])
@protected_route
def create_organization(current_user):
    logger.info(f"Create organization endpoint called by user: {current_user.username}")
    if(current_user.role != 'ADMIN'):
        logger.warning(f"User {current_user.username} with role {current_user.role} attempted to create an organization")
        return jsonify({"message": "Only ADMIN can create organization"}), 403
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        invite_code = generate_invite_code()
        organization_name = data.get('name')
        org = Organization.query.filter_by(name=organization_name).first()
        if(org is not None):
            logger.warning(f"Organization name already exists: {organization_name}")
            return jsonify({"message": "Organization name already exists"}), 400
        organization = Organization(name = organization_name, invite_code = invite_code)
        db.session.add(organization)
        db.session.commit()
        logger.info(f"Organization created successfully: {organization.name}")
        return jsonify({"message": "Organization created successfully", "invite_code": invite_code}), 200
    except Exception as err:
        logger.error(f"Error creating organization: {err}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/update_role', methods=['POST'])
@protected_route
def update_role(current_user):
    logger.info(f"Update role endpoint called by user: {current_user.username}")
    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        target_user_id = data.get('user_id')
        new_role = data.get('role')
        
        if not target_user_id or not new_role:
            logger.warning("User ID and role are required")
            return jsonify({"message": "User ID and role are required"}), 400
        
        updated_user = UserService.change_user_role(current_user.id, target_user_id, new_role)
        logger.info(f"User role updated successfully: {updated_user.username} to {new_role}")
        return jsonify({"message": "User role updated successfully", "user": updated_user.to_dict()}), 200
    except ValidationError as err:
        logger.warning(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except ValueError as err:
        logger.warning(f"Value error: {err}")
        return jsonify({"message": str(err)}), 400
    except Exception as err:
        logger.error(f"Error changing user role: {err}")
        return jsonify({"message": "Internal server error"}), 500
        