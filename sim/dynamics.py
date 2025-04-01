import random
import numpy as np

class LearningDynamic:

    # imitate best strategy among neighbors
    def replicator(agent, neighbors):
        if not neighbors:
            return agent.strategy
        best = max(neighbors, key=lambda n: n.score)
        return best.strategy if best.score > agent.score else agent.strategy

    # adopt better strategies probabilistically
    def fermi(agent, neighbors, beta=0.1):
        if not neighbors:
            return agent.strategy
        other = random.choice(neighbors)
        delta = other.score - agent.score
        if delta > 0 or random.random() < np.exp(beta * delta):
            return other.strategy
        return agent.strategy