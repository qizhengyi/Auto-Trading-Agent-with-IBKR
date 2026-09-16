import os
from dotenv import load_dotenv

from .agent import TradingAgent
from .strategy import SMASignalAgent
from .risk import RiskGate, PortfolioState
from .audit import AuditLog
from .brokers.paper import PaperBroker
from .brokers.ibkr import IBKRBroker


def build_agent():
    load_dotenv()
    broker_name = os.getenv("BROKER", "paper").lower()
    starting_cash = float(os.getenv("STARTING_CASH", "100000"))
    broker = PaperBroker(starting_cash) if broker_name == "paper" else IBKRBroker()
    risk = RiskGate(
        max_position_pct=float(os.getenv("MAX_POSITION_PCT", "0.10")),
        max_daily_loss_pct=float(os.getenv("MAX_DAILY_LOSS_PCT", "0.02")),
        risk_per_trade_pct=float(os.getenv("RISK_PER_TRADE_PCT", "0.005")),
    )
    return TradingAgent(SMASignalAgent(5, 20), risk, broker, AuditLog()), broker


def main():
    agent, broker = build_agent()
    symbol = os.getenv("SYMBOL", "NU")
    prices = [
        14.10, 14.00, 14.12, 14.08, 14.20,
        14.25, 14.30, 14.35, 14.28, 14.40,
        14.45, 14.50, 14.54, 14.52, 14.60,
        14.66, 14.72, 14.75, 14.80, 14.92,
        15.00, 15.08, 15.12, 15.20, 15.25,
    ]
    snap = broker.snapshot()
    cash = float(snap.get("cash", os.getenv("STARTING_CASH", "100000")))
    positions = snap.get("positions", {})
    state = PortfolioState(
        equity=float(os.getenv("STARTING_CASH", "100000")),
        cash=cash,
        daily_pnl=0.0,
        positions=positions,
    )
    print(agent.step(symbol, prices, state))


if __name__ == "__main__":
    main()
