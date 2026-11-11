"""severity: medium
finding: argus_audit_verify means two different things on the two servers, and the local one answers valid:true about its own ledger when it is handed a tampered chain
location: plugins/telarch-local/server/telarch_mcp_server.py:121-128 (schema: no properties, additionalProperties false) and :263-272 (arguments never read) against edge/telarch_edge_mcp.js argus_audit_verify (required `events`, verifies the chain passed in)
effect: the hosted tool verifies the `events` array supplied by the caller. The local tool of the same
  name ignores every argument and verifies the on-disk ledger. A caller that follows the hosted
  contract (the inspector UI and plugins/telarch/skills/telarch-setup/SKILL.md:11,19 describe sealing
  and verifying a supplied trail) and passes a tampered chain to the local server is told
  valid:true. The local schema forbids extra arguments but the handler does not enforce it, so the
  mismatch is silent. The same gap exists for every harpe_/argus_ tool in the local server: undeclared
  arguments are dropped without an error.
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


def _tampered_chain() -> list:
    sealed = _edge_call("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {"n": 1}}]})["result"]["structuredContent"]["events"]
    sealed[0]["payload"]["n"] = 2
    return sealed


def test_control_hosted_server_detects_the_tampered_chain_and_local_ledger_verifies(sandbox):
    assert _edge_call("argus_audit_verify", {"events": _tampered_chain()})["result"]["structuredContent"]["valid"] is False
    server = _load_local_module().TelarchMCPServer()
    assert not _rejected(_local_call(server, "argus_audit_append", {"event_type": "t", "actor": "a", "payload": {"n": 1}}))
    out = _local_call(server, "argus_audit_verify", {})["result"]["structuredContent"]
    assert out["valid"] is True and out["total_events"] == 1


def test_local_verify_does_not_report_a_supplied_tampered_chain_as_valid(sandbox):
    server = _load_local_module().TelarchMCPServer()
    resp = _local_call(server, "argus_audit_verify", {"events": _tampered_chain()})
    reported_valid = (not _rejected(resp)) and resp["result"]["structuredContent"]["valid"] is True
    assert not reported_valid, "tampered chain passed as `events` was answered with valid:true"


def test_local_tool_refuses_arguments_its_schema_forbids(sandbox):
    server = _load_local_module().TelarchMCPServer()
    listed = {t["name"]: t for t in server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}
    assert listed["argus_audit_tail"]["inputSchema"]["additionalProperties"] is False
    resp = _local_call(server, "argus_audit_tail", {"limit": 1, "since_sequence": 5})
    assert _rejected(resp), "undeclared argument accepted under additionalProperties:false"
