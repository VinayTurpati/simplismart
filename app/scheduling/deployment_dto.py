class DeploymentDto:
    def __init__(self, id, cpu, memory, gpu):
        self.id = id
        self.cpu = cpu
        self.memory = memory
        self.gpu = gpu