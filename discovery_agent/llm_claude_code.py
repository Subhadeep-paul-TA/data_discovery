"""Opt-in model backend: Claude through the Claude Code CLI in headless mode (DISCOVERY_BACKEND=claude-code).

For runs without gateway credentials. The pipeline still makes and logs every model call itself; only the
endpoint changes. make_llm() in llm.py picks this class; nothing else in the pipeline knows about it.

Each complete() call runs `claude -p` once:
- in a fresh, empty temporary folder, so no project file, CLAUDE.md or memory can reach the model;
- with no tools (--tools ""), no MCP servers (--strict-mcp-config), none of the user's settings files
  (--setting-sources "") and no customisations such as hooks or plugins (--safe-mode);
- with the agent's own system prompt (--system-prompt) and a JSON schema that the reply must follow;
- with an environment that has no CLAUDE* or ANTHROPIC_* variables, so neither a Claude Code session that
  started the pipeline (its effort level, its session links) nor gateway credentials can change the call.

stdin carries the tool definitions and the whole conversation as JSON in the Anthropic Messages format. The
model replies {"text": ..., "tool_calls": [{"name": ..., "input": {...}}]} through the CLI's StructuredOutput
tool, and the reply becomes SDK-like content blocks, so agent.py runs unchanged. Every at sign in that JSON is
written as \\u0040, because the CLI reads "@<path>" in its input as a request to attach that local file, and a
fetched web page could contain one.

The agent's tools do not exist inside the CLI. A model that calls one directly gets a "No such tool available"
error that the pipeline would never give, and may then act on it (for example, skip the tool). The CLI's event
stream shows such calls, so that reply is discarded and the call repeated.

The CLI still adds a short context block of its own (the login's email address, today's date, the working
folder, the model name). A claude.ai login cannot switch it off, so the request tells the model to ignore it.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass, field

from .llm import LLMError, say
from .trace import Trace

CLI_TIMEOUT_S = 600  # per call; the gateway client uses the same timeout
ATTEMPTS = 4  # first try plus 3 retries, as in llm.py
BACKOFF_S = 2.0  # waits 2s, 4s, 8s between attempts
MAX_SYSTEM_PROMPT_BYTES = 100_000  # passed as one argument; Linux caps a single argument at 128 KiB
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
KEEP_ENV = ("CLAUDE_CONFIG_DIR", "CLAUDE_CODE_OAUTH_TOKEN")  # where the CLI finds the user's login
# CLI messages that no retry can fix (wording from Claude Code 2.1.x)
LOGIN_ERROR = re.compile(r"not logged in|please run /login|session has expired|invalid api key|oauth token has expired", re.I)
LIMIT_ERROR = re.compile(r"usage limit reached|you.ve hit your", re.I)
TOO_LONG_ERROR = re.compile(r"prompt is too long|context limit reached", re.I)
MAX_TOKENS_ERROR = re.compile(r"exceeded the \d+ output token maximum", re.I)  # how the CLI reports a max_tokens cut
REPLY_TOOL = "StructuredOutput"  # the CLI's own tool for a --json-schema reply; any other tool call is a mistake

PREAMBLE = (
    "You are the model inside a tool-using agent that a Python program runs. Your instructions are the system prompt.\n"
    "The agent's tools are not attached to this request, so you cannot call them directly: the only tool you can call here "
    "is StructuredOutput, which carries your reply. To use one of the agent's tools, list the call in the \"tool_calls\" "
    "field of that reply; the program runs it and shows you the result in the next turn. A direct call to an agent tool "
    "fails with \"No such tool available\"; that error comes from this relay, not from the agent's tools.\n"
    "The tool definitions and the conversation so far are given below as JSON in the Anthropic Messages format: your earlier "
    "tool calls are tool_use blocks, and the program's results are tool_result blocks in the next user message. The JSON "
    "writes the at sign as \\u0040.\n"
    "The command-line client that relays this request may add context of its own (an account email address, today's date, "
    "a working folder, environment notes). That context is not part of the agent's task: do not use it, and never copy it "
    "into your replies or tool inputs."
)
CLOSING = (
    "Write the assistant's next turn, as an Anthropic tool-use model would, and send it by calling StructuredOutput once: "
    "any brief text goes in \"text\", and each tool call goes in \"tool_calls\" with the tool's exact name and an input "
    "that follows its input_schema. You may make several independent tool calls in one turn; they run in the order given. "
    "Tool results arrive in the next turn, so never write them yourself. An empty \"tool_calls\" list ends your turn "
    "without a tool call."
)


@dataclass
class TextBlock:
    text: str
    type: str = "text"

    def model_dump(self, exclude_none: bool = True) -> dict:
        return {"type": self.type, "text": self.text}


@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"

    def model_dump(self, exclude_none: bool = True) -> dict:
        return {"type": self.type, "id": self.id, "name": self.name, "input": self.input}


@dataclass
class Usage:
    input_tokens: int = 0  # uncached input plus cache writes
    output_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclass
class Message:
    """The parts of an SDK Message that agent.py and the trace use."""

    content: list
    stop_reason: str
    usage: Usage
    model: str
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:24]}")
    role: str = "assistant"
    type: str = "message"


class _Retry(Exception):
    """A failed call worth repeating. `code` goes to the trace; `detail` only to the console."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code, self.detail = code, detail


