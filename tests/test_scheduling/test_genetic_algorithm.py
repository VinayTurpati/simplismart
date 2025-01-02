import unittest
from app.scheduling.genetic_algorithm import GeneticAlgorithm
from app.scheduling.node import Node
from app.scheduling.deployment_dto import DeploymentDto
from copy import copy

class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        self.strategy = GeneticAlgorithm(generations=10, population_size=10)
        self.node = Node(id=1, cpu=10, memory=20, gpu=5)

    def test_no_deployments(self):
        deployments = []
        scheduled = self.strategy.schedule_deployments(copy(self.node), deployments)
        self.assertEqual(scheduled, [])


    def test_multiple_deployments_all_fit(self):
        deployments = [
            DeploymentDto(id=1, cpu=3, memory=5, gpu=1),
            DeploymentDto(id=2, cpu=4, memory=8, gpu=2),
            DeploymentDto(id=3, cpu=2, memory=4, gpu=1)
        ]
        scheduled = self.strategy.schedule_deployments(copy(self.node), deployments)
        self.assertEqual(len(scheduled), 3)
        self.assertEqual(set(d.id for d in scheduled), {1, 2, 3})

    def test_multiple_deployments_none_fit(self):
        deployments = [
            DeploymentDto(id=1, cpu=15, memory=25, gpu=10),
            DeploymentDto(id=2, cpu=12, memory=22, gpu=8)
        ]
        scheduled = self.strategy.schedule_deployments(copy(self.node), deployments)
        self.assertEqual(scheduled, [])

if __name__ == '__main__':
    unittest.main()