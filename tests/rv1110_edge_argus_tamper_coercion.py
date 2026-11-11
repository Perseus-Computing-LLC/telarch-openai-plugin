"""severity: medium
finding: argus_audit_verify accepts sealed events whose sequence, actor, payload, timestamp or event_id were altered after sealing
location: edge/telarch_edge_mcp.js:271 (sequence fallback) and :283-291 (String()/`||`/`??` coercion before hashing)
effect: the verifier does not hash the event as received. It rebuilds the envelope with
  `Number.isInteger(ev.sequence) ? ev.sequence : i + 1`, `String(ev.actor || "agent")`,
  `ev.payload ?? {}`, `String(ev.timestamp || <default>)`, `String(ev.event_id || <default>)`. Any
  altered value that coerces back to the sealed one verifies: sequence replaced by "999", 1.5 or
  removed; actor "agent" replaced by "" or null; actor "bob" replaced by ["bob"]; payload {} replaced
  by null or removed; timestamp or event_id removed when the default was sealed. The returned object
  says valid:true and echoes the altered events.
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


import copy

import pytest

SEAL_ARGS = {"events": [
    {"event_type": "t", "actor": "agent", "payload": {}},
    {"event_type": "t2", "actor": "bob", "payload": {"a": 1}},
]}


def _verify_many(mutations: dict) -> dict:
    script = (
        f"const sealed = (await call('argus_audit_seal', {json.dumps(SEAL_ARGS)})).result.structuredContent.events;\n"
        f"const muts = {json.dumps(mutations)}; const out = {{}};\n"
        "for (const [label, ops] of Object.entries(muts)) {\n"
        "  const e = JSON.parse(JSON.stringify(sealed));\n"
        "  for (const [idx, field, mode, value] of ops) { if (mode === 'del') delete e[idx][field]; else e[idx][field] = value; }\n"
        "  const r = (await call('argus_audit_verify', {events: e})).result;\n"
        "  out[label] = r.isError ? false : r.structuredContent.valid;\n"
        "}\nreturn out;"
    )
    return _node(script)


MUTATIONS = {
    "sequence -> '999'": [[0, "sequence", "set", "999"]],
    "sequence -> 1.5": [[0, "sequence", "set", 1.5]],
    "sequence removed": [[1, "sequence", "del", None]],
    "actor 'agent' -> ''": [[0, "actor", "set", ""]],
    "actor 'agent' -> null": [[0, "actor", "set", None]],
    "actor 'bob' -> ['bob']": [[1, "actor", "set", ["bob"]]],
    "payload {} -> null": [[0, "payload", "set", None]],
    "payload removed": [[0, "payload", "del", None]],
    "timestamp removed": [[0, "timestamp", "del", None]],
    "event_id removed": [[0, "event_id", "del", None]],
}


def test_control_untouched_chain_verifies_and_payload_edit_is_detected():
    out = _verify_many({"untouched": [], "payload edit": [[1, "payload", "set", {"a": 2}]]})
    assert out == {"untouched": True, "payload edit": False}


@pytest.mark.parametrize("label", sorted(MUTATIONS))
def test_altered_sealed_event_is_not_reported_valid(label):
    out = _verify_many({label: copy.deepcopy(MUTATIONS[label])})
    assert out[label] is False, f"altered event ({label}) verified as valid"
