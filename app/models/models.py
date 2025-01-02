from datetime import datetime, timezone
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    role = db.Column(db.String(50), nullable=True, default='VIEWER')  # Add role field

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'organization_id': self.organization_id,
            'role': self.role  
        }

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    invite_code = db.Column(db.String(150), unique=True, nullable=False)
    users = db.relationship('User', backref='organization', lazy=True)
    clusters = db.relationship('Cluster', backref='organization', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'invite_code': self.invite_code
        }

class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    total_ram = db.Column(db.Integer, nullable=False)
    total_cpu = db.Column(db.Integer, nullable=False)
    total_gpu = db.Column(db.Integer, nullable=False)
    allocated_ram = db.Column(db.Integer, default=0)
    allocated_cpu = db.Column(db.Integer, default=0)
    allocated_gpu = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'total_ram': self.total_ram,
            'total_cpu': self.total_cpu,
            'total_gpu': self.total_gpu,
            'allocated_ram': self.allocated_ram,
            'allocated_cpu': self.allocated_cpu,
            'allocated_gpu': self.allocated_gpu,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'organization_id': self.organization_id
        }

class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    ram = db.Column(db.Integer, nullable=False)
    cpu = db.Column(db.Integer, nullable=False)
    gpu = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='queued')
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'), nullable=True)
    cluster = db.relationship('Cluster', backref='deployments')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ram': self.ram,
            'cpu': self.cpu,
            'gpu': self.gpu,
            'priority': self.priority,
            'status': self.status,
            'cluster_id': self.cluster_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by
        }