from .redis_client import r
from .scheduling.deployment_dto import DeploymentDto

def add_deployment_to_redis(cluster_id, priority, deployment_id, cpu, ram, gpu):
    r.zadd(f"P{priority}:cluster:{cluster_id}:cpu", {deployment_id: cpu})
    r.zadd(f"P{priority}:cluster:{cluster_id}:ram", {deployment_id: ram})
    r.zadd(f"P{priority}:cluster:{cluster_id}:gpu", {deployment_id: gpu})

def remove_deployment_from_redis(cluster_id, priority, deployment_id):
    r.zrem(f"P{priority}:cluster:{cluster_id}:cpu", deployment_id)
    r.zrem(f"P{priority}:cluster:{cluster_id}:ram", deployment_id)
    r.zrem(f"P{priority}:cluster:{cluster_id}:gpu", deployment_id)

def fetch_deployments(cluster_id, priority, max_cpu, max_ram, max_gpu):
    # Fetch deployments within score limits
    cpu_deployments = r.zrangebyscore(f"P{priority}:cluster:{cluster_id}:cpu", 0, max_cpu)
    ram_deployments = r.zrangebyscore(f"P{priority}:cluster:{cluster_id}:ram", 0, max_ram)
    gpu_deployments = r.zrangebyscore(f"P{priority}:cluster:{cluster_id}:gpu", 0, max_gpu)

    # Find the intersection of all three sets
    deployment_ids = set(ram_deployments) & set(cpu_deployments) & set(gpu_deployments)

    # Fetch RAM, CPU, and GPU values for each deployment
    deployment_resources = []
    for deployment_id in deployment_ids:
        ram = r.zscore(f"P{priority}:cluster:{cluster_id}:ram", deployment_id)
        cpu = r.zscore(f"P{priority}:cluster:{cluster_id}:cpu", deployment_id)
        gpu = r.zscore(f"P{priority}:cluster:{cluster_id}:gpu", deployment_id)
        deployment_resources.append(DeploymentDto(deployment_id, ram, cpu, gpu))
    return deployment_resources
