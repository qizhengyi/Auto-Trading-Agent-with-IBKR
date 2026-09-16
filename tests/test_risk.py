from trading_agent.models import TradeProposal, Side
from trading_agent.risk import RiskGate, PortfolioState


def test_buy_order_is_sized_and_approved():
    gate = RiskGate()
    state = PortfolioState(100_000, 100_000, 0, {})
    proposal = TradeProposal(
        symbol="NU", side=Side.BUY, confidence=0.8,
        reference_price=15.0, stop_price=14.55, thesis="test"
    )
    result = gate.evaluate(proposal, state)
    assert result.approved
    assert result.order.quantity > 0


def test_daily_loss_kill_switch():
    gate = RiskGate(max_daily_loss_pct=0.02)
    state = PortfolioState(100_000, 100_000, -2_100, {})
    proposal = TradeProposal(
        symbol="NU", side=Side.BUY, confidence=0.9,
        reference_price=15.0, stop_price=14.5, thesis="test"
    )
    result = gate.evaluate(proposal, state)
    assert not result.approved
    assert "kill switch" in result.reason.lower()
