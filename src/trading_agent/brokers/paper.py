from .base import Broker
from ..models import ApprovedOrder, Side


class PaperBroker(Broker):
    def __init__(self, starting_cash: float = 100_000):
        self.cash = starting_cash
        self.positions: dict[str, int] = {}

    def submit_order(self, order: ApprovedOrder) -> dict:
        notional = order.quantity * order.reference_price
        if order.side == Side.BUY:
            if notional > self.cash:
                raise ValueError("Insufficient paper cash.")
            self.cash -= notional
            self.positions[order.symbol] = self.positions.get(order.symbol, 0) + order.quantity
        elif order.side == Side.SELL:
            held = self.positions.get(order.symbol, 0)
            if order.quantity > held:
                raise ValueError("Starter paper broker does not allow naked shorting.")
            self.cash += notional
            self.positions[order.symbol] = held - order.quantity

        return {
            "status": "FILLED",
            "mode": "PAPER",
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "fill_price": order.reference_price,
        }

    def snapshot(self) -> dict:
        return {"cash": self.cash, "positions": dict(self.positions)}