class ClaudeCodeLLM:
    """Same interface as llm.LLM: complete(...) returns an object with .content, .stop_reason and .usage."""

    def __init__(self, trace: Trace):
        self.cli = shutil.which("claude")
        if not self.cli:
            raise SystemExit("DISCOVERY_BACKEND=claude-code needs the Claude Code CLI ('claude') on PATH and logged in. "
                             "Install it and log in, or unset DISCOVERY_BACKEND to use the gateway.")
        self.cli_model = os.environ.get("DISCOVERY_MODEL") or None  # ANTHROPIC_MODEL names a gateway model, so it is not used
        self.effort = os.environ.get("DISCOVERY_EFFORT") or None
        if self.effort and self.effort not in EFFORT_LEVELS:
            raise SystemExit(f"DISCOVERY_EFFORT={self.effort!r} is not one of: {', '.join(EFFORT_LEVELS)}.")
        self.model = f"claude-code:{self.cli_model or 'default'}"
        self.trace = trace

    def complete(self, *, agent: str, system: str, messages: list, tools: list[dict], max_tokens: int, turn: int):
        if len(system.encode("utf-8")) > MAX_SYSTEM_PROMPT_BYTES:
            raise SystemExit(f"The {agent} system prompt is over {MAX_SYSTEM_PROMPT_BYTES} bytes, too long to pass to the Claude Code CLI.")
        names = [t["name"] for t in tools]
        cmd = self._command(system, response_schema(names))
        request = render_request(tools, messages)
        for attempt in range(1, ATTEMPTS + 1):
            try:
                msg = self._call(cmd, request, max_tokens, names)
                break
            except _Retry as exc:
                self.trace.event("llm_retry", agent=agent, turn=turn, attempt=attempt, error=exc.code)
                if attempt == ATTEMPTS:
                    raise LLMError(f"Claude Code call failed {attempt} times (last error: {exc.code})") from None
                detail = f": {exc.detail}" if exc.detail else ""
                say(f"  [{agent}] Claude Code call failed ({exc.code}{detail}); retrying {attempt}/{ATTEMPTS - 1}")
                time.sleep(BACKOFF_S * 2 ** (attempt - 1))
        self.trace.event("llm_call", agent=agent, turn=turn, model=self.model, stop_reason=msg.stop_reason,
                         input_tokens=msg.usage.input_tokens, output_tokens=msg.usage.output_tokens,
                         cache_read_input_tokens=msg.usage.cache_read_input_tokens)
        return msg

    def _command(self, system: str, schema: dict) -> list[str]:
        cmd = [self.cli, "-p", "--output-format", "stream-json", "--verbose",  # the event stream shows every tool call
               "--tools", "", "--strict-mcp-config", "--setting-sources", "", "--safe-mode", "--no-session-persistence",
               "--system-prompt", system, "--json-schema", json.dumps(schema)]
        if self.cli_model:
            cmd += ["--model", self.cli_model]
        if self.effort:
            cmd += ["--effort", self.effort]
        return cmd

    def _call(self, cmd: list[str], request: str, max_tokens: int, names: list[str]) -> Message:
        """One CLI run. Returns a Message, raises _Retry for a failure worth repeating, or stops (SystemExit, LLMError)."""
        try:
            with tempfile.TemporaryDirectory(prefix="discovery_cc_") as cwd:
                proc = subprocess.run(cmd, input=request, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                      cwd=cwd, env=child_env(max_tokens), timeout=CLI_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise _Retry("timeout", f"no reply within {CLI_TIMEOUT_S}s") from None
        out, stray = _parse_stream(proc.stdout)
        reply = out.get("structured_output") if out and not out.get("is_error") else None
        calls = _tool_calls(reply, names)
        if calls is not None:
            if stray:  # the model called a tool directly and saw an error the pipeline would never give
                raise _Retry("native_tool_call", ", ".join(sorted(set(stray)))[:200])
            blocks = [TextBlock(reply["text"])] if reply["text"].strip() else []
            blocks += [ToolUseBlock(id=f"toolu_{uuid.uuid4().hex[:24]}", name=n, input=i) for n, i in calls]
            return Message(blocks, "tool_use" if calls else "end_turn", _usage(out), self.model)
        error = " ".join(s for s in (proc.stderr, (out or {}).get("result") if (out or {}).get("is_error") else None)
                         if isinstance(s, str) and s).strip()
        stop = "max_tokens" if MAX_TOKENS_ERROR.search(error) else (out or {}).get("stop_reason")
        if stop in ("refusal", "max_tokens"):  # agent.py handles these exactly as it does on the gateway
            return Message([], stop, _usage(out), self.model)
        status = (out or {}).get("api_error_status")
        _stop_if_hopeless(status, error)
        if out is None:
            raise _Retry(f"exit_{proc.returncode}" if proc.returncode else "no_result", error[:200])
        if proc.returncode or out.get("is_error"):
            raise _Retry(f"api_{status}" if status else "is_error", error[:200])
        raise _Retry("no_reply", str(out.get("subtype") or ""))


def child_env(max_tokens: int) -> dict[str, str]:
    """The caller's environment without Claude Code session variables or gateway credentials, plus two settings."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC_")) or k in KEEP_ENV}
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(max_tokens)  # the agent's max_tokens, as the API would get it
    env["DISABLE_AUTOUPDATER"] = "1"  # no CLI update in the middle of a run
    return env


def response_schema(tool_names: list[str]) -> dict:
    """The reply the CLI must return. Tool inputs stay free-form objects, as for non-strict API tools: the
    pipeline's own validators judge them, so rejected submissions still show up in the trace."""
    call = {"type": "object", "additionalProperties": False, "required": ["name", "input"],
            "properties": {"name": {"type": "string", "enum": tool_names}, "input": {"type": "object"}}}
    return {"type": "object", "additionalProperties": False, "required": ["text", "tool_calls"],
            "properties": {"text": {"type": "string"}, "tool_calls": {"type": "array", "items": call}}}


def render_request(tools: list[dict], messages: list[dict]) -> str:
    """stdin for one call: protocol notes, the tools and the conversation as JSON, then the reply instruction."""
    data = ("TOOLS (JSON, one per line):\n" + _json_lines(tools) + "\n\n"
            "CONVERSATION SO FAR (JSON, one message per line, oldest first):\n" + _json_lines([_message(m) for m in messages]))
    text = PREAMBLE + "\n\n" + data.replace("@", "\\u0040") + "\n\n" + CLOSING  # inside JSON strings, \u0040 still means @
    if "@" in text:  # the fixed text must not contain one either
        raise RuntimeError("request text contains an at sign, which the Claude Code CLI would treat as a file mention")
    return text


def _json_lines(items: list) -> str:
    return "[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, default=str) for x in items) + "\n]"


