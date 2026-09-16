from dataclasses import dataclass
from .models import TradeProposal, RiskDecision, ApprovedOrder, Side


@dataclass
class PortfolioState:
    equity: float
    cash: float
    daily_pnl: float
    positions: dict[str, int]


class RiskGate:
    def __init__(self, max_position_pct=0.10, max_daily_loss_pct=0.02,
                 risk_per_trade_pct=0.005, min_confidence=0.55):
        self.max_position_pct = max_position_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.risk_per_trade_pct = risk_per_trade_pct
        self.min_confidence = min_confidence

    def evaluate(self, proposal: TradeProposal, state: PortfolioState) -> RiskDecision:
        if proposal.side == Side.HOLD:
            return RiskDecision(approved=False, reason="HOLD proposal.")
        if proposal.confidence < self.min_confidence:
            return RiskDecision(approved=False, reason="Confidence below threshold.")
        if state.daily_pnl <= -state.equity * self.max_daily_loss_pct:
            return RiskDecision(approved=False, reason="Daily-loss kill switch triggered.")

        px = proposal.reference_price
        max_notional = state.equity * self.max_position_pct
        max_qty_by_concentration = int(max_notional // px)

        if proposal.stop_price is not None:
            risk_per_share = abs(px - proposal.stop_price)
            if risk_per_share <= 0:
                return RiskDecision(approved=False, reason="Invalid stop distance.")
            risk_budget = state.equity * self.risk_per_trade_pct
            max_qty_by_risk = int(risk_budget // risk_per_share)
        else:
            max_qty_by_risk = max_qty_by_concentration

        qty = min(max_qty_by_concentration, max_qty_by_risk)

        if proposal.side == Side.BUY:
            qty = min(qty, int(state.cash // px))
        elif proposal.side == Side.SELL:
            qty = min(qty, max(0, state.positions.get(proposal.symbol, 0)))

        if qty <= 0:
            return RiskDecision(approved=False, reason="No allowable quantity after risk checks.")

        return RiskDecision(
            approved=True,
            reason="Passed deterministic risk gate.",
            order=ApprovedOrder(
                symbol=proposal.symbol,
                side=proposal.side,
                quantity=qty,
                reference_price=px,
                rationale=proposal.thesis,
            ),
        )
