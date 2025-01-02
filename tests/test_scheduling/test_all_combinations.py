import unittest
from app.scheduling.all_combinations import AllCombinations
from app.scheduling.node import Node
from app.scheduling.deployment_dto import DeploymentDto

class TestAllCombinations(unittest.TestCase):
    def setUp(self):
        self.strategy = AllCombinations()
        self.node = Node(id=1, cpu=10, memory=20, gpu=5)

    def test_no_deployments(self):
        deployments = []
        scheduled = self.strategy.schedule_deployments(self.node, deployments)
        self.assertEqual(scheduled, [])

    def test_single_deployment_fits(self):
        deployments = [DeploymentDto(id=1, cpu=5, memory=10, gpu=2)]
        scheduled = self.strategy.schedule_deployments(self.node, deployments)
        self.assertEqual(len(scheduled), 1)
        self.assertEqual(scheduled[0].id, 1)

    def test_single_deployment_does_not_fit(self):
        deployments = [DeploymentDto(id=1, cpu=15, memory=25, gpu=10)]
        scheduled = self.strategy.schedule_deployments(self.node, deployments)
        self.assertEqual(scheduled, [])

    def test_multiple_deployments_all_fit(self):
        deployments = [
            DeploymentDto(id=1, cpu=3, memory=5, gpu=1),
            DeploymentDto(id=2, cpu=4, memory=8, gpu=2),
            DeploymentDto(id=3, cpu=2, memory=4, gpu=1)
        ]
        scheduled = self.strategy.schedule_deployments(self.node, deployments)
        self.assertEqual(len(scheduled), 3)
        self.assertEqual(set(d.id for d in scheduled), {1, 2, 3})

    def test_multiple_deployments_some_fit(self):
        deployments = [
            DeploymentDto(id=1, cpu=3, memory=5, gpu=1),
            DeploymentDto(id=2, cpu=4, memory=8, gpu=2),
            DeploymentDto(id=3, cpu=10, memory=20, gpu=5)
        ]
        scheduled = self.strategy.schedule_deployments(self.node, deployments)
        self.assertEqual(len(scheduled), 2)
        self.assertEqual(set(d.id for d in scheduled), {1, 2})

    def test_multiple_deployments_none_fit(self):
        deployments = [
            DeploymentDto(id=1, cpu=15, memory=25, gpu=10),
            DeploymentDto(id=2, cpu=12, memory=22, gpu=8)
        ]
        scheduled = self.strategy.schedule_deployments(self.node, deployments)
        self.assertEqual(scheduled, [])

if __name__ == '__main__':
    unittest.main()