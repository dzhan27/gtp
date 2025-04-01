import random

class Strategy:
    def __init__(self, name, actor):
        self.name = name
        self.actor = actor
        
    def act(self, history):
        return self.actor(history)

# basic prisoner dilemma strategies
AlwaysCooperate = Strategy("Cooperate", lambda _: 'C')
AlwaysDefect = Strategy("Defect", lambda _: 'D')
TitForTat = Strategy("TitForTat", lambda h: h[-1][1] if h else 'C')
Random = Strategy("Random", lambda _: random.choice(['C','D']))