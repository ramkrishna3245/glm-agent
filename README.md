# GLM Agent — Free CLI Coding Agent Powered by GLM-5.2

A ChatGPT/opencode-like CLI agent that runs on **GLM-5.2** (Zhipu AI's 1M-context flagship) for free. Executes bash commands, reads/writes files, searches code, and installs packages — all through a terminal chat interface.

## How It's Free

GLM-5.2 is accessed through **Puter.js**'s OpenAI-compatible API (`z-ai/glm-5.2`). Get a free auth token at [puter.com/dashboard](https://puter.com/dashboard) — no credit card required. The "user-pays" model means you (the developer) pay nothing.

Alternatively, use **Z.ai's free tier** (1,000 requests/day, no credit card) at [z.ai](https://z.ai).

## Quick Start

```bash
# 1. Install
pip install openai

# 2. Get a free token from https://puter.com/dashboard → "Create token"

# 3. Set env vars and run
set GLM_API_KEY=your_puter_token_here
python glm_agent.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `bash` | Execute any shell command |
| `read` | Read file contents |
| `write` | Write/overwrite files |
| `glob` | Search files by pattern |
| `grep` | Search file contents by regex |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GLM_API_KEY` | (required) | Puter auth token or Z.ai API key |
| `GLM_BASE_URL` | `https://api.puter.com/puterai/openai/v1/` | API endpoint |
| `GLM_MODEL` | `z-ai/glm-5.2` | Model name |

### Alternative: Use Z.ai directly

```bash
set GLM_API_KEY=your_zai_key
set GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
set GLM_MODEL=glm-5.2
python glm_agent.py
```

## Commands

- `exit` — quit
- `/clear` — reset conversation

## Requirements

- Python 3.10+
- `openai` library
- GLM-5.2 supports tool/function calling natively
