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
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sim.game import GameType

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

class SimulationGUI:
    def __init__(self, master):
        self.master = master
        master.title("GTP")
        
        # state
        self.is_running = False
        self.should_stop = False
        self.save_data = tk.BooleanVar(value=True)
        self.current_game = GameType.PD
        
        # layout
        self.create_controls()
        self.create_visualization()

        self.initialize_simulation()

    def create_controls(self):
        control_frame = ttk.Frame(self.master, padding=10)
        control_frame.grid(row=0, column=0, sticky="nsew")
        
        ttk.Label(control_frame, text="Select Game:").pack(pady=5)
        self.game_selector = ttk.Combobox(control_frame, 
                                        values=[gt.name for gt in GameType])
        self.game_selector.current(0)
        self.game_selector.pack(pady=5)
        
        # buttons
        self.btn_run = ttk.Button(control_frame, text="Run", command=self.start_simulation)
        self.btn_run.pack(pady=5, fill=tk.X)
        
        self.btn_stop = ttk.Button(control_frame, text="Stop", 
                                 command=self.stop_simulation, state=tk.DISABLED)
        self.btn_stop.pack(pady=5, fill=tk.X)
        
        self.btn_reset = ttk.Button(control_frame, text="Reset", command=self.reset_simulation)
        self.btn_reset.pack(pady=5, fill=tk.X)

        # save data
        ttk.Checkbutton(control_frame, text="Save Metrics", 
                       variable=self.save_data).pack(pady=5)
        
        self.game_selector.bind('<<ComboboxSelected>>', self.on_game_change)

    def on_game_change(self, event):
        selected_game = self.game_selector.get()
        self.current_game = next(gt for gt in GameType if gt.value.name == selected_game)
        self.reset_simulation()
        
    def create_visualization(self):
        vis_frame = ttk.Frame(self.master)
        vis_frame.grid(row=0, column=1, sticky="nsew")
        
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=vis_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.img = self.ax.imshow(np.zeros((50, 50, 3)), interpolation='nearest')
        self.ax.axis('off')

    def start_simulation(self):
        if not self.is_running:
            self.is_running = True
            self.should_stop = False
            self.btn_run.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            
            selected_game = self.game_selector.get()
            self.current_game = next(gt for gt in GameType if gt.name == selected_game)
            
            self.master.after(100, self.run_simulation_loop)

    def run_simulation_loop(self):
        if not hasattr(self, 'current_iteration'):
            self.current_iteration = 0
        
        if self.should_stop:
            self.stop_simulation()
            return
            
        self.sim.run_iteration()
        self.current_iteration += 1
        
        self.update_grid()
        self.iteration_text.set_text(f'Iteration: {self.current_iteration}')
        
        self.master.after(50, self.run_simulation_loop)

    def stop_simulation(self):
        self.should_stop = True
        self.is_running = False
        self.btn_run.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        
    def reset_simulation(self):
        self.stop_simulation()
        self.initialize_simulation()
        self.current_iteration = 0
        self.update_grid()
        
    def initialize_simulation(self):
        game_config = self.current_game.value
        config = SpatialConfig(
            size=50,
            radius=1,
            mobility=0.0,
            topology='toroidal',
            strategy_distribution=game_config.default_distribution
        )
        
        self.sim = Simulation(
            game_type=self.current_game,
            config=config,
            dynamic=LearningDynamic.replicator
        )

        # legend
        game_config = self.current_game.value
        legend_elements = [
            Patch(facecolor=color, label=name) 
            for name, color in game_config.strategy_colors.items()
        ]
        self.ax.legend(handles=legend_elements, loc='upper right')
        
        # iteration counter
        self.iteration_text = self.ax.text(
            0.95, 0.95, 'Iteration: 0',
            horizontalalignment='right',
            verticalalignment='top',
            transform=self.ax.transAxes,
            color='white',
            fontsize=12
        )
        
    def update_grid(self):
        game_config = self.current_game.value
        
        self.img.set_data(np.zeros((50, 50, 3)))
        
        grid = np.array([
            to_rgb(game_config.strategy_colors[agent.strategy.name]) 
            for agent_row in self.sim.grid 
            for agent in agent_row]).reshape(self.sim.grid.shape[0], self.sim.grid.shape[1], 3)
        
        self.img.set_data(grid)
        self.canvas.draw_idle()

    def on_closing(self):
        self.stop_simulation()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = SimulationGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()