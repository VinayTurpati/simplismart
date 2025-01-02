import logging
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.models import db, User, Organization

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class UserService:
    @staticmethod
    def register_user(username, password):
        logger.info("Attempting to register a new user: %s", username)

        if User.query.filter_by(username=username).first():
            logger.warning("Registration failed: User '%s' already exists", username)
            raise ValueError("User already exists")
        
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)

        if User.query.count() == 0:
            new_user.role = 'ADMIN'
            logger.info("First user registered. Role set to ADMIN.")

        db.session.add(new_user)
        db.session.commit()

        logger.info("User '%s' registered successfully", username)
        return new_user

    @staticmethod
    def authenticate_user(username, password):
        logger.info("Authenticating user: %s", username)

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            logger.warning("Authentication failed for user: %s", username)
            raise ValueError("Invalid credentials")

        logger.info("User '%s' authenticated successfully", username)
        return user

    @staticmethod
    def join_organization(id, invite_code):
        logger.info("User ID %d attempting to join organization with invite code: %s", id, invite_code)

        user = User.query.filter_by(id=id).first()
        if not user:
            logger.error("Join organization failed: User with ID %d not found", id)
            raise ValueError("User not found")

        organization = Organization.query.filter_by(invite_code=invite_code).first()
        if not organization:
            logger.error("Join organization failed: Invalid invite code '%s'", invite_code)
            raise ValueError("Invalid invite code")

        user.organization_id = organization.id
        db.session.commit()

        logger.info("User ID %d successfully joined organization ID %d", id, organization.id)
        return user

    @staticmethod
    def change_user_role(admin_user_id, target_user_id, new_role):
        logger.info(
            "Admin user ID %d attempting to change role of user ID %d to '%s'", 
            admin_user_id, target_user_id, new_role
        )

        admin_user = User.query.filter_by(id=admin_user_id).first()
        if not admin_user or admin_user.role != 'ADMIN':
            logger.error("Role change failed: User ID %d is not an ADMIN", admin_user_id)
            raise ValueError("Only ADMIN users can change roles")

        target_user = User.query.filter_by(id=target_user_id).first()
        if not target_user:
            logger.error("Role change failed: Target user ID %d not found", target_user_id)
            raise ValueError("Target user not found")

        if new_role not in ['ADMIN', 'DEVELOPER', 'VIEWER']:
            logger.error("Role change failed: Invalid role '%s'", new_role)
            raise ValueError("Invalid role")

        target_user.role = new_role
        db.session.commit()

        logger.info(
            "Role of user ID %d successfully changed to '%s' by admin user ID %d", 
            target_user_id, new_role, admin_user_id
        )
        return target_user
