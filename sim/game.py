"""
Game.py contains the definitions for the games and the strategies used in the simulation.
All relevant game types are defined here, along with strategies and associated metadata.
"""

from enum import Enum
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

class Strategy:
    def __init__(self, name, actor):
        self.name = name
        self.actor = actor
        
    def act(self, history):
        return self.actor(history)

@dataclass
class GameConfig:
    name: str
    payoff_matrix: Dict[Tuple[str, str], Tuple[int, int]]
    strategies: List['Strategy']
    strategy_colors: Dict[str, str]
    default_distribution: Dict[str, float]
    valid_actions: List[str]

class GameType(Enum):
    
    PD = GameConfig(
        name="Prisoner's Dilemma",
        payoff_matrix={
            ('C', 'C'): (3, 3),
            ('C', 'D'): (0, 5),
            ('D', 'C'): (5, 0),
            ('D', 'D'): (1, 1)
        },
        strategies=[
            Strategy("Cooperate", lambda _: 'C'),
            Strategy("Defect", lambda _: 'D'),
            Strategy("TitForTat", lambda h: h[-1][1] if h else 'C')
        ],
        strategy_colors={
            'Cooperate': '#2ecc71',
            'Defect': '#e74c3c',
            'TitForTat': '#3498db'
        },
        default_distribution={'Cooperate': 0.5, 'Defect': 0.25, 'TitForTat': 0.25},
        valid_actions=['C', 'D']
    )

    SH = GameConfig(
        name="Stag Hunt",
        payoff_matrix={
            ('S', 'S'): (5, 5),
            ('S', 'H'): (0, 3),
            ('H', 'S'): (3, 0),
            ('H', 'H'): (3, 3)
        },
        strategies=[
            Strategy("Always Stag", lambda _: 'S'),
            Strategy("Always Hare", lambda _: 'H'),
            Strategy("Cautious", lambda h: 'S' if h.count('S') > h.count('H') else 'H')
        ],
        strategy_colors={
            'Always Stag': '#1abc9c',
            'Always Hare': '#e67e22',
            'Cautious': '#9b59b6'
        },
        default_distribution={'Always Stag': 0.4, 'Always Hare': 0.4, 'Cautious': 0.2},
        valid_actions=['S', 'H']
    )

    HD = GameConfig(
        name="Hawk-Dove",
        payoff_matrix={
            ('H', 'H'): (0, 0),
            ('H', 'D'): (4, 0),
            ('D', 'H'): (0, 4),
            ('D', 'D'): (2, 2)
        },
        strategies=[
            Strategy("Always Hawk", lambda _: 'H'),
            Strategy("Always Dove", lambda _: 'D'),
            Strategy("Random", lambda h: 'H' if random.random() < 0.5 else 'D')
        ],
        strategy_colors={
            'Always Hawk': '#f1c40f',
            'Always Dove': '#9b59b6',
            'Random': '#0e44ad'
        },
        default_distribution={'Always Hawk': 0.4, 'Always Dove': 0.4, 'Random': 0.2},
        valid_actions=['H', 'D']
    )

    def __str__(self):
        return self.value.name

"""

old code

PAYOFF_MATRIX = {
    GameType.PD: {
        ('C', 'C'): (3, 3),
        ('C', 'D'): (0, 5),
        ('D', 'C'): (5, 0),
        ('D', 'D'): (1, 1)
    },
    GameType.HD: {
        ('H', 'H'): (0, 0),
        ('H', 'D'): (4, 0),
        ('D', 'H'): (0, 4),
        ('D', 'D'): (2, 2)
    },
    GameType.SH: {
        ('S', 'S'): (5, 5),
        ('S', 'H'): (0, 3),
        ('H', 'S'): (3, 0),
        ('H', 'H'): (3, 3)
    },
    GameType.RPS: {
        ('R', 'R'): (0, 0),
        ('R', 'P'): (-1, 1),
        ('R', 'S'): (1, -1),
        ('P', 'R'): (1, -1),
        ('P', 'P'): (0, 0),
        ('P', 'S'): (-1, 1),
        ('S', 'R'): (-1, 1),
        ('S', 'P'): (1, -1),
        ('S', 'S'): (0, 0)
    },
    GameType.BS: {
        ('C', 'H'): (2, 2),
        ('C', 'U'): (0, 0),
        ('F', 'H'): (5, 5),
        ('F', 'U'): (15, -5)
    }
}
"""