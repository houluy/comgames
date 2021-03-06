## This file is intended for the configuration of hyper-parameters

config = {
    "tictactoe": {
        "Q_learning": {
            "gamma": 1, # Discount factor
            "alpha": 0.7, # Learning rate
            "min_epsilon": 0.1, # Minimum epsilon for epsilon-greedy
            "epsilon": 1, # Initial epsilon for epsilon-greedy
            "epsilon_decay": 0.99998, # Exponential rate for the decay of epsilon
            "num_episodes": 100000, # Number of episodes for training
            "n-step": 3, # Number of steps for n-step Q learning
        },
    },
    "fourinarow": {
        "Q_learning": {
            "gamma": 1, # Discount factor
            "alpha": 0.5, # Learning rate
            "min_epsilon": 0.1, # Minimum epsilon for epsilon-greedy
            "epsilon": 1, # Initial epsilon for epsilon-greedy
            "epsilon_decay": 0.99998, # Exponential rate for the decay of epsilon
            "num_episodes": 1, # Number of episodes for training
            "verbose": True, # Show the training process
        },
    },
}

