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
        
    def act(self, history, type):
        return self.actor(history, type)

@dataclass
class GameConfig:
    name: str
    payoff_matrix: Dict[Tuple[str, str], Tuple[int, int]]
    strategies: List['Strategy']
    strategy_colors: Dict[str, str]
    default_distribution: Dict[str, float]
    valid_actions: List[str]
    agent_types: List[str]

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
            Strategy("Cooperate", lambda h, t: 'C'),
            Strategy("Defect", lambda h, t: 'D'),
            Strategy("TitForTat", lambda h, t: h[-1][1] if h else 'C')
        ],
        strategy_colors={
            'Cooperate': '#2ecc71',
            'Defect': '#e74c3c',
            'TitForTat': '#3498db'
        },
        default_distribution={'Cooperate': 0.5, 'Defect': 0.25, 'TitForTat': 0.25},
        valid_actions=['C', 'D'],
        agent_types=None
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
            Strategy("Always Stag", lambda h, t: 'S'),
            Strategy("Always Hare", lambda h, t: 'H'),
            Strategy("Cautious", lambda h, t: 'S' if h.count('S') > h.count('H') else 'H')
        ],
        strategy_colors={
            'Always Stag': '#1abc9c',
            'Always Hare': '#e67e22',
            'Cautious': '#9b59b6'
        },
        default_distribution={'Always Stag': 0.4, 'Always Hare': 0.4, 'Cautious': 0.2},
        valid_actions=['S', 'H'],
        agent_types=None
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
            Strategy("Always Hawk", lambda h, t: 'H'),
            Strategy("Always Dove", lambda h, t: 'D'),
            Strategy("Random", lambda h, t: 'H' if random.random() < 0.5 else 'D')
        ],
        strategy_colors={
            'Always Hawk': '#f1c40f',
            'Always Dove': '#9b59b6',
            'Random': '#0e44ad'
        },
        default_distribution={'Always Hawk': 0.4, 'Always Dove': 0.4, 'Random': 0.2},
        valid_actions=['H', 'D'],
        agent_types=None
    )

    BS = GameConfig(
        name="Battle of Sexes",
        payoff_matrix={
            ('C', 'H'): (2, 2),
            ('C', 'U'): (0, 0),
            ('F', 'H'): (5, 5),
            ('F', 'U'): (15, -5),
            ('H', 'C'): (2, 2),
            ('U', 'C'): (0, 0),
            ('H', 'F'): (5, 5),
            ('U', 'F'): (-5, 15)
        },
        strategies=[
            Strategy("Always Cooperative", lambda h, t: 'C' if t == "Female" else 'H'),
            Strategy("Always Uncooperative", lambda h, t: 'F' if t == "Female" else 'U')
        ],
        strategy_colors={
            "Always Cooperative": '#f1c40f',
            "Always Uncooperative": '#9b59b6',
        },
        default_distribution={'Always Cooperative': 0.5, 'Always Uncooperative': 0.5},
        valid_actions=['C', 'H', 'F', 'U'],
        agent_types=["Male", "Female"]
    )
    
    RPS = GameConfig(
        name="Battle of Sexes",
        payoff_matrix={
            ('R', 'R'): (0, 0),
            ('P', 'P'): (0, 0),
            ('S', 'S'): (0, 0),
            ('S', 'P'): (-1, 1),
            ('P', 'R'): (-1, 1),
            ('R', 'S'): (-1, 1),
            ('P', 'S'): (1, -1),
            ('S', 'R'): (1, -1),
            ('R', 'P'): (1, -1),
        },
        strategies=[
            Strategy("Always Rock", lambda h, t: 'R'),
            Strategy("Always Paper", lambda h, t: 'P'),
            Strategy("Always Scissor", lambda h, t: 'S'),
            Strategy("Always Random",  lambda h, t: 'R' if (r := random.random()) < 1/3 else 'P' if r < 2/3 else 'S')
        ],
        strategy_colors={
            "Always Rock": '#f1c40f',
            "Always Paper": '#9b59b6',
            "Always Scissor": '#1abc9c',
            "Always Random": '#0e44ad'
            
        },
        #default_distribution={"Always Rock": 0.25, "Always Paper": 0.25,"Always Scissor": 0.25},
        default_distribution={"Always Rock": 0.25, "Always Paper": 0.25,"Always Scissor": 0.25,"Always Random": 0.25 },
        valid_actions=['R', 'P', 'S'],
        agent_types=None
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