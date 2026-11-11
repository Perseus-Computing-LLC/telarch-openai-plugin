"""severity: low
finding: a chain sealed as a continuation (argus_audit_seal with prev_hash) can never be verified by argus_audit_verify
location: edge/telarch_edge_mcp.js:221 (seal starts from args.prev_hash), :268 (verify always starts from "GENESIS"), verify schema has only `events`
effect: argus_audit_seal declares an optional `prev_hash` "to continue a chain" and returns events whose
  first prev_hash is that value. argus_audit_verify has no matching input and compares the first
  event's prev_hash with the constant GENESIS, so every continuation segment is reported broken at its
  first event. Since the server keeps no state, the only way to verify is to resend the whole chain
  from genesis; the tool description does not say so.
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


def _seal(args):
    return _tool("argus_audit_seal", args)["result"]["structuredContent"]


def _verify(events):
    return _tool("argus_audit_verify", {"events": events})["result"]["structuredContent"]


FIRST = {"events": [{"event_type": "a", "actor": "w", "payload": {"i": 1}}, {"event_type": "b", "actor": "w", "payload": {"i": 2}}]}


def test_control_whole_chain_from_genesis_verifies_including_the_continuation():
    first = _seal(FIRST)
    cont = _seal({"prev_hash": first["head_hash"], "events": [{"sequence": 3, "event_type": "c", "actor": "w", "payload": {"i": 3}}]})
    assert cont["events"][0]["prev_hash"] == first["head_hash"]
    assert _verify(first["events"] + cont["events"])["valid"] is True


def test_continuation_segment_sealed_by_this_server_verifies():
    first = _seal(FIRST)
    cont = _seal({"prev_hash": first["head_hash"], "events": [{"sequence": 3, "event_type": "c", "actor": "w", "payload": {"i": 3}}]})
    out = _verify(cont["events"])
    assert out["valid"] is True, f"untampered continuation reported broken: {out['error_detail']}"
