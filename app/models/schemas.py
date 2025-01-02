from marshmallow import Schema, fields, ValidationError

# Schemas for validation
class RegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class JoinOrganizationSchema(Schema):
    invite_code = fields.Str(required=True)

class CreateClusterSchema(Schema):
    name = fields.Str(required=True)
    total_ram = fields.Int(required=True)
    total_cpu = fields.Int(required=True)
    total_gpu = fields.Int(required=True)

class CreateDeploymentSchema(Schema):
    name = fields.Str(required=True)
    ram = fields.Int(required=True)
    cpu = fields.Int(required=True)
    gpu = fields.Int(required=True)
    priority = fields.Int(required=True)
    docker_path = fields.Str(required=True)
    cluster_name = fields.Str(required=True)