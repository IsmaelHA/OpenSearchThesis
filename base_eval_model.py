from abc import ABC, abstractmethod

class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, eval_data):
        pass
