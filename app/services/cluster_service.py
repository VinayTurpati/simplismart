import logging
from app.models.models import db, Cluster

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ClusterService:
    @staticmethod
    def create_cluster(name, total_ram, total_cpu, total_gpu, created_by, organization_id):
        logger.info("Creating cluster")
        if(organization_id is None):
            logger.warning("You need to join an organization to create a cluster")
            raise ValueError("You need to join an organization to create a cluster")
        if Cluster.query.filter_by(name=name).first():
            logger.warning("Cluster already exists")
            raise ValueError("Cluster already exists")
        
        new_cluster = Cluster(name=name, total_ram=total_ram, total_cpu=total_cpu, total_gpu=total_gpu, created_by=created_by, organization_id=organization_id)
        db.session.add(new_cluster)
        db.session.commit()
        logger.info(f"Cluster created: {new_cluster.name}")
        return new_cluster

    @staticmethod
    def get_all_clusters():
        return Cluster.query.all()