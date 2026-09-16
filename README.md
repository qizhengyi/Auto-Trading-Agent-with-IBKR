# Auto-Trading-Agent-with-IBKR

A portfolio-ready autonomous trading agent with a strict separation between:

1. **Signal / Research Agent** — proposes a trade.
2. **Risk Gate** — deterministic checks; the agent cannot bypass it.
3. **Execution Broker** — paper broker by default, IBKR Web API adapter optional.
4. **Audit Log** — every proposal, rejection, and fill is recorded.

> Default mode is PAPER. Live trading requires two explicit environment flags.

## Architecture

```text
Market Data
    |
    v
SignalAgent  ---> TradeProposal
                    |
                    v
                 RiskGate ----> REJECT + reason
                    |
                    v
               BrokerAdapter
               /           \
          PaperBroker     IBKRBroker
                    |
                    v
                 Audit Log
```

## Features

- SMA momentum baseline strategy
- Structured `TradeProposal`
- Position sizing by max portfolio risk
- Max position concentration
- Daily-loss kill switch
- Duplicate-order protection
- Paper execution
- IBKR Web API adapter
- JSONL audit trail
- Unit tests
- `.env` configuration
- Safe-by-default live trading lock

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src python -m trading_agent.main
```

## Live IBKR mode

For an individual IBKR account, launch and authenticate the Client Portal Gateway first.

Then change:

```env
BROKER=ibkr
ENABLE_LIVE_TRADING=true
DRY_RUN=false
IBKR_ACCOUNT_ID=YOUR_ACCOUNT
IBKR_BASE_URL=https://localhost:5000/v1/api
```

The adapter deliberately refuses to submit an order unless **both**
`ENABLE_LIVE_TRADING=true` and `DRY_RUN=false`.

## Why this is an Agent rather than a trading script

The orchestration layer maintains state and executes a closed decision loop:

**observe → analyze → propose → validate → act → record**

The strategy module can later be replaced by:

- an LLM research agent,
- news/sentiment agent,
- factor model,
- options volatility model,
- reinforcement-learning policy,

without changing the risk or broker layer.

## Interview extensions

- LLM turns news into a typed `TradeProposal`
- RAG over 10-K / 10-Q / earnings calls
- Portfolio optimizer
- Options Greeks / volatility surface
- Walk-forward backtesting
- WebSocket market data
- PostgreSQL + dashboard
- Multi-agent cross-checking before RiskGate
