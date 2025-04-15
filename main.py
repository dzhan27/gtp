import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from simulation import Simulation, SpatialConfig
from sim.game import GameType
from sim.dynamics import LearningDynamic
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

class Agent:
    def __init__(self, strategy, position):
        self.strategy = strategy
        self.score = 0
        self.history = []
        self.position = position
        self.prev_score = 0

    def reset_score(self):
        self.prev_score = self.score
        self.score = 0

def create_output_dir(game_type):
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    dir_name = f"{date_str}_{game_type}"
    output_dir = os.path.join("results", dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def strategy_to_color(strategy, game_config):
    return game_config.strategy_colors.get(strategy.name, '#000000')

def run_simulation(game_type=GameType.HD, save_metrics=False):
    game_config = game_type.value
    legend_elements = [
        Patch(facecolor=color, label=strat_name)
        for strat_name, color in game_config.strategy_colors.items()
    ]

    # Variables for detecting stability (probably should make these percent based)
    stabilityRange = 30
    stabilityIterations = 50  
    strategyHistory = {strat.name: [] for strat in game_config.strategies}
    stabilityReached = False
    
    config = SpatialConfig(
        size=50,
        radius=1,
        mobility=0.0,
        topology='toroidal',
        strategy_distribution=game_config.default_distribution
    )
    
    metrics = []
    if save_metrics:
        output_dir = create_output_dir()

    legend_elements = [
    Patch(facecolor=color, label=name)
    for name, color in game_config.strategy_colors.items()
    ]
    
    # initialize sim
    sim = Simulation(
        game_type=game_type,
        config=config,
        dynamic=LearningDynamic.replicator
    )
    
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.legend(handles=legend_elements, loc='upper right')
    img = None

    for iteration in range(1000):
        sim.run_iteration()

        if not plt.fignum_exists(fig.number):
            print("Figure closed by user; stopping simulation.")
            break
        
        # vis
        grid = np.array([[to_rgb(strategy_to_color(agent.strategy, game_config)) for agent in row] 
                        for row in sim.grid])
        if img is None:
            img = ax.imshow(grid, interpolation='nearest')
        else:
            img.set_data(grid)
        
        plt.title(f"Iteration {iteration}")
        plt.pause(0.001)
        
        # collect data
        strategy_counts = {strat.name: 0 for strat in game_config.strategies}
        for row in sim.grid:
            for agent in row:
                strategy_counts[agent.strategy.name] += 1
        metrics.append({
            'iteration': iteration,
            **strategy_counts
        })
        
        # Update history for each strategy
        for strat in strategy_counts:
            strategyHistory[strat].append(strategy_counts[strat])
            if len(strategyHistory[strat]) > stabilityIterations:
                strategyHistory[strat].pop(0)

        # Check if all strategy counts are stable over the last iterations
        if all(len(history) == stabilityIterations for history in strategyHistory.values()) and not stabilityReached:
            is_stable = all(max(history) - min(history) <= stabilityRange for history in strategyHistory.values())
            if is_stable:
                print(f"Stability reached at iteration {iteration}")
                stabilityReached = True

    if save_metrics:
        pd.DataFrame(metrics).to_csv(os.path.join(output_dir, "metrics.csv"), index=False)
    
    plt.close(fig)
    plt.ioff()
    
    print(f"Simulation complete!")

if __name__ == "__main__":
    run_simulation()