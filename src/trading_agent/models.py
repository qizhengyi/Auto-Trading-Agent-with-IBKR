from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TradeProposal(BaseModel):
    symbol: str
    side: Side
    confidence: float = Field(ge=0.0, le=1.0)
    reference_price: float = Field(gt=0)
    stop_price: float | None = None
    thesis: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApprovedOrder(BaseModel):
    symbol: str
    side: Side
    quantity: int = Field(gt=0)
    order_type: str = "MKT"
    reference_price: float
    rationale: str


class RiskDecision(BaseModel):
    approved: bool
    reason: str
    order: ApprovedOrder | None = None
