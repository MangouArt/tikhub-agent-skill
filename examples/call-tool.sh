#!/usr/bin/env bash
set -euo pipefail

platform="${1:?Usage: examples/call-tool.sh <platform> <tool-name> <arguments-json>}"
tool_name="${2:?Usage: examples/call-tool.sh <platform> <tool-name> <arguments-json>}"
arguments_json="${3:?Usage: examples/call-tool.sh <platform> <tool-name> <arguments-json>}"

if [[ -z "${TIKHUB_API_KEY:-}" ]]; then
  echo "Missing TIKHUB_API_KEY" >&2
  exit 1
fi

endpoint="https://mcp.tikhub.io/${platform}/mcp"

headers_file="$(mktemp)"
payload_file="$(mktemp)"
trap 'rm -f "$headers_file" "$payload_file"' EXIT

curl -sS -D "$headers_file" -o /dev/null -X POST "$endpoint" \
  -H "Authorization: Bearer ${TIKHUB_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "tikhub-agent-skill",
        "version": "1.0"
      }
    }
  }'

session_id="$(
  awk 'BEGIN{IGNORECASE=1} /^Mcp-Session-Id:/ {gsub("\r",""); print $2}' "$headers_file" | tail -n 1
)"

if [[ -z "$session_id" ]]; then
  echo "Initialize did not return Mcp-Session-Id" >&2
  exit 1
fi

printf '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":%s,"arguments":%s}}' \
  "$(printf '%s' "$tool_name" | jq -Rs .)" \
  "$arguments_json" > "$payload_file"

curl -sS -X POST "$endpoint" \
  -H "Authorization: Bearer ${TIKHUB_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: ${session_id}" \
  --data-binary "@${payload_file}"
