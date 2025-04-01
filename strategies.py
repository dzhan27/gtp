
class Strategy:
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy

    def get_next_value(self, previous_val):
        return self.strategy(previous_val)