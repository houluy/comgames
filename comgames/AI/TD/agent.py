from 

class TDAgent:
    def __init__(self, dumped_qfile=None):
        if dumped_qfile is None:
            gamma = tictactoe.get("Q_learning").get("gamma")
            alpha = tictactoe.get("Q_learning").get("alpha")
            self.Q = Q(gamma=gamma, alpha=alpha)
        else:
            with open(dumped_qfile, 'rb') as f:
                self.Q = pickle.load(f)

    @classmethod
    def by_Q(cls, Q_dic: Q):
        """Initialize an agent with Q instance"""
        inst = cls()
        inst.Q = Q_dic
        inst.gamma, inst.alpha = Q_dic.gamma, Q_dic.alpha
        return inst

    def epsilon_greedy(self, state, actions, epsilon=0.1):
        rand = random.random()
        if rand < epsilon:
            return random.choice(actions)
        else:
            return self.greedy(state, actions)

    def greedy(self, state, actions):
        for ind, a in enumerate(actions):
            if ind == 0:
                action, maxQ = [a], self.Q[(state, a)]
            else:
                q_value = self.Q[(state, a)]
                if q_value > maxQ:
                    action, maxQ = [a], q_value
                elif q_value == maxQ:
                    action.append(a) # randomly choose an action if Q value is equivalent
                else:
                    continue
        if len(action) == 1:
            return action[0]
        else:
            return random.choice(action)

