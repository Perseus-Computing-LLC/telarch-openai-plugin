"""severity: medium
finding: harpe_synthesize_context has the same name on both servers and returns different packings for the same arguments
location: plugins/telarch-local/server/telarch_mcp_server.py:235 (`TokenBudget(total_budget=...)` only: reserved_completion, reserved_tools and safety_margin are never read) against edge/telarch_edge_mcp.js:49-57 (reservations default to 2048/1024/512 and are subtracted); policy handling at server:236 against edge:87,118-127
effect: (1) for total_budget 8000 the hosted server packs into 4416 tokens and the local server into
  8000, although the local server's own harpe_budget_evaluate (server:209-214) reports 4416 available
  for the same budget; (2) the local schema (server:58, tool harpe_synthesize_context) does not declare
  reserved_completion/reserved_tools/safety_margin, and a call that passes them is accepted and they are ignored; (3) policy
  `fifo` keeps the later item locally and the higher-priority item on the hosted server; (4) the
  local tool accepts policies truncate_tail, least_relevant and duo_attention that the hosted enum
  does not have. The skill documents are byte-identical for both plugins and README.md describes one
  Harpe; nothing says the two differ. Token counts also differ (the same six-word text is 7 tokens
  locally and 8 hosted), which is noted but not asserted here.
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


def _both(sandbox_unused, args: dict):
    server = _load_local_module().TelarchMCPServer()
    local = _local_call(server, "harpe_synthesize_context", args)["result"]["structuredContent"]
    edge = _edge_call("harpe_synthesize_context", args)["result"]["structuredContent"]
    return local, edge


def test_control_both_servers_keep_a_small_item_and_report_knapsack_dp(sandbox):
    local, edge = _both(sandbox, {"total_budget": 8000, "items": [{"id": "a", "content": "hello world"}]})
    assert local["included_ids"] == edge["included_ids"] == ["a"]
    assert local["policy_applied"] == edge["policy_applied"] == "knapsack_dp"


def test_default_effective_budget_agrees(sandbox):
    local, edge = _both(sandbox, {"total_budget": 8000, "items": [{"id": "a", "content": "hello world"}]})
    assert local["effective_budget"] == edge["effective_budget"], f"local {local['effective_budget']} vs hosted {edge['effective_budget']}"


def test_local_effective_budget_matches_its_own_budget_tool(sandbox):
    server = _load_local_module().TelarchMCPServer()
    available = _local_call(server, "harpe_budget_evaluate", {"total_budget": 8000})["result"]["structuredContent"]["available_context"]
    packed = _local_call(server, "harpe_synthesize_context", {"total_budget": 8000, "items": []})["result"]["structuredContent"]["effective_budget"]
    assert packed == available, f"harpe_budget_evaluate says {available} available, harpe_synthesize_context packs into {packed}"


def test_reserved_completion_is_honoured_or_refused_locally(sandbox):
    args = {"total_budget": 8000, "reserved_completion": 7990, "reserved_tools": 0, "safety_margin": 0,
            "items": [{"id": "a", "content": "hello world " * 20}]}
    edge = _edge_call("harpe_synthesize_context", args)["result"]["structuredContent"]
    assert edge["included_ids"] == [] and edge["effective_budget"] == 10
    resp = _local_call(_load_local_module().TelarchMCPServer(), "harpe_synthesize_context", args)
    # The local schema does not declare reserved_* and sets additionalProperties:false, so refusing is also correct.
    assert _rejected(resp) or resp["result"]["structuredContent"]["included_ids"] == [], (
        f"local kept {resp['result']['structuredContent']['included_ids']} and ignored reserved_completion without an error"
    )


def test_fifo_picks_the_same_survivor_on_both(sandbox):
    args = {"total_budget": 10, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "policy": "fifo", "items": [
        {"id": "first", "content": "one two three four five six", "priority": 99},
        {"id": "second", "content": "one two three four five six", "priority": 1},
    ]}
    local, edge = _both(sandbox, args)
    assert local["included_ids"] == edge["included_ids"], f"local {local['included_ids']} vs hosted {edge['included_ids']}"
