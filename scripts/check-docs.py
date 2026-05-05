#!/usr/bin/env python3
"""Check that critical TikHub/NewAPI Agent Gateway docs stay present."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TERMS = [
    "TIKHUB_API_KEY",
    "BILLING_TOKEN",
    "TIKHUB_API_KEY != BILLING_TOKEN",
    "/v1/agent/auth/check",
    "/v1/agents/register/email-code",
    "/v1/agents/register",
    "/v1/agent/balance",
    "/v1/agent/recharge-qr",
    "qr_url",
    "payment_url",
    "image/svg+xml",
    "idempotent",
    "[REDACTED]",
]


def main() -> int:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    missing = [term for term in REQUIRED_TERMS if term not in skill]
    if missing:
        for term in missing:
            print(f"Missing required doc term: {term}")
        return 1
    print(f"OK: {len(REQUIRED_TERMS)} required doc terms present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
