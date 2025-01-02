from copy import copy
from time import time

class Scheduler:
    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def schedule_deployments(self, node, deployments):
        st = time()
        scheduled_deployements = self.strategy.schedule_deployments(copy(node), deployments)
        for deployment in scheduled_deployements:
            node.schedule(deployment)
        rem_cpu = node.cpu
        rem_memory = node.memory
        rem_gpu = node
        print(f"Remaining CPU: {rem_cpu}, RAM: {rem_memory}, GPU: {rem_gpu}")
        tt = time() - st
        print("Deployments scheduled")
        print("Total time taken: {:.6f} seconds".format(tt))
        return scheduled_deployements