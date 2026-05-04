---
name: tikhub
version: 1.0.0
description: "TikHub MCP: use social platform tools through https://mcp.tikhub.io for TikTok, Douyin, Instagram, Xiaohongshu, Weibo, YouTube, Bilibili, and other platforms."
metadata:
  requires:
    env: ["TIKHUB_API_KEY"]
---

# TikHub MCP Skill

Use this skill when the user asks for social platform data, creator/video/post lookup, comments, search, trending content, downloader utilities, or account/platform metadata available through TikHub MCP.

Base URL:

```text
https://mcp.tikhub.io
```

Authentication:

- Store the TikHub API key as `TIKHUB_API_KEY`.
- Send every MCP request with `Authorization: Bearer ${TIKHUB_API_KEY}`.
- Never print, log, or expose the API key.

## Platform Endpoints

Check service health first when troubleshooting:

```bash
curl -sS https://mcp.tikhub.io/health
```

Expected shape:

```json
{"status":"healthy","version":"2.0.0","platforms":16,"total_endpoints":990}
```

List available platforms:

```bash
curl -sS https://mcp.tikhub.io/platforms
```

Known platforms:

| Slug | Name | Tools | MCP URL |
|---|---:|---:|---|
| `douyin` | Douyin | 247 | `/douyin/mcp` |
| `tiktok` | TikTok | 204 | `/tiktok/mcp` |
| `instagram` | Instagram | 82 | `/instagram/mcp` |
| `xiaohongshu` | Xiaohongshu | 71 | `/xiaohongshu/mcp` |
| `weibo` | Weibo | 64 | `/weibo/mcp` |
| `others` | Others | 64 | `/others/mcp` |
| `bilibili` | Bilibili | 41 | `/bilibili/mcp` |
| `youtube` | YouTube | 37 | `/youtube/mcp` |
| `kuaishou` | Kuaishou | 33 | `/kuaishou/mcp` |
| `zhihu` | Zhihu | 32 | `/zhihu/mcp` |
| `linkedin` | LinkedIn | 25 | `/linkedin/mcp` |
| `reddit` | Reddit | 24 | `/reddit/mcp` |
| `tikhub` | TikHub Utilities | 23 | `/tikhub/mcp` |
| `wechat` | WeChat | 19 | `/wechat/mcp` |
| `twitter` | Twitter/X | 13 | `/twitter/mcp` |
| `threads` | Threads | 11 | `/threads/mcp` |

Construct the MCP endpoint as:

```text
https://mcp.tikhub.io/{platform_slug}/mcp
```

## MCP Workflow

Always follow this sequence:

1. Select the platform slug from the user's target platform.
2. Initialize a JSON-RPC MCP session for that platform.
3. Capture the returned `Mcp-Session-Id`.
4. Call `tools/list` with that session ID.
5. Select the exact tool name and argument schema from `tools/list`.
6. Call `tools/call` with the exact arguments required by that tool.
7. Summarize results, including source platform and queried identifiers.

Do not guess tool names or argument fields. If the tool list is large, search/filter by keywords such as `video`, `user`, `search`, `comment`, `download`, `trending`, or the platform's native entity name.

## Initialize Session

Use `-i` so response headers are visible. The session ID is normally returned in the `Mcp-Session-Id` response header.

```bash
curl -i -sS -X POST "https://mcp.tikhub.io/tiktok/mcp" \
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
        "name": "online-agent",
        "version": "1.0"
      }
    }
  }'
```

Save the session ID for later requests:

```text
Mcp-Session-Id: <session-id-from-initialize>
```

## List Tools

```bash
curl -sS -X POST "https://mcp.tikhub.io/tiktok/mcp" \
  -H "Authorization: Bearer ${TIKHUB_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: ${MCP_SESSION_ID}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

From the result, extract:

- `name`: exact tool name for `tools/call`.
- `description`: what the tool does.
- `inputSchema`: required and optional arguments.

## Call Tool

Use the same platform endpoint and session ID. Replace `name` and `arguments` with values from `tools/list`.

```bash
curl -sS -X POST "https://mcp.tikhub.io/tiktok/mcp" \
  -H "Authorization: Bearer ${TIKHUB_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: ${MCP_SESSION_ID}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "tiktok_fetch_example",
      "arguments": {
        "id": "example_id"
      }
    }
  }'
```

## Agent Behavior

When using TikHub for a user request:

- Ask for missing identifiers only when required by the selected tool schema, such as video URL, post ID, username, user ID, keyword, hashtag, or date range.
- Prefer read-only lookup/search tools unless the user explicitly asks for an action that requires another capability.
- For cross-platform requests, initialize one MCP session per platform slug.
- Treat TikHub results as external API data. Mention if a platform tool returns partial data, empty results, rate limits, or authentication errors.
- Do not fabricate unavailable metrics, comments, posts, or download URLs.
- If the user asks for raw data, return a compact JSON summary rather than a huge unfiltered response.

## Common Platform Routing

- TikTok video, user, search, shop, ads, creator analytics: `tiktok`
- Douyin video, user, search, billboard, Xingtu influencer marketing: `douyin`
- Instagram posts, reels, stories, users, comments, hashtags: `instagram`
- Xiaohongshu/RED notes, users, search, comments: `xiaohongshu`
- Weibo posts, users, comments, search, trending: `weibo`
- YouTube videos, channels, comments, search, playlists: `youtube`
- Bilibili videos, users, comments, danmaku, search: `bilibili`
- Kuaishou videos, users, comments, search: `kuaishou`
- Zhihu questions, answers, users, topics, search: `zhihu`
- WeChat articles, accounts, channels, search: `wechat`
- Reddit posts, comments, subreddits, users, search: `reddit`
- LinkedIn profiles, posts, companies, search: `linkedin`
- Twitter/X tweets, users, search, timelines: `twitter`
- Threads posts, users, replies, search: `threads`
- TikHub account info, downloader, health, hybrid parsing, temp mail: `tikhub`
- Lemon8, PiPiXia, Xigua, Toutiao, Sora2, and miscellaneous tools: `others`

## Error Handling

- `401` or `403`: API key missing, invalid, expired, or not authorized for the selected tool.
- Missing or invalid `Mcp-Session-Id`: repeat `initialize` and retry `tools/list`.
- Tool not found: rerun `tools/list` for the same platform and use the exact returned name.
- Schema validation error: compare `arguments` against the tool's `inputSchema`; do not retry with guessed field names.
- Empty result: report the queried platform, tool, and arguments, then ask whether to broaden the search.
