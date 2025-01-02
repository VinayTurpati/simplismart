from itertools import chain, combinations
from .strategy import SchedulingStrategy
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AllCombinations(SchedulingStrategy):
    def schedule_deployments(self, node, deployments):
        logger.info("Scheduling deployments using All Combinations with deployment size: %d", len(deployments))
        def is_valid_subset(subset):
            total_cpu = sum(d.cpu for d in subset)
            total_memory = sum(d.memory for d in subset)
            total_gpu = sum(d.gpu for d in subset)
            return (
                total_cpu <= node.cpu
                and total_memory <= node.memory
                and total_gpu <= node.gpu
            )

        all_subsets = chain.from_iterable(combinations(deployments, r) for r in range(len(deployments) + 1))
        best_subset = []
        for subset in all_subsets:
            if is_valid_subset(subset) and len(subset) > len(best_subset):
                best_subset = subset
        return best_subset