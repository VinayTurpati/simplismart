import unittest
from unittest.mock import patch, MagicMock
from app.redis_helper import add_deployment_to_redis, remove_deployment_from_redis, fetch_deployments
from app.scheduling.deployment_dto import DeploymentDto

class TestRedisHelper(unittest.TestCase):

    @patch('app.redis_helper.r')
    def test_add_deployment_to_redis(self, mock_redis):
        add_deployment_to_redis(1, 0, 123, 4, 1024, 1)
        mock_redis.zadd.assert_any_call('P0:cluster:1:cpu', {123: 4})
        mock_redis.zadd.assert_any_call('P0:cluster:1:ram', {123: 1024})
        mock_redis.zadd.assert_any_call('P0:cluster:1:gpu', {123: 1})

    @patch('app.redis_helper.r')
    def test_remove_deployment_from_redis(self, mock_redis):
        remove_deployment_from_redis(1, 0, 123)
        mock_redis.zrem.assert_any_call('P0:cluster:1:cpu', 123)
        mock_redis.zrem.assert_any_call('P0:cluster:1:ram', 123)
        mock_redis.zrem.assert_any_call('P0:cluster:1:gpu', 123)

    @patch('app.redis_helper.r')
    def test_fetch_deployments(self, mock_redis):
        mock_redis.zrangebyscore.side_effect = [
            [b'123', b'124'],  # CPU deployments
            [b'123'],          # RAM deployments
            [b'123', b'125']   # GPU deployments
        ]
        mock_redis.zscore.side_effect = [1024, 4, 1]

        deployments = fetch_deployments(1, 0, 4, 1024, 1)
        self.assertEqual(len(deployments), 1)
        self.assertEqual(deployments[0].id, b'123')


if __name__ == '__main__':
    unittest.main()