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
    
    # probability of choosing strategy proportional to fitness
    def moran(agent, neighbors):
        candidate_pool = [agent] + neighbors
        total_payoff = sum(c.score for c in candidate_pool)
        
        if total_payoff <= 0:
            chosen = random.choice(candidate_pool)
        else:
            probabilities = [c.score/total_payoff for c in candidate_pool]
            chosen = np.random.choice(candidate_pool, p=probabilities)
        return chosen.strategy
    
    # random
    def random_copy(agent, neighbors):
        if not neighbors:
            return agent.strategy
        other = random.choice(neighbors)
        return other.strategy
    
    # threshold driven random strategy adoption
    def aspiration(agent, neighbors):
        if not neighbors:
            return agent.strategy
        
        avg_payoff = np.mean([n.score for n in neighbors]) if neighbors else 0
        if agent.score < avg_payoff:
            return random.choice(neighbors).strategy
        return agent.strategy