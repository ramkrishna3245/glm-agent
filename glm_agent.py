#!/usr/bin/env python3
"""
GLM Agent — A CLI coding agent powered by GLM-5.2 (free via Puter or Z.ai).

Like opencode, but you choose the model backend.

Usage:
  set GLM_API_KEY=<puter_token_or_zai_key>
  set GLM_BASE_URL=https://api.puter.com/puterai/openai/v1/
  python glm_agent.py

Or with defaults (Puter):
  set GLM_API_KEY=your_puter_token
  python glm_agent.py
"""

import os, sys, json, subprocess, shlex, base64, re, time
from pathlib import Path
from openai import OpenAI

API_KEY = os.environ.get("GLM_API_KEY", "")
BASE_URL = os.environ.get("GLM_BASE_URL", "https://api.puter.com/puterai/openai/v1/")
MODEL = os.environ.get("GLM_MODEL", "z-ai/glm-5.2")
MAX_TOOLS = 20

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a shell command. Returns stdout+stderr. Use for running code, installing packages, git, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to execute"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Read a file from disk. Returns the contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to file"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Write content to a file. Overwrites existing content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to file"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Search for files matching a pattern. Supports ** wildcards.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern like **/*.py"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for text in files using regex.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern"},
                    "path": {"type": "string", "description": "Directory to search (default: current)"}
                },
                "required": ["pattern"]
            }
        }
    }
]

SYSTEM = (
    "You are GLM Agent, a CLI coding assistant with full access to the user's system. "
    "You can execute bash commands, read/write files, search the codebase, and install packages. "
    "Be concise, direct, and helpful. Use tools to accomplish tasks. "
    "When writing code, test it. When fixing bugs, find the root cause. "
    "When reading files, use the read tool. When executing commands, use the bash tool. "
    "The current working directory is: " + os.getcwd()
)


def run_tool(name, args):
    try:
        if name == "bash":
            cmd = args["command"]
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout
            if result.stderr:
                output += "\n[stderr]\n" + result.stderr[:2000]
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output[:8000] or "(no output)"

        elif name == "read":
            p = Path(args["path"])
            if not p.exists():
                return f"File not found: {p}"
            return p.read_text(encoding="utf-8")[:8000]

        elif name == "write":
            p = Path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"Written {len(args['content'])} bytes to {p}"

        elif name == "glob":
            import glob as g
            matches = g.glob(args["pattern"], recursive=True)
            result = list(matches)[:100]
            return "\n".join(result) if result else "(no matches)"

        elif name == "grep":
            import glob as g
            path = args.get("path", ".")
            matches = []
            for f in g.glob(f"{path}/**", recursive=True):
                p = Path(f)
                if p.is_file() and p.suffix in {".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".bat", ".ps1", ".sh", ".c", ".h", ".cpp", ".java", ".rs", ".go"}:
                    try:
                        text = p.read_text(encoding="utf-8", errors="ignore")
                        for i, line in enumerate(text.split("\n"), 1):
                            if re.search(args["pattern"], line):
                                matches.append(f"{p}:{i}: {line[:200]}")
                    except:
                        pass
            result = matches[:100]
            return "\n".join(result) if result else "(no matches)"

        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Error: {str(e)}"


def chat_loop():
    messages = [{"role": "system", "content": SYSTEM}]
    print(f"GLM Agent [{MODEL}] — 'exit' to quit, '/clear' to reset")
    print("=" * 50)

    while True:
        try:
            user = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user:
            continue
        if user.lower() == "exit":
            break
        if user.lower() == "/clear":
            messages = [{"role": "system", "content": SYSTEM}]
            print("Cleared.")
            continue

        messages.append({"role": "user", "content": user})

        for turn in range(MAX_TOOLS):
            print(f"  [{turn}] GLM-5.2 thinking...", end="", flush=True)
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                    temperature=0.3,
                    max_tokens=4096,
                )
            except Exception as e:
                print(f"\n  API error: {e}")
                break

            msg = response.choices[0].message
            print(f"\r", end="", flush=True)

            if not msg.tool_calls:
                # Text response
                content = msg.content or ""
                print(content)
                messages.append({"role": "assistant", "content": content})
                break

            # Tool calls
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"  [{name}]\n    {json.dumps(args)[:200]}")
                result = run_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
                if result[:200] != "(no output)":
                    for line in result.split("\n")[:8]:
                        print(f"    | {line}")
        else:
            print("  Reached tool call limit.")

    print("\nGoodbye!")


if __name__ == "__main__":
    if not API_KEY:
        print("Error: GLM_API_KEY not set.")
        print("  For Puter: get a token at https://puter.com/dashboard")
        print("  For Z.ai:  get a key at https://z.ai")
        print("  Then: set GLM_API_KEY=<your_key>")
        print("  Or set GLM_BASE_URL and GLM_API_KEY for custom endpoints")
        sys.exit(1)

    chat_loop()
