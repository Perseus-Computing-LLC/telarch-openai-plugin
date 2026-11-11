"""Helpers shared by the tests added with the 2026-11-10 review fixes. Test-only; neither server imports this."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGE_JS = ROOT / "edge" / "telarch_edge_mcp.js"
LOCAL_PY = ROOT / "plugins" / "telarch-local" / "server" / "telarch_mcp_server.py"
ENV_PREFIXES = ("KIBISIS_", "ARGUS_", "TELARCH_", "PLUGIN_", "HARPE_")

_NODE_PRELUDE = """
const fs = require('fs');
const code = fs.readFileSync(%s, 'utf8');
const edge = new Function(code + '\\nreturn {rpc: handleMcpRpcSingle, http: handleMcpHttpRequest, tools: MCP_TOOLS, limits: TELARCH_LIMITS, html: INSPECTOR_HTML};')();
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
"""


def node(body: str, payload=None):
    """Run ``body`` (JavaScript, may use ``edge`` and ``input`` and must call ``done(value)`` once) in node."""
    script = (_NODE_PRELUDE % json.dumps(str(EDGE_JS))) + "const done = v => process.stdout.write(JSON.stringify(v));\n" + body
    proc = subprocess.run(["node", "-e", script], input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    return json.loads(proc.stdout)


def edge_rpc_many(messages: list) -> list:
    """Answers of handleMcpRpcSingle for each message, in order (null where no reply is due)."""
    return node("(async () => { const out = []; for (const m of input) out.push(await edge.rpc(m)); done(out); })();", messages)


def edge_call(name: str, arguments: dict) -> dict:
    return edge_rpc_many([{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}])[0]


def edge_http(requests: list) -> list:
    """Send each ``{method, headers, body}`` (body is a string, or ``{"repeat": text, "times": n}`` for a large
    one built inside node) to handleMcpHttpRequest. Returns ``{status, headers, text}`` per request."""
    return node(
        """(async () => {
          const out = [];
          for (const r of input) {
            const init = {method: r.method || 'POST', headers: r.headers || {}};
            if (r.body !== undefined) init.body = typeof r.body === 'string' ? r.body : (r.body.prefix || '') + r.body.repeat.repeat(r.body.times) + (r.body.suffix || '');
            const res = await edge.http(new Request('https://telarch.ai/mcp', init));
            out.push({status: res.status, headers: Object.fromEntries(res.headers.entries()), text: await res.text()});
          }
          done(out);
        })();""",
        requests,
    )


def rejected(response: dict) -> bool:
    """True when a tools/call was refused: a JSON-RPC error, or a result flagged isError."""
    return "error" in response or bool(response.get("result", {}).get("isError"))


def isolate_environment(tmp_path: Path, monkeypatch) -> Path:
    """No Telarch variables; HOME, XDG_DATA_HOME, the working directory and PLUGIN_DATA inside ``tmp_path``."""
    for key in list(os.environ):
        if key.startswith(ENV_PREFIXES):
            monkeypatch.delenv(key)
    (tmp_path / "home").mkdir()
    (tmp_path / "cwd").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "home" / "xdg"))
    monkeypatch.setenv("PLUGIN_DATA", str(tmp_path / "plugin_data"))
    # The server points KIBISIS_PASSPHRASE_FILE at its key file; naming it here makes pytest restore it afterwards.
    monkeypatch.setenv("KIBISIS_PASSPHRASE_FILE", "")
    monkeypatch.chdir(tmp_path / "cwd")
    return tmp_path


def load_local_module():
    spec = importlib.util.spec_from_file_location("telarch_mcp_server", LOCAL_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_call(server, name: str, arguments: dict) -> dict:
    return server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
