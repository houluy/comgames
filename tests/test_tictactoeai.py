from comgames.AI.tictactoeai import Q

import unittest


class TestQDict(unittest.TestCase):
    def test_Q(self):
        self.q = Q()
        self.assertEqual(self.q[([1, 2, 3], 2)], 0)
        key = ('123', (1, 2))
        self.assertEqual(self.q[key], 0)
        self.q[key] = 15
        self.assertEqual(self.q[key], 15)

        key = [1, 1, 1, 2, 1, 1, 2, 2, 2]
        self.assertEqual(self.q[(key,)], 0)

    def test_Q_update(self):
        self.q = Q()
        state = [1, 2, 3]
        action = (1, 2)
        reward = 10
        next_state = [1, 3, 4]
        actions = [(1, 3), (1, 4)]
        self.q.update(state, action, next_state, reward, actions)
        self.assertEqual(self.q[(state, action)], 1.0)
        self.q.update_terminal(next_state, reward)
        self.assertEqual(self.q[(next_state,)], 1.0)
        state = [0, 1, 2]
        action = (2, 1)
        nstate = [1, 2, 3]
        actions = [(1, 2), (1, 4)]
        reward = 1
        self.q.update(state, action, nstate, reward, actions)
        self.assertEqual(self.q[(state, action)], 0.199)

