from abc import ABC, abstractmethod

class SchedulingStrategy(ABC):
    @abstractmethod
    def schedule_deployments(self, node, deployments):
        pass