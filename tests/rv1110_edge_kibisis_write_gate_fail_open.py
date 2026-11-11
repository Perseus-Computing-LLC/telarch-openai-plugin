"""severity: medium
finding: the kibisis_resolve_memory write gate refuses a verified write only when origin is exactly "model"; with origin left out or spelled any other way the write passes
location: edge/telarch_edge_mcp.js:166 (`args.write_attempt.origin === "model" && args.write_attempt.epistemic_state === "verified"`); schema at :405-413 (`write_attempt.origin` is optional, enum model|user)
effect: the gate exists to stop a model from promoting its own text to `verified` ("model-originated
  writes cannot self-promote"). `origin` is optional in the declared schema and nothing checks the
  enum (see rv1110_edge_args_unvalidated), so a caller that sends
  `write_attempt: {"epistemic_state": "verified"}`, or origin "Model" or "assistant", gets an
  ordinary successful result. The result carries no field for the gate's outcome, so "evaluated and
  allowed" cannot be told from "not evaluated". Same fail-open shape as
  rv1110_edge_lease_fail_open. The local server refuses any epistemic_state on kibisis_remember.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGE_JS = ROOT / "edge" / "telarch_edge_mcp.js"


def _node(script: str, prelude: str = ""):
    """Run an async JS body against the worker's handlers in-process (same loader trick as
    tests/test_mcp_contract.py) and return the JSON value the body returns."""
    harness = (
        "const fs = require('fs');\n"
        f"const code = fs.readFileSync({json.dumps(str(EDGE_JS))}, 'utf8');\n"
        + prelude
        + "const { rpc, http } = new Function(code + '\\nreturn {rpc: handleMcpRpcSingle, http: handleMcpHttpRequest};')();\n"
        "const call = async (name, args) => (await rpc({jsonrpc: '2.0', id: 1, method: 'tools/call', params: {name, arguments: args}}));\n"
        "const post = async (body, headers) => { const r = await http(new Request('https://x.invalid/mcp', {method: 'POST', body: typeof body === 'string' ? body : JSON.stringify(body), headers: Object.assign({'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}, headers || {})})); const t = await r.text(); let j = null; try { j = JSON.parse(t); } catch (_) {} return {status: r.status, ct: r.headers.get('content-type'), text: t, json: j}; };\n"
        "(async () => {\n" + script + "\n})().then(o => process.stdout.write(JSON.stringify(o === undefined ? null : o)));\n"
    )
    proc = subprocess.run(["node", "-e", harness], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def _tool(name: str, args) -> dict:
    """tools/call through handleMcpRpcSingle; returns the whole JSON-RPC response."""
    return _node(f"return await call({json.dumps(name)}, {json.dumps(args)});")


def _rejected(resp: dict) -> bool:
    """True when the server refused the call: a JSON-RPC error or a tool result with isError."""
    return "error" in resp or bool(resp.get("result", {}).get("isError"))


import pytest


def _gate(write_attempt) -> dict:
    return _tool("kibisis_resolve_memory", {"query": "x", "write_attempt": write_attempt})


def test_control_model_verified_is_refused_and_user_verified_or_model_candidate_passes():
    refused = _gate({"origin": "model", "epistemic_state": "verified"})
    assert refused["result"]["isError"] is True
    assert "EpistemicTrustViolation" in refused["result"]["content"][0]["text"]
    for ok in ({"origin": "user", "epistemic_state": "verified"}, {"origin": "model", "epistemic_state": "candidate"}):
        assert not _rejected(_gate(ok)), ok


@pytest.mark.parametrize(
    "write_attempt",
    [
        {"epistemic_state": "verified"},
        {"origin": "Model", "epistemic_state": "verified"},
        {"origin": "assistant", "epistemic_state": "verified"},
    ],
    ids=["origin-missing", "origin-Model", "origin-assistant"],
)
def test_verified_write_without_a_known_non_model_origin_is_refused(write_attempt):
    resp = _gate(write_attempt)
    assert _rejected(resp), f"write gate passed {write_attempt} as an ordinary successful result"
