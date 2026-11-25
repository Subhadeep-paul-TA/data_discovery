"""Web search for Step 2b: print an answer and the citation URLs for one query.

Usage: python scripts/web_search.py "<query>"

Backends
- Gateway (README prompt): POST {ANTHROPIC_BASE_URL}/v1/chat/completions with a Bearer token, model from
  WEB_SEARCH_MODEL (default gemini-3.8-flash), one user message holding the query, and web_search_options: {}.
- Claude Code fallback (used when ANTHROPIC_BASE_URL or ANTHROPIC_AUTH_TOKEN is missing): one headless
  `claude -p` call whose only tool is WebSearch, run from an empty temporary folder with the query on stdin and
  a JSON schema for {answer, citations}.

Results are leads from a search model, not verified sources: open every cited URL yourself.
The token and the full request are never printed.
Exit codes: 0 answer with citations; 1 backend error or missing variable; 2 bad usage; 3 answer without citations.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from typing import NoReturn

DEFAULT_MODEL = "gemini-3.8-flash"
HTTP_TIMEOUT_S = 120
CLI_TIMEOUT_S = 300
GATEWAY_VARS = ("ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN")
KEEP_ENV = ("CLAUDE_CONFIG_DIR", "CLAUDE_CODE_OAUTH_TOKEN")  # where the CLI finds the user's claude.ai login

CITATION_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "citations"],
    "additionalProperties": False,
}

CLI_INSTRUCTION = (
    "Search the web for the query below with the WebSearch tool; do not answer from memory. "
    "Give a short answer. In citations, list the exact URLs of the pages your answer relies on, "
    "copied from the search results, one URL per item.\n\nQuery: "
)


def fail(message: str, code: int = 1) -> NoReturn:
    print(f"web_search: {message}", file=sys.stderr)
    sys.exit(code)


def unique_urls(urls) -> list[str]:
    seen, out = set(), []
    for url in urls:
        if isinstance(url, str):
            url = url.strip()
            if url.startswith(("http://", "https://")) and url not in seen:
                seen.add(url)
                out.append(url)
    return out


# ---------------------------------------------------------------- gateway (README prompt)

def gateway_citations(data: dict, message: dict) -> list[str]:
    """Collect citation URLs from the response shapes OpenAI-compatible gateways use."""
    urls = []
    for ann in message.get("annotations") or []:  # OpenAI: {"type": "url_citation", "url_citation": {"url": ...}}
        if isinstance(ann, dict):
            urls.append((ann.get("url_citation") or {}).get("url") or ann.get("url"))
    for holder in (data, message):  # top-level or message-level "citations": [url, ...]
        for item in holder.get("citations") or []:
            urls.append(item.get("url") if isinstance(item, dict) else item)
    for item in data.get("search_results") or []:
        if isinstance(item, dict):
            urls.append(item.get("url"))
    meta = data.get("vertex_ai_grounding_metadata") or []  # LiteLLM proxy in front of Gemini
    for block in meta if isinstance(meta, list) else [meta]:
        for chunk in (block or {}).get("groundingChunks") or []:
            urls.append(((chunk or {}).get("web") or {}).get("uri"))
    return unique_urls(urls)


def search_gateway(query: str, base_url: str, token: str) -> tuple[str, list[str], str]:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        fail("ANTHROPIC_BASE_URL must not end with /v1 (the script adds /v1/chat/completions)")
    model = os.environ.get("WEB_SEARCH_MODEL") or DEFAULT_MODEL
    body = {"model": model, "messages": [{"role": "user", "content": query}], "web_search_options": {}}
    req = urllib.request.Request(
        base + "/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:500]
        fail(f"gateway returned HTTP {err.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as err:
        fail(f"gateway request failed: {getattr(err, 'reason', err)}")
    except json.JSONDecodeError:
        fail("gateway reply is not JSON")
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        fail("gateway reply has no choices[0].message")
    content = message.get("content") or ""
    if isinstance(content, list):  # content parts
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content.strip(), gateway_citations(data, message), f"gateway ({data.get('model') or model})"


# ---------------------------------------------------------------- Claude Code fallback

def child_env() -> dict:
    """The caller's environment without Claude Code session variables or gateway settings.

    A Claude Code session that runs this script exports CLAUDE_* variables (for example CLAUDE_EFFORT), and a
    half-set gateway (ANTHROPIC_BASE_URL without a token) would redirect the CLI; neither may reach the child.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC_")) or k in KEEP_ENV}


def search_claude_code(query: str, cli: str) -> tuple[str, list[str], str]:
    if "@" in query:  # the CLI turns @<path> in piped text into a local file attachment
        fail("the query contains '@', which the Claude Code CLI would read as a file mention; remove it", 2)
    cmd = [cli, "-p", "--output-format", "json", "--tools", "WebSearch", "--allowedTools", "WebSearch",
           "--strict-mcp-config", "--setting-sources", "", "--safe-mode", "--no-session-persistence",
           "--json-schema", json.dumps(CITATION_SCHEMA)]
    try:
        with tempfile.TemporaryDirectory(prefix="web_search_") as cwd:
            proc = subprocess.run(cmd, input=CLI_INSTRUCTION + query, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", cwd=cwd, env=child_env(),
                                  timeout=CLI_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        fail(f"claude -p gave no reply within {CLI_TIMEOUT_S}s")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        fail(f"claude -p exited {proc.returncode} without a JSON reply: {(proc.stderr or proc.stdout)[:500]}")
    if proc.returncode != 0 or data.get("is_error"):
        fail(f"claude -p failed ({data.get('subtype')}): {str(data.get('result'))[:500]}")
    if data.get("permission_denials"):
        print(f"web_search: warning: permission denials: {data['permission_denials']}", file=sys.stderr)
    reply = data.get("structured_output")
    if not isinstance(reply, dict):
        try:
            reply = json.loads(data.get("result") or "")
        except json.JSONDecodeError:
            fail("claude -p reply has no structured answer")
    models = ", ".join(data.get("modelUsage") or {}) or "CLI default model"
    return (str(reply.get("answer") or "").strip(), unique_urls(reply.get("citations") or []),
            f"Claude Code web-search fallback (claude -p, {models})")


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    if len(argv) != 2 or not argv[1].strip():
        fail('usage: python scripts/web_search.py "<query>"', 2)
    query = argv[1].strip()
    base_url, token = (os.environ.get(k) for k in GATEWAY_VARS)
    if base_url and token:
        answer, citations, backend = search_gateway(query, base_url, token)
    else:
        missing = ", ".join(k for k in GATEWAY_VARS if not os.environ.get(k))
        cli = shutil.which("claude")
        if not cli:
            fail(f"missing {missing}, and the fallback needs the Claude Code CLI ('claude'), which is not on PATH")
        print(f"web_search: {missing} not set; using the Claude Code web-search fallback", file=sys.stderr)
        answer, citations, backend = search_claude_code(query, cli)
    print(f"Backend: {backend}\n")
    print(answer or "(no answer text)")
    print("\nCitations:")
    for i, url in enumerate(citations, 1):
        print(f"{i}. {url}")
    if not citations:
        print("(none)")
        print("web_search: no citations returned; do not suggest anything from this answer", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
