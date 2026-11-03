"""Payment handler for POST /payments.

Toy service used by the RCA autonomous remediation reference implementation.
The request/response shapes are defined in api/contract.yaml.
"""
from __future__ import annotations

import hashlib
import math

FEE_RATE = 0.029


def process_payment(request: dict) -> tuple[int, dict]:
    """Handle a POST /payments request. Returns (http_status, response_body)."""
    customer_id = request.get("customer_id", "")
    amount = request.get("amount")

    # Contract: a missing or non-positive amount is rejected with 400 INVALID_AMOUNT.
    # bool is a subclass of int, so exclude it explicitly; reject NaN and infinity too.
    if (
        isinstance(amount, bool)
        or not isinstance(amount, (int, float))
        or not math.isfinite(amount)
        or amount <= 0
    ):
        return 400, {
            "status": "REJECTED",
            "error": {
                "code": "INVALID_AMOUNT",
                "message": "amount must be a number greater than 0",
            },
        }

    fee = round(amount * FEE_RATE, 2)
    total = round(amount + fee, 2)
    payment_id = "PAY-" + hashlib.sha1(f"{customer_id}:{amount}".encode()).hexdigest()[:8]

    return 200, {
        "payment_id": payment_id,
        "status": "ACCEPTED",
        "amount": amount,
        "fee": fee,
        "total": total,
    }
