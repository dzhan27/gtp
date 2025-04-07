from enum import Enum

class GameType(Enum):
    PD = "Prisoner's Dilemma"
    HD = "Hawk-Dove"
    SH = "Stag Hunt"
    RPS = "Rock-Paper-Scissors"
    BS = "Battle of the Sexes"
    CUSTOM = "Custom"

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