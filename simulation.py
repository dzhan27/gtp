'''
simulation.py contains methods neccesary for setting up and running the simulation
of the game. This class sets up the game grid and update interactions between agents.
'''
import numpy as np
from sim.game import GameType
import random
from sim.agent import Agent

class SpatialConfig:
    def __init__(self, size=50, radius=1, mobility=False, topology='toroidal', strategy_distribution=None):
        self.size = size
        # interaction radius, default set to 1: only interacting with immediate neighbors. If radius < 1 it is fully random.
        self.radius = radius
        # stretch goal: should agents be allowed to move? we start with agents stuck in place, only interacting with neighbors, then explore this later
        self.mobility = mobility
        # default topology is toroidal. this means agents at edges interact with agents at opposite edges. this eliminates weird edge effects. can try classic bounded edges as well
        self.topology = topology
        # dict mapping strategy names to their desired proportions (must sum to 1)
        self.strategy_distribution = strategy_distribution

class Simulation:
    def __init__(self, game_type, config, dynamic, agent_types=[]):
        self.game_type = game_type
        self.game_config = game_type.value
        self.config = config
        self.dynamic = dynamic
        self.agent_types = agent_types
        self.grid = self._init_grid()
        self.payoffs = self.game_config.payoff_matrix

    def _init_grid(self):
        grid = np.empty((self.config.size, self.config.size), dtype=object)
        total_cells = self.config.size ** 2
        strategies = self.game_config.strategies
        
        if self.config.strategy_distribution:
            strategy_list = []
            for strategy in strategies:
                count = int(self.config.strategy_distribution.get(strategy.name, 0) * total_cells)
                strategy_list.extend([strategy] * count)
            
            # fill rounding error randomly
            while len(strategy_list) < total_cells:
                strategy_list.append(random.choice(strategies))
            random.shuffle(strategy_list)
            
            # place strategies
            idx = 0
            for x in range(self.config.size):
                type_count = x
                for y in range(self.config.size):
                    if len(self.agent_types) > 1:
                        type = self.agent_types[type_count % len(self.agent_types)]
                        grid[x, y] = Agent(strategy_list[idx], (x, y), type)
                    else:
                        grid[x, y] = Agent(strategy_list[idx], (x, y))
                    idx += 1
                    type_count += 1
        else:
            # randomly distribute strategies
            for x in range(self.config.size):
                type_count = x
                for y in range(self.config.size):
                    if len(self.agent_types) > 1:
                        type = self.agent_types[type_count % len(self.agent_types)]
                        available_strategies = []
                        for strategy in strategies:
                            available_strategies.append(strategy)
                        grid[x, y] = Agent(random.choice(available_strategies), (x, y), type)
                        type_count = type_count + 1
                    else:
                        grid[x,y] = Agent(random.choice(strategies), (x,y))
        
        return grid

    def _get_neighbors(self, agent):
        x, y = agent.position
        neighbors = []
        while self.config.radius < 1:
            nx = random.randint(0, self.config.size-1)
            ny = random.randint(0, self.config.size-1)
            if nx != x and ny != y and self.grid[nx, ny].type is not None and self.grid[nx, ny].type == agent.type and len(neighbors) < 1:
                neighbors.append(self.grid[nx, ny])
            if nx != x and ny != y and (self.grid[nx, ny].type is None or (self.grid[nx, ny].type != agent.type and len(neighbors) >= 1)):
                neighbors.append(self.grid[nx, ny])
                return neighbors
        for dx in range(-self.config.radius, self.config.radius+1):
            for dy in range(-self.config.radius, self.config.radius+1):
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.config.size
                ny = (y + dy) % self.config.size
                neighbors.append(self.grid[nx, ny])
        return neighbors

    def _interact(self, a1, a2):
        a1_action = a1.strategy.act(a1.history, a1.type)
        a2_action = a2.strategy.act(a2.history, a2.type)
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
                while agent.type is not None and partner.type == agent.type:
                    partner = random.choice(neighbors)
                self._interact(agent, partner)
            # Update strategy
            new_strat = self.dynamic(agent, neighbors)
            new_grid[agent.position] = Agent(new_strat, agent.position, agent.type)
            new_grid[agent.position].score = agent.score
        self.grid = new_grid