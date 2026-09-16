import os
import requests
import urllib3
from .base import Broker
from ..models import ApprovedOrder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IBKRBroker(Broker):
    def __init__(self):
        self.base = os.getenv("IBKR_BASE_URL", "https://localhost:5000/v1/api").rstrip("/")
        self.account_id = os.getenv("IBKR_ACCOUNT_ID", "")
        self.enable_live = os.getenv("ENABLE_LIVE_TRADING", "false").lower() == "true"
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    def _guard(self):
        if not self.account_id:
            raise RuntimeError("IBKR_ACCOUNT_ID is missing.")
        if not self.enable_live or self.dry_run:
            raise RuntimeError(
                "Live submission locked. Set ENABLE_LIVE_TRADING=true and DRY_RUN=false intentionally."
            )

    def submit_order(self, order: ApprovedOrder) -> dict:
        self._guard()
        payload = {
            "orders": [{
                "acctId": self.account_id,
                "conid": self._resolve_conid(order.symbol),
                "orderType": order.order_type,
                "side": order.side.value,
                "tif": "DAY",
                "quantity": order.quantity,
            }]
        }
        r = requests.post(
            f"{self.base}/iserver/account/{self.account_id}/orders",
            json=payload,
            verify=False,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    def _resolve_conid(self, symbol: str) -> int:
        r = requests.get(
            f"{self.base}/iserver/secdef/search",
            params={"symbol": symbol},
            verify=False,
            timeout=15,
        )
        r.raise_for_status()
        items = r.json()
        if not items:
            raise RuntimeError(f"No IBKR contract found for {symbol}.")
        return int(items[0]["conid"])

    def snapshot(self) -> dict:
        if not self.account_id:
            return {"status": "IBKR_ACCOUNT_ID missing"}
        r = requests.get(
            f"{self.base}/portfolio/{self.account_id}/summary",
            verify=False,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
