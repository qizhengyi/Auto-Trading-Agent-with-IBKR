from .audit import AuditLog


class TradingAgent:
    def __init__(self, strategy, risk, broker, audit: AuditLog):
        self.strategy = strategy
        self.risk = risk
        self.broker = broker
        self.audit = audit
        self._last_fingerprint = None

    def step(self, symbol: str, prices: list[float], state) -> dict:
        proposal = self.strategy.propose(symbol, prices)
        self.audit.write("proposal", proposal.model_dump())

        decision = self.risk.evaluate(proposal, state)
        self.audit.write("risk_decision", decision.model_dump())
        if not decision.approved:
            return {"status": "REJECTED", "reason": decision.reason}

        order = decision.order
        fingerprint = (order.symbol, order.side.value, order.quantity, round(order.reference_price, 4))
        if fingerprint == self._last_fingerprint:
            result = {"status": "REJECTED", "reason": "Duplicate-order guard."}
            self.audit.write("duplicate_guard", result)
            return result

        result = self.broker.submit_order(order)
        self._last_fingerprint = fingerprint
        self.audit.write("execution", result)
        return result
