"""severity: low
finding: the local stdio server writes a response (id null) for requests sent without an id
location: plugins/telarch-local/server/telarch_mcp_server.py:179-201 (initialize, tools/list and tools/call return a response whatever `id` is), :326-328 (main writes it)
effect: JSON-RPC 2.0 section 4.1: a Request object without an "id" member is a Notification and "The
  Server MUST NOT reply to a Notification". Here an id-less initialize, tools/list or tools/call puts
  a line `{"jsonrpc": "2.0", "id": null, "result": ...}` on stdout. A client that sends a tool call as
  a fire-and-forget notification receives an unmatched response; an id-less argus_audit_append also
  appends to the ledger and reports it. Unknown id-less methods are correctly dropped.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EDGE_JS = ROOT / "edge" / "telarch_edge_mcp.js"
LOCAL_PY = ROOT / "plugins" / "telarch-local" / "server" / "telarch_mcp_server.py"
_ENV_PREFIXES = ("KIBISIS_", "ARGUS_", "TELARCH_", "PLUGIN_", "HARPE_")


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """Clean environment: no Telarch variables, HOME/XDG/cwd/PLUGIN_DATA inside pytest's tmp_path."""
    for key in list(os.environ):
        if key.startswith(_ENV_PREFIXES):
            monkeypatch.delenv(key)
    data = tmp_path / "plugin_data"
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "home" / "xdg"))
    monkeypatch.setenv("PLUGIN_DATA", str(data))
    (tmp_path / "home").mkdir()
    (tmp_path / "cwd").mkdir()
    monkeypatch.chdir(tmp_path / "cwd")
    return tmp_path


def _load_local_module():
    spec = importlib.util.spec_from_file_location("telarch_mcp_server", LOCAL_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _local_call(server, name: str, args) -> dict:
    return server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})


def _run_stdio(mod, lines) -> list:
    """Drive the real main() loop with the given stdin lines; return the stdout lines it wrote."""
    out, err = io.StringIO(), io.StringIO()
    saved = sys.stdin, sys.stdout, sys.stderr
    sys.stdin, sys.stdout, sys.stderr = io.StringIO("".join(line + "\n" for line in lines)), out, err
    try:
        rc = mod.main()
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved
    assert rc == 0
    return [ln for ln in out.getvalue().split("\n") if ln != ""]


def _edge_rpc(req: dict) -> dict:
    harness = (
        "const fs = require('fs');\n"
        f"const code = fs.readFileSync({json.dumps(str(EDGE_JS))}, 'utf8');\n"
        "const fn = new Function(code + '\\nreturn handleMcpRpcSingle;')();\n"
        f"(async () => {{ process.stdout.write(JSON.stringify(await fn({json.dumps(req)}))); }})();\n"
    )
    proc = subprocess.run(["node", "-e", harness], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def _edge_call(name: str, args) -> dict:
    return _edge_rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})


def _rejected(resp: dict) -> bool:
    return "error" in resp or bool(resp.get("result", {}).get("isError"))


def _stdout_lines(lines):
    return _run_stdio(_load_local_module(), [json.dumps(x) for x in lines])


def test_control_request_with_id_is_answered_and_declared_notification_is_silent(sandbox):
    out = _stdout_lines([
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "method": "no/such/notification"},
        {"jsonrpc": "2.0", "id": 0, "method": "ping"},
    ])
    assert [json.loads(x) for x in out] == [{"jsonrpc": "2.0", "id": 0, "result": {}}]


@pytest.mark.parametrize("message", [
    {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
    {"jsonrpc": "2.0", "method": "tools/list"},
    {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "harpe_budget_evaluate", "arguments": {"total_budget": 8000}}},
    {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "kibisis_health", "arguments": {}}},
], ids=["initialize", "tools-list", "tools-call-harpe", "tools-call-kibisis"])
def test_message_without_id_gets_no_reply(sandbox, message):
    out = _stdout_lines([message])
    assert out == [], f"notification was answered: {out[0][:120]}"
