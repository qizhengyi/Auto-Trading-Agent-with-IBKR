from abc import ABC, abstractmethod
from ..models import ApprovedOrder


class Broker(ABC):
    @abstractmethod
    def submit_order(self, order: ApprovedOrder) -> dict:
        ...

    @abstractmethod
    def snapshot(self) -> dict:
        ...