def _message(m: dict) -> dict:
    """One conversation message in Messages-API form; the SDK-like blocks above become plain dicts."""
    if isinstance(m["content"], str):
        return {"role": m["role"], "content": m["content"]}
    blocks = []
    for b in m["content"]:
        b = b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else b if isinstance(b, dict) else dict(vars(b))
        if b.get("type") == "tool_result":
            b = {"type": "tool_result", "tool_use_id": b.get("tool_use_id"), "is_error": bool(b.get("is_error")),
                 "content": b.get("content")}
        blocks.append(b)
    return {"role": m["role"], "content": blocks}


def _parse_stream(stdout: str) -> tuple[dict | None, list[str]]:
    """From the CLI's event stream: the final result event (or None), and the names of any tools the model called
    other than StructuredOutput."""
    result, stray = None, []
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(ev, dict):
            continue
        if ev.get("type") == "result":
            result = ev
        elif ev.get("type") == "assistant":
            content = (ev.get("message") or {}).get("content")
            for b in content if isinstance(content, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") != REPLY_TOOL:
                    stray.append(str(b.get("name")))
    return result, stray


def _tool_calls(reply, names: list[str]) -> list[tuple[str, dict]] | None:
    """The reply's tool calls as (name, input) pairs, or None when the reply does not fit the schema."""
    if not isinstance(reply, dict) or not isinstance(reply.get("text"), str) or not isinstance(reply.get("tool_calls"), list):
        return None
    calls = []
    for c in reply["tool_calls"]:
        if not (isinstance(c, dict) and c.get("name") in names and isinstance(c.get("input"), dict)):
            return None
        calls.append((c["name"], c["input"]))
    return calls


def _usage(out: dict | None) -> Usage:
    u = (out or {}).get("usage") or {}

    def n(key: str) -> int:
        return int(u.get(key) or 0)

    return Usage(n("input_tokens") + n("cache_creation_input_tokens"), n("output_tokens"), n("cache_read_input_tokens"))


def _stop_if_hopeless(status, error: str) -> None:
    """Failures that no retry can fix: stop the run, as llm.py does for 401/403/404, or fail at once, as for 400."""
    said = f" CLI said: {error[:300]}" if error else ""
    if status == 401 or LOGIN_ERROR.search(error):
        raise SystemExit(f"Claude Code is not logged in, or its login expired. Run `claude` and /login, then re-run.{said}")
    if LIMIT_ERROR.search(error):
        raise SystemExit(f"Claude usage limit reached. Re-run this stage after it resets.{said}")
    if status in (403, 404):
        raise SystemExit(f"Claude Code refused the model or the request ({status}). Check DISCOVERY_MODEL.{said}")
    if status == 400 or TOO_LONG_ERROR.search(error):
        raise LLMError(f"Bad request ({status or 'prompt too long'}) from the Claude Code CLI")
