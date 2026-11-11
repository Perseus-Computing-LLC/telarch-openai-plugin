"""severity: low
finding: the local server answers tools/call for an unknown or missing tool name with a successful result (isError) and not a JSON-RPC error
location: plugins/telarch-local/server/telarch_mcp_server.py:197-201 (dispatch on `name`), :291-292 (`raise ValueError("unknown tool ...")`), :293-301 (every exception becomes an isError result)
effect: MCP 2024-11-05 (the revision this server declares at :21), Server Features > Tools > Error
  Handling, lists "Unknown tools" under Protocol Errors and shows code -32602; isError results are
  for failures inside a tool that ran. A client that separates protocol errors from tool failures
  shows the model "Error in nope: ValueError: unknown tool 'nope'" as tool output, including the
  Python exception class. Same deviation as the hosted server (rv1110_edge_unknown_tool_error.py).
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


def _server():
    return _load_local_module().TelarchMCPServer()


def test_control_known_tool_succeeds_and_unknown_method_is_a_jsonrpc_error(sandbox):
    server = _server()
    ok = _local_call(server, "harpe_budget_evaluate", {"total_budget": 8000})
    assert ok["result"]["isError"] is False and ok["result"]["structuredContent"]["total_budget"] == 8000
    unknown = server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "no/such/method"})
    assert unknown["id"] == 3 and unknown["error"]["code"] == -32601


@pytest.mark.parametrize("name", ["nope", "harpe_nope", "argus_audit_seal"])
def test_unknown_tool_is_a_protocol_error(sandbox, name):
    resp = _local_call(_server(), name, {})
    assert "error" in resp, f"unknown tool answered with a result: {resp['result']['content'][0]['text']!r}"
    assert resp["error"]["code"] == -32602


def test_missing_tool_name_is_a_protocol_error(sandbox):
    resp = _server().handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"arguments": {}}})
    assert "error" in resp and resp["error"]["code"] == -32602
