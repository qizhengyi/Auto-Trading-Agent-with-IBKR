from .models import TradeProposal, Side


class SMASignalAgent:
    def __init__(self, fast: int = 5, slow: int = 20):
        if fast >= slow:
            raise ValueError("fast must be < slow")
        self.fast = fast
        self.slow = slow

    def propose(self, symbol: str, prices: list[float]) -> TradeProposal:
        if len(prices) < self.slow:
            return TradeProposal(
                symbol=symbol,
                side=Side.HOLD,
                confidence=0.0,
                reference_price=prices[-1],
                thesis="Insufficient history.",
            )

        fast_ma = sum(prices[-self.fast:]) / self.fast
        slow_ma = sum(prices[-self.slow:]) / self.slow
        px = prices[-1]
        spread = abs(fast_ma - slow_ma) / max(slow_ma, 1e-9)
        confidence = min(0.95, 0.55 + spread * 10)

        if fast_ma > slow_ma:
            side = Side.BUY
            stop = px * 0.97
            thesis = f"Fast SMA {fast_ma:.2f} > slow SMA {slow_ma:.2f}."
        elif fast_ma < slow_ma:
            side = Side.SELL
            stop = px * 1.03
            thesis = f"Fast SMA {fast_ma:.2f} < slow SMA {slow_ma:.2f}."
        else:
            side = Side.HOLD
            stop = None
            thesis = "No edge: moving averages are equal."

        return TradeProposal(
            symbol=symbol,
            side=side,
            confidence=confidence,
            reference_price=px,
            stop_price=stop,
            thesis=thesis,
        )
