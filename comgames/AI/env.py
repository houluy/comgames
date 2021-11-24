import pickle


class Env:
    def __init__(self, game):
        self.game = game
        self.game_name = game.game_name
        self.max_round = self.game.board.mround()
        self.verbose = True
        self.reward_dic = {
            1: 100,
            -2: 10, # Duel
            0: 0, 
        }
        self.finish_state = {
            "Win": 1,
            "Tie": 2,
            "Move": 0,
        }

    @property
    def game_round(self):
        return self.game.game_round

    def _reward(self, result):
        return self.reward_dic.get(result)

    def observation(self):
        return self.game.board.state

    def info(self):
        return 

    def actions(self, state):
        board = self.game.board.state2board(state)
        if self.game_name == "fourinarow":
            return self.game.board.columns(board)
        else:
            return self.game.board.positions(board)
    
    def step(self, action):
        pos = self.game.move(action)
        if self.verbose:
            self.game.board.print_pos(coordinates=[pos])
        self.game.board.game_round += 1
        finish = self.game.board.check_win_by_step(pos, player=self.game.board.player)
        if self.game.board.game_round == self.max_round and not finish:
            return self.game.board.state, self._reward(-2), self.finish_state["Tie"], "Tie!"
        if finish:
            return self.game.board.state, self._reward(1), self.finish_state["Win"], "Agent wins!"
        if not finish:
            return self.game.board.state, self._reward(0), self.finish_state["Move"], "Switch player!"

    def reset(self):
        self.game.board.clear()

#def run(game_name=None, Q_file=None, turn="offensive"):
#    with open(Q_file, "rb") as f:
#        trained_Q = pickle.load(f)
#    agent = TDAgent.by_Q(game_name, trained_Q)
#    env = Env(game_name)
#    done = 0
#    game_round = 0
#    env.game.board.print_pos()
#    state = env.observation()
#    while done == 0:
#        game_round += 1
#        if turn == "offensive":
#            actions = env.actions(state) 
#            action = agent.greedy(state, actions)
#        elif turn == "defensive":
#            action = env.game.input_pos() # Be careful, no exception handlers here
#        state, _, done, info = env.step(action)
#        env.game.board.print_pos(coordinates=[action])
#        env.game.celebrate(done)
#        if done:
#            break
#        if turn == "offensive":
#            action = env.game.input_pos() # Be careful, no exception handlers here
#        elif turn == "defensive":
#            actions = env.actions(state) 
#            action = agent.greedy(state, actions)
#        next_state, _, done, info = env.step(action)
#        env.game.board.print_pos(coordinates=[action])
#        env.game.celebrate(done)
#        state = next_state[:]
#    
#
