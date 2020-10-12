## This file is intended for the configuration of hyper-parameters

tictactoe = {
    "Q_learning": {
        "gamma": 1, # Discount factor
        "alpha": 0.7, # Learning rate
        "min_epsilon": 0.1, # Minimum epsilon for epsilon-greedy
        "epsilon_decay": 0.99998, # Exponential rate for the decay of epsilon
        "num_episodes": 100000, # Number of episodes for training
    },
}


fourinarow = {
    "Q_learning": {
        "gamma": 1, # Discount factor
        "alpha": 0.5, # Learning rate
        "min_epsilon": 0.1, # Minimum epsilon for epsilon-greedy
        "num_episodes": 100000, # Number of episodes for training
    },
}

