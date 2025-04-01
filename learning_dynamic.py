from abc import ABC, abstractmethod

class LearningDynamic(ABC):
    @abstractmethod
    def newStrategy(self, curr_strategy, opp_strategy, payouts):
        pass

class ReplicatorDynamic(LearningDynamic):
    def __init__(self):
        return

    def newStrategy(self, curr_strategy, opp_strategy, payouts):
        if payouts[0] < payouts[1]:
            return opp_strategy
        return curr_strategy