class Node:
    def __init__(self, id, cpu, memory, gpu):
        self.id = id
        self.cpu = cpu
        self.memory = memory
        self.gpu = gpu

    def can_schedule(self, deployment):
        return (
            self.cpu >= deployment.cpu
            and self.memory >= deployment.memory
            and self.gpu >= deployment.gpu
        )

    def schedule(self, deployment):
        if self.can_schedule(deployment):
            self.cpu -= deployment.cpu
            self.memory -= deployment.memory
            self.gpu -= deployment.gpu
            return True
        return False