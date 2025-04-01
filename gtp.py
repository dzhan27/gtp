import random
from learning_dynamic import LearningDynamic, ReplicatorDynamic
from strategies import Strategy

GAME = [[(0,0), (1,0)], [(0,1), (1,1)]]
LEARNING_DYNAMIC = ReplicatorDynamic()

class Agent:
    def __init__(self, strategy):
        self.strategy = strategy
        self.previous = (0,0)
        self.type = 0

def initialize_board(size, strategies):
    '''
    initalizes the board to its starting position and randomly assigns strategies
    :param size: size of square board
    :param strategies: available strategies
    :return: tbhe board
    '''
    board = [[Agent(strategies[0]) for _ in range(size)] for _ in range(size)]
    for x in range(0,size):
        for y in range(0,size):
            board[x][y].strategy = strategies[random.randint(0,len(strategies)-1)]

    return board

def get_opponent(board, x, y):
    '''
    Gets a random opponent to play against
    :param board: the board
    :param x: the x coordinate of agent
    :param y: the y coordinate of agent
    :return: the opponent agent
    '''
    xopp = random.randint(0,len(board)-1)
    yopp = random.randint(0,len(board[0])-1)
    if xopp == x and yopp == y:
        get_opponent(board,x,y)
    return board[xopp][yopp]

def play_agent(curr_agent, opponent):
    '''
    Plays between the current agent and the opponent
    :param curr_agent:
    :param opponent:
    :return:
    '''
    curr_agent_choice = curr_agent.strategy.get_next_value(curr_agent.previous)
    opponent_choice = opponent.strategy.get_next_value(opponent.previous)
    payouts = GAME[curr_agent_choice][opponent_choice]

    curr_agent.strategy = LEARNING_DYNAMIC.newStrategy(curr_agent.strategy, opponent.strategy, payouts)

    curr_agent.previous = (curr_agent_choice, opponent_choice)
    return curr_agent

def play_round(board):
    '''
    Plays through a round
    :param board:
    :return:
    '''
    new_board = board.copy()

    for x in range(len(board)):
        for y in range(len(board[0])):
            opponent = get_opponent(board, x, y)
            new_board[x][y] = play_agent(board[x][y], opponent)
    return new_board

def main():
    size = 100
    strategies = [Strategy("Always 0", lambda previous : 0), Strategy("Always 1", lambda previous : 1)]
    iterations = 100
    board = initialize_board(size,strategies)

    for iteration in range(0,iterations):
        board = play_round(board)

    print([[agent.strategy == strategies[0] for agent in row] for row in board])

if __name__ == "__main__":
    main()