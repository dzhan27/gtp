class Agent:
    def __init__(self, strategy, position, gender=None):
        self.strategy = strategy
        self.score = 0
        self.history = []
        self.position = position
        self.type = gender
        self.prev_score = 0

    def reset_score(self):
        self.prev_score = self.score
        self.score = 0