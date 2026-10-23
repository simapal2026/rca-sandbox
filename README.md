# rca-sandbox

A deliberately tiny service used as the remediation target for the RCA autonomous remediation
reference implementation. It contains one known defect, so the pipeline has something real to fix.

```
src/payment.py          POST /payments handler (contains the defect)
tests/test_payment.py   visible test suite
api/contract.yaml       API contract; must not be changed by an automated fix
```

Run the tests (standard library only):

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Do not edit `api/contract.yaml` or the tests to make a fix pass.
