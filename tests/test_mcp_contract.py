"""Cross-runtime JSON-RPC 2.0 contract tests for Telarch Edge MCP (JS) and Local Stdio MCP (Python)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGE_JS = ROOT / "edge" / "telarch_edge_mcp.js"
LOCAL_PY = ROOT / "plugins" / "telarch-local" / "server" / "telarch_mcp_server.py"


_ENV_PREFIXES = ("KIBISIS_", "ARGUS_", "TELARCH_", "PLUGIN_", "HARPE_")


def _load_local_server(tmp_path, monkeypatch):
    """Start the local server on a throwaway data directory: nothing is written to the checkout or the real home."""
    for key in list(os.environ):
        if key.startswith(_ENV_PREFIXES):
            monkeypatch.delenv(key)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_DATA_HOME", str(home / "xdg"))
    monkeypatch.setenv("PLUGIN_DATA", str(tmp_path / "plugin_data"))
    # The server points KIBISIS_PASSPHRASE_FILE at its key file; registering the name here makes pytest restore it.
    monkeypatch.setenv("KIBISIS_PASSPHRASE_FILE", "")
    spec = importlib.util.spec_from_file_location("telarch_mcp_server", LOCAL_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TelarchMCPServer()


def _call_edge_rpc(rpc_payload: dict) -> dict:
    harness = (
        "const fs = require('fs');\n"
        f"const code = fs.readFileSync({json.dumps(str(EDGE_JS))}, 'utf8');\n"
        "const fn = new Function(code + '\\nreturn handleMcpRpcSingle;')();\n"
        "(async () => {\n"
        f"  const res = await fn({json.dumps(rpc_payload)});\n"
        "  process.stdout.write(JSON.stringify(res));\n"
        "})();\n"
    )
    proc = subprocess.run(["node", "-e", harness], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def test_edge_and_local_initialize_and_tools_list(tmp_path, monkeypatch):
    local = _load_local_server(tmp_path, monkeypatch)
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    local_init = local.handle_request(init_req)
    edge_init = _call_edge_rpc(init_req)

    assert local_init["result"]["serverInfo"]["name"] == "telarch-mcp"
    assert edge_init["result"]["serverInfo"]["name"] == "telarch-mcp"
    # one version for the two servers and the two plugin manifests, so a client can tell which code it is talking to
    manifests = [json.loads((ROOT / "plugins" / name / "plugin.json").read_text(encoding="utf-8"))["version"] for name in ("telarch", "telarch-local")]
    versions = {local_init["result"]["serverInfo"]["version"], edge_init["result"]["serverInfo"]["version"], *manifests}
    assert versions == {"0.2.0"}, versions

    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    local_tools = {t["name"] for t in local.handle_request(list_req)["result"]["tools"]}
    edge_tools = {t["name"] for t in _call_edge_rpc(list_req)["result"]["tools"]}

    shared = {"harpe_budget_evaluate", "harpe_synthesize_context", "argus_audit_verify"}
    assert shared.issubset(local_tools)
    assert shared.issubset(edge_tools)
    assert "telarch_open_inspector" in edge_tools
    assert not (ROOT / ".telarch").exists(), "the local server wrote into the checkout"
    assert (tmp_path / "plugin_data" / "kibisis_vault.sqlite").is_file()


def test_edge_harpe_and_argus_deterministic_execution():
    synth_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "harpe_synthesize_context",
            "arguments": {
                "total_budget": 100,
                "reserved_completion": 20,
                "reserved_tools": 10,
                "safety_margin": 10,
                "items": [
                    {"id": "c1", "content": "Critical invariant rule", "priority": 10},
                    {"id": "c2", "content": "Low priority note " * 60, "priority": 90},
                ],
            },
        },
    }
    res = _call_edge_rpc(synth_req)
    assert not res["result"].get("isError")
    sc = res["result"]["structuredContent"]
    assert sc["included_ids"] == ["c1"]
    assert sc["pruned_ids"] == ["c2"]

    seal_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "argus_audit_seal",
            "arguments": {
                "events": [
                    {"event_type": "tool_call", "actor": "agent", "payload": {"step": 1, "score_bp": 9500}},
                    {"event_type": "tool_result", "actor": "agent", "payload": {"step": 2, "ok": "true"}},
                ]
            },
        },
    }
    sealed = _call_edge_rpc(seal_req)["result"]["structuredContent"]
    assert sealed["valid"] is True
    assert sealed["total_events"] == 2
    assert len(sealed["head_hash"]) == 64

    verify_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "argus_audit_verify",
            "arguments": {"events": sealed["events"]},
        },
    }
    verified = _call_edge_rpc(verify_req)["result"]["structuredContent"]
    assert verified["valid"] is True
    assert verified["total_events"] == 2

    # Tamper with event 1 payload and assert verification catches sequence 1
    tampered_events = json.loads(json.dumps(sealed["events"]))
    tampered_events[0]["payload"]["score_bp"] = 1000
    tamper_req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "argus_audit_verify",
            "arguments": {"events": tampered_events},
        },
    }
    tampered_res = _call_edge_rpc(tamper_req)["result"]["structuredContent"]
    assert tampered_res["valid"] is False
    assert tampered_res["first_broken_sequence"] == 1
