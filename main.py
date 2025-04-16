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
import json

class SimulationGUI:
    def __init__(self, master):
        self.master = master
        master.title("GTP")
        
        # state
        self.is_running = False
        self.should_stop = False
        self.save_data = tk.BooleanVar(value=False)
        self.current_game = GameType.PD
        self.metrics = []
        self.output_dir = None
        
        # stability tracking
        self.stability_range = 30
        self.stability_iterations = 50
        self.strategy_history = {}
        self.stability_reached = False
        
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
        self.current_game = next(gt for gt in GameType if gt.name == selected_game)
        self.reset_simulation()
        
    def create_visualization(self):
        vis_frame = ttk.Frame(self.master)
        vis_frame.grid(row=0, column=1, sticky="nsew")
        
        # chart frame (right)
        viz_container = ttk.Frame(vis_frame)
        viz_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # strategy map (left)
        map_frame = ttk.Frame(viz_container)
        map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.img = self.ax.imshow(np.zeros((50, 50, 3)), interpolation='nearest')
        self.ax.axis('off')
        
        # strategy count chart (right)
        chart_frame = ttk.Frame(viz_container)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.chart_fig = Figure(figsize=(6, 6))
        self.chart_ax = self.chart_fig.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.chart_fig, master=chart_frame)
        self.chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.strategy_lines = {}
        self.strategy_data = {}
        
        # chart setup
        self.chart_ax.set_title("Strategy Proportions Over Time")
        self.chart_ax.set_xlabel("Iteration")
        self.chart_ax.set_ylabel("Proportion")
        self.chart_ax.set_ylim(0, 1)
        self.chart_ax.grid(True)

    def start_simulation(self):
        if not self.is_running:
            if not hasattr(self, 'current_iteration') or self.should_stop:
                self.current_iteration = 0
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
        
        # collect data if saving is enabled
        if self.save_data.get():
            game_config = self.current_game.value
            strategy_counts = {strat.name: 0 for strat in game_config.strategies}
            for row in self.sim.grid:
                for agent in row:
                    strategy_counts[agent.strategy.name] += 1
            
            self.metrics.append({
                'iteration': self.current_iteration,
                **strategy_counts
            })
            
            # update strategy history for stability detection
            for strat in strategy_counts:
                self.strategy_history[strat].append(strategy_counts[strat])
                if len(self.strategy_history[strat]) > self.stability_iterations:
                    self.strategy_history[strat].pop(0)
            
            # check for stability
            if all(len(history) == self.stability_iterations for history in self.strategy_history.values()) and not self.stability_reached:
                is_stable = all(max(history) - min(history) <= self.stability_range for history in self.strategy_history.values())
                if is_stable:
                    print(f"Stability reached at iteration {self.current_iteration}")
                    self.stability_reached = True
        
        self.update_grid()
        self.iteration_text.set_text(f'Iteration: {self.current_iteration}')
        
        self.master.after(50, self.run_simulation_loop)

    def stop_simulation(self):
        self.should_stop = True
        self.is_running = False
        self.btn_run.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        
        # save data if enabled
        if self.save_data.get() and self.metrics:
            self.save_simulation_data()
            self.metrics = []  # clear metrics after saving
        
    def reset_simulation(self):
        self.stop_simulation()
        self.initialize_simulation()
        self.current_iteration = 0
        self.update_grid()
        
    def initialize_simulation(self):
        game_config = self.current_game.value
        if hasattr(self, 'iteration_text'):
            self.iteration_text.remove()
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
        self.strategy_history = {strat.name: [] for strat in game_config.strategies}
        self.stability_reached = False

        # create legend
        legend_elements = [
            Patch(facecolor=color, label=name) 
            for name, color in game_config.strategy_colors.items()
        ]
        self.ax.legend(handles=legend_elements, loc='upper right')
        
        # iteration counter
        self.iteration_text = self.ax.text(
            0.95, 0.05,
            'Iteration: 0',
            horizontalalignment='right',
            verticalalignment='bottom',
            transform=self.ax.transAxes,
            color='white',
            fontsize=12,
            bbox=dict(facecolor='black', alpha=0.5)
        )
        
        # initialize strategy data for the chart
        self.strategy_data = {strat.name: [] for strat in game_config.strategies}
        self.strategy_lines = {}
        
        # clear the chart
        self.chart_ax.clear()
        self.chart_ax.set_title("Strategy Proportions Over Time")
        self.chart_ax.set_xlabel("Iteration")
        self.chart_ax.set_ylabel("Proportion")
        self.chart_ax.set_ylim(0, 1)
        self.chart_ax.grid(True)
        
        # create lines for each strategy
        for strat_name, color in game_config.strategy_colors.items():
            line, = self.chart_ax.plot([], [], label=strat_name, color=color, linewidth=2)
            self.strategy_lines[strat_name] = line
        
        self.chart_ax.legend(loc='upper right')
        self.chart_canvas.draw()

    def update_grid(self):
        game_config = self.current_game.value
        
        self.img.set_data(np.zeros((50, 50, 3)))
        
        grid = np.array([
            to_rgb(game_config.strategy_colors[agent.strategy.name]) 
            for agent_row in self.sim.grid 
            for agent in agent_row]).reshape(self.sim.grid.shape[0], self.sim.grid.shape[1], 3)
        
        self.img.set_data(grid)
        self.canvas.draw_idle()
        
        # update strategy count chart
        if self.is_running:
            # count strategies
            strategy_counts = {strat.name: 0 for strat in game_config.strategies}
            total_agents = 0
            
            for row in self.sim.grid:
                for agent in row:
                    strategy_counts[agent.strategy.name] += 1
                    total_agents += 1
            
            # calculate proportions
            for strat_name, count in strategy_counts.items():
                proportion = count / total_agents if total_agents > 0 else 0
                self.strategy_data[strat_name].append(proportion)
                
                # update the line data
                self.strategy_lines[strat_name].set_data(
                    range(len(self.strategy_data[strat_name])), 
                    self.strategy_data[strat_name]
                )
            
            self.chart_ax.set_xlim(0, max(10, len(self.strategy_data[list(self.strategy_data.keys())[0]])))
            self.chart_canvas.draw_idle()

    def save_simulation_data(self):
        # create output directory with timestamp
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{date_str}_{self.current_game.name}"
        self.output_dir = os.path.join("results", dir_name)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # save metrics to csv
        metrics_df = pd.DataFrame(self.metrics)
        metrics_df.to_csv(os.path.join(self.output_dir, "metrics.csv"), index=False)
        
        # save configuration
        config = {
            'game_type': self.current_game.name,
            'grid_size': self.sim.grid.shape[0],
            'radius': self.sim.config.radius,
            'mobility': self.sim.config.mobility,
            'topology': self.sim.config.topology,
            'total_iterations': self.current_iteration,
            'strategy_distribution': self.sim.config.strategy_distribution
        }
        
        with open(os.path.join(self.output_dir, "config.json"), 'w') as f:
            json.dump(config, f, indent=4)
            
        print(f"Simulation data saved to {self.output_dir}")

    def on_closing(self):
        self.stop_simulation()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = SimulationGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()