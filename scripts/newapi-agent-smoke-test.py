#!/usr/bin/env python3
"""Smoke test Mangou NewAPI Agent Gateway without printing secrets."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://mangou-newapi.zeabur.app"
DEFAULT_AGENT_ID = "tikhub-agent"


def redact(value: str) -> str:
    return "[REDACTED]" if value else ""


def request_json(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, dict, str]:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw else {}
            return resp.status, parsed, resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"error": raw}
        return exc.code, parsed, exc.headers.get("Content-Type", "")


def request_head_or_get(url: str) -> tuple[int, str]:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if method == "GET":
                    resp.read(512)
                return resp.status, resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (405, 501):
                continue
            return exc.code, exc.headers.get("Content-Type", "")
    return 0, ""


def data_field(payload: dict) -> dict:
    data = payload.get("data")
    return data if isinstance(data, dict) else payload


def balance_value(payload: dict) -> int | None:
    data = data_field(payload)
    for key in ("balance", "quota"):
        value = data.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def print_step(name: str, status: int, payload: dict | None = None, content_type: str = "") -> None:
    summary = {"step": name, "status": status}
    if content_type:
        summary["content_type"] = content_type
    if payload is not None:
        safe_payload = json.loads(json.dumps(payload))
        for token_key in ("token", "billing_token", "authorization"):
            if token_key in safe_payload:
                safe_payload[token_key] = "[REDACTED]"
            if isinstance(safe_payload.get("data"), dict) and token_key in safe_payload["data"]:
                safe_payload["data"][token_key] = "[REDACTED]"
        summary["response"] = safe_payload
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("NEWAPI_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--agent-id", default=os.environ.get("AGENT_ID", DEFAULT_AGENT_ID))
    parser.add_argument("--recharge", action="store_true", help="exercise demo recharge QR and payment_url idempotency")
    parser.add_argument("--tier", default="gems_100")
    parser.add_argument("--amount", type=int, default=100)
    args = parser.parse_args()

    token = os.environ.get("BILLING_TOKEN", "").strip()
    if not token:
        print("Missing BILLING_TOKEN", file=sys.stderr)
        return 2

    base_url = args.base_url.rstrip("/")
    print(json.dumps({"base_url": base_url, "billing_token": redact(token)}, sort_keys=True))

    status, payload, content_type = request_json("GET", f"{base_url}/v1/agent/auth/check", token)
    print_step("auth_check", status, payload, content_type)
    if status >= 400:
        return 1

    status, before_payload, content_type = request_json("GET", f"{base_url}/v1/agent/balance", token)
    print_step("balance_before", status, before_payload, content_type)
    if status >= 400:
        return 1
    before_balance = balance_value(before_payload)

    if not args.recharge:
        return 0

    status, recharge_payload, content_type = request_json(
        "POST",
        f"{base_url}/v1/agent/recharge-qr",
        token,
        {
            "agent_id": args.agent_id,
            "tier": args.tier,
            "amount": args.amount,
        },
    )
    print_step("recharge_qr", status, recharge_payload, content_type)
    if status >= 400:
        return 1

    recharge_data = data_field(recharge_payload)
    qr_url = str(recharge_data.get("qr_url", ""))
    payment_url = str(recharge_data.get("payment_url", ""))
    if not qr_url or not payment_url:
        print("Missing qr_url or payment_url", file=sys.stderr)
        return 1

    qr_status, qr_content_type = request_head_or_get(qr_url)
    print_step("qr_url", qr_status, content_type=qr_content_type)
    if qr_status >= 400 or "image/svg+xml" not in qr_content_type:
        return 1

    pay_status, pay_content_type = request_head_or_get(payment_url)
    print_step("payment_url_first_open", pay_status, content_type=pay_content_type)
    if pay_status >= 400:
        return 1

    status, after_payload, content_type = request_json("GET", f"{base_url}/v1/agent/balance", token)
    print_step("balance_after", status, after_payload, content_type)
    if status >= 400:
        return 1
    after_balance = balance_value(after_payload)

    pay_status, pay_content_type = request_head_or_get(payment_url)
    print_step("payment_url_second_open", pay_status, content_type=pay_content_type)
    if pay_status >= 400:
        return 1

    status, final_payload, content_type = request_json("GET", f"{base_url}/v1/agent/balance", token)
    print_step("balance_final", status, final_payload, content_type)
    if status >= 400:
        return 1
    final_balance = balance_value(final_payload)

    idempotent = after_balance == final_balance
    increased = before_balance is None or after_balance is None or after_balance >= before_balance
    print(json.dumps({"balance_increased": increased, "payment_idempotent": idempotent}, sort_keys=True))
    return 0 if idempotent and increased else 1


if __name__ == "__main__":
    raise SystemExit(main())
