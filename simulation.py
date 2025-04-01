import numpy as np
from sim.game import GameType, PAYOFF_MATRIX
import random
from sim.agent import Agent

class SpatialConfig:
    def __init__(self, size=50, radius=1, mobility=False, topology='toroidal'):
        self.size = size
        # interaction radius, default set to 1: only interacting with immediate neighbors
        self.radius = radius
        # stretch goal: should agents be allowed to move? we start with agents stuck in place, only interacting with neighbors, then explore this later
        self.mobility = mobility
        # default topology is toroidal. this means agents at edges interact with agents at opposite edges. this eliminates weird edge effects. can try classic bounded edges as well
        self.topology = topology

class Simulation:
    def __init__(self, game_type, strategies, config, dynamic):
        self.game_type = game_type
        self.config = config
        self.dynamic = dynamic
        self.grid = self._init_grid(strategies)
        self.payoffs = PAYOFF_MATRIX[game_type]

    def _init_grid(self, strategies):
        grid = np.empty((self.config.size, self.config.size), dtype=object)
        for x in range(self.config.size):
            for y in range(self.config.size):
                grid[x,y] = Agent(random.choice(strategies), (x,y))
        return grid

    def _get_neighbors(self, agent):
        x, y = agent.position
        neighbors = []
        for dx in range(-self.config.radius, self.config.radius+1):
            for dy in range(-self.config.radius, self.config.radius+1):
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.config.size
                ny = (y + dy) % self.config.size
                neighbors.append(self.grid[nx, ny])
        return neighbors

    def _interact(self, a1, a2):
        a1_action = a1.strategy.act(a1.history)
        a2_action = a2.strategy.act(a2.history)
        payoff = self.payoffs.get((a1_action, a2_action), (0,0))
        a1.score += payoff[0]
        a2.score += payoff[1]
        a1.history.append((a1_action, a2_action))
        a2.history.append((a2_action, a1_action))

    def run_iteration(self):
        new_grid = np.copy(self.grid)
        for agent in self.grid.flatten():
            neighbors = self._get_neighbors(agent)
            if neighbors:
                partner = random.choice(neighbors)
                self._interact(agent, partner)
            # Update strategy
            new_strat = self.dynamic(agent, neighbors)
            new_grid[agent.position] = Agent(new_strat, agent.position)
            new_grid[agent.position].score = agent.score
        self.grid = new_grid