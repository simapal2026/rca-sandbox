"""Visible test suite for POST /payments.

    python -m unittest discover -s tests -v

Standard library only, so it runs in any Python 3 without installing anything.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from payment import process_payment  # noqa: E402

CONTRACT = (ROOT / "api" / "contract.yaml").read_text()
# Flat "code: NAME" lines are the documented error codes (kept simple to avoid a YAML dependency).
CONTRACT_ERROR_CODES = re.findall(r"^\s*code:\s*([A-Z_]+)\s*$", CONTRACT, re.MULTILINE)


class AcceptedPayment(unittest.TestCase):
    def test_valid_payment_is_accepted(self) -> None:
        status, body = process_payment({"customer_id": "C-1", "amount": 100.0})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ACCEPTED")
        self.assertEqual(body["fee"], 2.9)
        self.assertEqual(body["total"], 102.9)

    def test_fee_is_rounded_to_two_places(self) -> None:
        _, body = process_payment({"customer_id": "C-1", "amount": 33.33})
        self.assertEqual(body["fee"], 0.97)
        self.assertEqual(body["total"], 34.3)

    def test_accepted_response_keeps_contract_shape(self) -> None:
        _, body = process_payment({"customer_id": "C-1", "amount": 10.0})
        self.assertEqual(sorted(body), ["amount", "fee", "payment_id", "status", "total"])


class MissingAmount(unittest.TestCase):
    """The reported defect: a request without an amount must be rejected, not crash."""

    def test_missing_amount_is_rejected_with_400(self) -> None:
        status, body = process_payment({"customer_id": "C-1"})
        self.assertEqual(status, 400)
        self.assertEqual(body["status"], "REJECTED")
        self.assertEqual(body["error"]["code"], "INVALID_AMOUNT")

    def test_rejection_uses_a_code_from_the_contract(self) -> None:
        _, body = process_payment({"customer_id": "C-1"})
        self.assertIn(body["error"]["code"], CONTRACT_ERROR_CODES)


if __name__ == "__main__":
    unittest.main()
