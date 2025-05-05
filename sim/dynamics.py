"""
dynamics.py contains the definitions for the learning dynamics applied to eacj agent.
These dynamics will affect the agent's startegy based on game state or randomly.
"""

import random
import numpy as np

class LearningDynamic:

    # imitate best strategy among neighbors
    def replicator(agent, neighbors):
        if not neighbors:
            return agent.strategy
        for neighbor in neighbors.copy():
            if agent.type != neighbor.type:
                neighbors.remove(neighbor)
        best = max(neighbors, key=lambda n: n.score)
        return best.strategy if best.score > agent.score else agent.strategy

    # adopt better strategies probabilistically
    def fermi(agent, neighbors, beta=0.1):
        if not neighbors:
            return agent.strategy
        for neighbor in neighbors.copy():
            if agent.type != neighbor.type:
                neighbors.remove(neighbor)
        other = random.choice(neighbors)
        delta = other.score - agent.score
        if delta > 0 or random.random() < np.exp(beta * delta):
            return other.strategy
        return agent.strategy
    
    # probability of choosing strategy proportional to fitness
    def moran(agent, neighbors):
        for neighbor in neighbors.copy():
            if agent.type != neighbor.type:
                neighbors.remove(neighbor)
        candidate_pool = [agent] + neighbors
        total_payoff = sum(max(c.score, 0) for c in candidate_pool)
        
        if total_payoff <= 0:
            chosen = random.choice(candidate_pool)
        else:
            probabilities = [max(c.score/total_payoff, 0) for c in candidate_pool]
            chosen = np.random.choice(candidate_pool, p=probabilities)
        return chosen.strategy
    
    # random
    def random_copy(agent, neighbors):
        if not neighbors:
            return agent.strategy
        for neighbor in neighbors.copy():
            if agent.type != neighbor.type:
                neighbors.remove(neighbor)
        other = random.choice(neighbors)
        return other.strategy
    
    # threshold driven random strategy adoption
    def aspiration(agent, neighbors):
        if not neighbors:
            return agent.strategy
        for neighbor in neighbors.copy():
            if agent.type != neighbor.type:
                neighbors.remove(neighbor)
        
        avg_payoff = np.mean([n.score for n in neighbors]) if neighbors else 0
        if agent.score < avg_payoff:
            return random.choice(neighbors).strategy
        return agent.strategy