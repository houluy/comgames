from collections import UserDict
from collections.abc import Iterable, MutableSequence


class Q(UserDict):
    def __init__(self, gamma=0.9999, alpha=0.9):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha

    def __str__(self):
        ret_str = []
        for key, value in self.data.items():
            try:
                ret_str.append(f"State: {key[0]}, action: {key[1]}, Q: {value}")
            except IndexError: # Terminal state, no actions
                ret_str.append(f"Terminal state: {key}, Q: {value}")
        return '\n'.join(ret_str)

    def _state2str(self, state):
        return ''.join([str(x) for x in state])

    def _key_transform(self, key):
        assert len(key) <= 2
        assert isinstance(key[0], Iterable)
        state_str = self._state2str(key[0])
        try:
            new_key = (state_str, key[1])
        except IndexError:
            new_key = (state_str,)
        return new_key

    def __getitem__(self, key):
        """
        @params
        key: a two-element tuple, first element is an iterable, second one can be empty (terminal state)
        """
        new_key = self._key_transform(key)
        return super().__getitem__(new_key)

    def __setitem__(self, key, value):
        new_key = self._key_transform(key)
        super().__setitem__(new_key, value)

    def __missing__(self, key):
        self.data[key] = value = 0
        return value

    def update(self, state, action, next_state, reward, actions=None):
        key = (state, action)
        current_Q = self[key]
        if actions is not None:
            for ind, a in enumerate(actions):
                if ind == 0:
                    max_nQ = self[(next_state, a)]
                else:
                    temp_Q = self[(next_state, a)]
                    if temp_Q > max_nQ:
                        max_nQ = temp_Q
        else:
            max_nQ = self[(next_state,)]
        self[key] = current_Q + self.alpha*(reward + self.gamma * max_nQ - current_Q)

    def n_step_update(self, state, action, n_state, reward, steps, actions=None):
        pass

    def sum(self):
        val = 0
        for k, v in self.data.items():
            val += v
        return val

    def __add__(self, other):
        for key, value in self.data.items():
            if other[key] != 0:
                self[key] = (other[key] + value)/2
        for key, value in other.data.items():
            if self[key] == 0:
                self[key] = value
        return self


