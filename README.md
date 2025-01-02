# Simplismart

 Flask-based application handles user registration, authentication, organization management, cluster management, and deployment management. With support for role-based access control and Redis-powered deployment queue handling efficiently.

---

## Features
- **User Registration and Authentication**: Secure user onboarding and access.
- **Organization Management**: Create and manage organizations.
- **Cluster Management**: Simplify cluster creation and management.
- **Deployment Management**: Manage deployments effectively.
- **Role-Based Access Control (RBAC)**: Roles include ADMIN, DEVELOPER, and VIEWER.
- **Redis Integration**: Efficient deployment queue handling with Redis. And efficiently scheduled deploments from queue by using Genetic Algorithm and combinations.

NOTE: 
* Simulated deployment by sending deployment details to redis with random TTL, when it expires we will trigger new deployment from queue of same cluster.
* Deployments are scheduled dynamically: for fewer than 10 in cluster queue, we select the optimal combination of all combinations; for more than 10, we use a genetic algorithm for efficiency.
* Support two priorities HIGH(1) and LOW(0)

---

## Installation

### Prerequisites
- Python 3.9+
- Docker
- Docker Compose

### Setup using Docker
To build and run the application using Docker:
```bash
docker-compose up --build
```
or 
```bash
docker compose up --build
```
---

## API Endpoints

### User Management
- **User Registration**
  - Endpoint: `/register`
  - Method: `POST`
  - Description: Register a new user with the default role of VIEWER.
    ```
    curl --location 'http://localhost:5002/register' \
    --header 'Content-Type: application/json' \
    --data '{"username": "vinay3", "password": "test1"}'
    ```

- **User Login**
  - Endpoint: `/login`
  - Method: `POST`
  - Description: Authenticate a user and return a JWT token.
    ```
    curl --location 'http://localhost:5002/login' \
    --header 'Content-Type: application/json' \
    --data '{"username": "vinay3", "password": "test1"}'
    ```

- **Update User Role** (ADMIN only)
  - Endpoint: `/update_role`
  - Method: `POST`
  - Description: Change the role of a any user .
    ```
    curl --location 'http://localhost:5002/update_role' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw' \
    --header 'Content-Type: application/json' \
    --data '{"user_id": 1,"role":"ADMIN"}'
    ```

### Organization Management
- **Create Organization** (ADMIN only)
  - Endpoint: `/create_organization`
  - Method: `POST`
  - Description: Create a new organization.

    ```
    curl --location 'http://localhost:5002/create_organization' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw' \
    --header 'Content-Type: application/json' \
    --data '{ "name": "org4" }'
    ```
    
- **Join Organization**
  - Endpoint: `/join_organization`
  - Method: `POST`
  - Description: Join an organization using an invite code.
    ```
    curl --location 'http://localhost:5002/join_organization' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw' \
    --header 'Content-Type: application/json' \
    --data '{"invite_code": "GI3DBA"}'
    ```

### Cluster Management
- **Create Cluster** (ADMIN and DEVELOPER)
  - Endpoint: `/create_cluster`
  - Method: `POST`
  - Description: Create a new cluster with CPU, RAM and GPU resources.
    ```
    curl --location 'http://localhost:5002/create_cluster' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw' \
    --header 'Content-Type: application/json' \
    --data '{
        "name": "cluser1",
        "total_cpu": 10,
        "total_ram": 10,
        "total_gpu": 10
    }'
    ```

- **Get Clusters**
  - Endpoint: `/clusters`
  - Method: `GET`
  - Description: Retrieve all clusters.
    ```
    curl --location 'http://localhost:5002/clusters' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw'
    ```


### Deployment Management
- **Create Deployment** (ADMIN and DEVELOPER)
  - Endpoint: `/create_deployment`
  - Method: `POST`
  - Description: Create a new deployment.
      ```
      curl --location 'http://localhost:5002/create_deployment' \
      --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw' \
      --header 'Content-Type: application/json' \
      --data '{
        "name": "deployment1",
        "ram": 2,
        "cpu": 5,
        "gpu": 2,
        "priority": 1,
        "cluster_name": "cluser1",
        "docker_path": "https://sampledockerpath/DockerFile"
      }'
      ```

- **Get Deployments**
  - Endpoint: `/deployments`
  - Method: `GET`
  - Description: Retrieve all deployments.
    ```
    curl --location 'http://localhost:5002/deployments' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNTQ5OTYyOCwianRpIjoiNjI3ZDA0YmItNTc0MS00M2QzLThkZmItMzFkMmY2YTE4MzYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM1NDk5NjI4LCJleHAiOjE3NjcwMzU2Mjh9.TBP9OLG1vdwEkRNA1egKO_sg2hpOB1zD8FOdd73zNpw'
    ```

---

## Role-Based Access Control
- **ADMIN**: Full access to all features, including managing users, organizations, clusters, and deployments.
- **DEVELOPER**: Can create clusters and deployments.
- **VIEWER**: Can view clusters and deployments.

---

## Redis Integration
Redis is utilized for handling deployment queues. The application listens for expired keys in Redis and automatically processes deployment queues, ensuring smooth and efficient operations.

---

## Running Tests
To run the test suite, use the following command:
```bash
pytest
```
