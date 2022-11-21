from abc import abstractmethod

from Groot.Database.models.FinancialJargon import FinancialJargon


class Strategy:
    @abstractmethod
    def execute(self) -> dict:
        pass

    @abstractmethod
    def set_description(self):
        pass


class TermVisualization:
    strategy: Strategy
    term: FinancialJargon

    def __init__(self, term, strategy: Strategy = None) -> None:
        self.strategy = strategy
        self.term = term

    def executeStratey(self, client_currency: str) -> dict:
        return self.strategy.execute(client_currency)

    def set_description(self, description):
        self.strategy.set_description(description)
