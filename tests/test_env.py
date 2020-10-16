from comgames.AI.env import Env

import unittest

class TestTictactoeEnv(unittest.TestCase):
    def setUp(self):
        self.env = Env("tictactoe")

    def test_observation(self):
        observation = self.env.observation()
        self.assertEqual(observation, [0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_actions(self):
        test_state = [1, 2, 0, 1, 2, 0, 1, 2, 0]
        actions = self.env.actions(test_state)
        self.assertEqual(actions, [
            (0, 2), (1, 2), (2, 2)
        ])


class TestFourinarowEnv(unittest.TestCase):
    def setUp(self):
        self.env = Env("fourinarow")

    def test_observation(self):
        observation = self.env.observation()
        self.assertEqual(observation, [0 for _ in range(7*7)])

    def test_actions(self):
        test_state = [0 for _ in range(7*7)]
        actions = self.env.actions(test_state)
        self.assertEqual(actions, [
            i for i in range(7)
        ])
        test_state[0] = 1
        self.assertEqual(self.env.actions(test_state), [i for i in range(1, 7)])
        test_state[1] = 1
        self.assertEqual(self.env.actions(test_state), [i for i in range(2, 7)])
        test_state[2:7] = [1 for _ in range(7 - 2)]
        self.assertEqual(self.env.actions(test_state), [])
