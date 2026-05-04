# TikHub Agent Skill

This repository packages a standalone agent skill for using TikHub MCP at `https://mcp.tikhub.io`.

Online agents can install or read:

```text
https://raw.githubusercontent.com/MangouArt/tikhub-agent-skill/main/SKILL.md
```

## Usage

1. Configure `TIKHUB_API_KEY` in the agent runtime.
2. Read [SKILL.md](./SKILL.md).
3. Select a platform slug such as `tiktok`, `douyin`, `instagram`, `xiaohongshu`, `weibo`, `youtube`, or `bilibili`.
4. Initialize the MCP session.
5. Use `tools/list` to discover exact tool names and schemas.
6. Use `tools/call` with the selected tool name and validated arguments.

## Quick Checks

```bash
curl -sS https://mcp.tikhub.io/health
curl -sS https://mcp.tikhub.io/platforms
```

Example scripts:

- [examples/list-tools.sh](./examples/list-tools.sh)
- [examples/call-tool.sh](./examples/call-tool.sh)

`examples/call-tool.sh` uses `jq` to safely encode the tool name into JSON.

## Security

Do not commit API keys. Pass the key through `TIKHUB_API_KEY` and keep logs free of authorization headers.
