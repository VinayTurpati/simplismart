import json
import random
from app.models.models import db, Deployment, Cluster, User
from app.redis_client import r
from app.redis_helper import add_deployment_to_redis, remove_deployment_from_redis, fetch_deployments
from app.scheduling.all_combinations import AllCombinations
from app.scheduling.genetic_algorithm import GeneticAlgorithm
from app.scheduling.scheduler import Scheduler
from app.scheduling.node import Node
from copy import copy
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DeploymentService:
    priorities = [1, 0]
    @staticmethod
    def create_deployment(name, ram, cpu, gpu, priority, docker_path, cluster_name, created_by):
        logger.info("Creating deployment for cluster: %s", cluster_name)
        if not docker_path:
            raise ValueError("Docker path is required")
        
        if priority not in DeploymentService.priorities:
            logger.error("Invalid priority")
            raise ValueError("Invalid priority")
        
        cluster = Cluster.query.filter_by(name=cluster_name).first()
        if not cluster:
            logger.error("Cluster not found")
            raise ValueError("Cluster not found")
        
        user = User.query.get(created_by)
        if not user:
            logger.error("User not found")
            raise ValueError("User not found")
        
        if user.organization_id != cluster.organization_id:
            logger.error("User does not belong to the same organization as the cluster")
            raise ValueError("User does not belong to the same organization as the cluster")
        
        new_deployment = Deployment(name=name, ram=ram, cpu=cpu, gpu=gpu, priority=priority, cluster_id=cluster.id, status='queued', created_by=created_by)
        db.session.add(new_deployment)
        db.session.commit()

        if (cluster.allocated_ram + ram <= cluster.total_ram and
            cluster.allocated_cpu + cpu <= cluster.total_cpu and
            cluster.allocated_gpu + gpu <= cluster.total_gpu):
            cluster.allocated_ram += ram
            cluster.allocated_cpu += cpu
            cluster.allocated_gpu += gpu
            new_deployment.status = 'running'
            db.session.add(cluster)
            db.session.add(new_deployment)
            db.session.commit()

            ttl = DeploymentService.get_random_ttl()

            # Simulate deployment running on Redis which will complete after some random TTL
            r.setex(f"deployment:{new_deployment.id}", ttl, json.dumps({'deployment_id': new_deployment.id}))
            logger.info("Deployment is running")
            return new_deployment, "running"
        elif ram > cluster.total_ram or cpu > cluster.total_cpu or gpu > cluster.total_gpu:
            new_deployment.status = 'rejected'
            db.session.commit()
            logger.info("Resources requested are more than available resources")
            raise ValueError("Resources requested are more than available resources")
        else:
            new_deployment.status = 'queued'
            db.session.commit()
            add_deployment_to_redis(cluster.id, priority, new_deployment.id, new_deployment.cpu, new_deployment.ram, new_deployment.gpu)
            logger.info("Deployment queued to Redis")
            return new_deployment, "queued"

    @staticmethod
    def get_random_ttl():
        return random.randint(20, 30)
    
    @staticmethod
    def handle_expire_deployment(deployment_id):
        deployment = Deployment.query.get(deployment_id)
        cluster = Cluster.query.get(deployment.cluster.id)
        if deployment and deployment.status == 'running':
            cluster = deployment.cluster
            cluster.allocated_ram = max(0, cluster.allocated_ram-deployment.ram)
            cluster.allocated_cpu = max(0, cluster.allocated_cpu-deployment.cpu)
            cluster.allocated_gpu = max(0, cluster.allocated_gpu-deployment.gpu)
            deployment.status = 'done'
            db.session.commit()
            from app.services.deployment_service import DeploymentService
            DeploymentService.trigger_deployment_in_cluster(cluster.id)

    @staticmethod
    def trigger_deployment_in_cluster(cluster_id):
        logger.info(f"Processing queue for cluster: {cluster_id}" )

        for priority in DeploymentService.priorities:
            queue_length = r.zcard(f"P{priority}:cluster:{cluster_id}:cpu")
            logger.info(f"P{priority} Found queue length for : {queue_length}")
            if queue_length > 0:
                cluster = Cluster.query.get(cluster_id)
                if not cluster:
                    logger.info("Cluster not found")
                    return
                
                available_cpu = cluster.total_cpu - cluster.allocated_cpu
                available_ram = cluster.total_ram - cluster.allocated_ram
                available_gpu = cluster.total_gpu - cluster.allocated_gpu
                logger.info(f"For cluster {cluster_id}, allocated resources: CPU={cluster.allocated_cpu}, RAM={cluster.allocated_ram}, GPU={cluster.allocated_gpu}")
                
                deployments = fetch_deployments(cluster_id, priority, available_cpu, available_ram, available_gpu)
                len_deployments = len(deployments)
                if(len_deployments == 0):
                    logger.info("No deployments to schedule")
                    return
                
                # Dynamic strategy selection based on number of deployments
                if(len_deployments < 10):
                    strategy = AllCombinations()
                else:
                    strategy = GeneticAlgorithm(generations=10, population_size=10)
                    
                scheduler = Scheduler(strategy=strategy)
                node = Node(id=cluster_id, cpu=available_cpu, memory=available_ram, gpu=available_gpu)
                scheduled_deployments = scheduler.schedule_deployments(copy(node), deployments)
                for dp in scheduled_deployments:
                    logger.info(f"Scheduled deployment: {dp}")

                for scheduled_deployment_dto in scheduled_deployments:
                    try:
                        deployment = Deployment.query.get(int(scheduled_deployment_dto.id))
                        if not deployment:
                            logger.info(f"Deployment with ID {scheduled_deployment_dto.id} not found")
                            continue

                        if not deployment.cluster:
                            logger.info(f"Cluster for deployment ID {deployment.id} not found")
                            continue

                        if (cluster.allocated_ram + deployment.ram <= cluster.total_ram and
                            cluster.allocated_cpu + deployment.cpu <= cluster.total_cpu and
                            cluster.allocated_gpu + deployment.gpu <= cluster.total_gpu):
                            cluster.allocated_ram += deployment.ram
                            cluster.allocated_cpu += deployment.cpu
                            cluster.allocated_gpu += deployment.gpu
                            deployment.status = 'running'
                            db.session.commit()
                            remove_deployment_from_redis(cluster_id, priority, deployment.id)

                            # Save deployment in Redis with random TTL
                            ttl = DeploymentService.get_random_ttl()  # TTL between 20 and 30 seconds
                            r.setex(f"deployment:{deployment.id}", ttl, json.dumps({'deployment_id': deployment.id}))
                            logger.info(f"Deployment ID {deployment.id} is running")
                        else:
                            logger.info(f"Insufficient resources for deployment ID {deployment.id}")
                            return
                            # r.lpush('deployment_queue', json.dumps({'deployment_id': deployment.id, 'priority': deployment.priority}))
                    except Exception as e:
                        logger.info("Error processing deployment: {e}")
                if(len_deployments > len(scheduled_deployments)):
                    logger.info("Some high priority deployments could not be scheduled")
                    return
        logger.info("Queue processed")