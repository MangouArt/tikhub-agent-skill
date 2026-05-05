# TikHub Agent Skill

This repository packages a standalone agent skill for using TikHub MCP at `https://mcp.tikhub.io`.

Online agents can install or read:

```text
https://raw.githubusercontent.com/MangouArt/tikhub-agent-skill/main/SKILL.md
```

## Usage

1. Configure `TIKHUB_API_KEY` in the agent runtime for direct TikHub MCP calls.
2. Read [SKILL.md](./SKILL.md).
3. Select a platform slug such as `tiktok`, `douyin`, `instagram`, `xiaohongshu`, `weibo`, `youtube`, or `bilibili`.
4. Initialize the MCP session.
5. Use `tools/list` to discover exact tool names and schemas.
6. Use `tools/call` with the selected tool name and validated arguments.

## Token Boundary

This skill documents two independent paths:

- TikHub MCP uses `TIKHUB_API_KEY`.
- Mangou NewAPI Agent Gateway uses `BILLING_TOKEN`.

`TIKHUB_API_KEY` is never valid for `/v1/agent/*`, and `BILLING_TOKEN` is never valid for `https://mcp.tikhub.io/{platform}/mcp`.

The optional Mangou NewAPI Agent Gateway reference in [SKILL.md](./SKILL.md) covers registration, auth check, balance check, and demo recharge.

## Quick Checks

```bash
curl -sS https://mcp.tikhub.io/health
curl -sS https://mcp.tikhub.io/platforms
```

Example scripts:

- [examples/list-tools.sh](./examples/list-tools.sh)
- [examples/call-tool.sh](./examples/call-tool.sh)
- [scripts/newapi-agent-smoke-test.py](./scripts/newapi-agent-smoke-test.py)

`examples/call-tool.sh` uses `jq` to safely encode the tool name into JSON.

## Security

Do not commit API keys. Pass TikHub MCP credentials through `TIKHUB_API_KEY`, pass NewAPI gateway credentials through `BILLING_TOKEN`, and keep logs free of authorization headers.
