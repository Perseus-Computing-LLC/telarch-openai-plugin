"""severity: medium
finding: argus_audit_verify returns valid:true when it was given no event to verify (missing, misspelled or non-array `events`)
location: edge/telarch_edge_mcp.js:267 (runArgusVerify) and :306-314
effect: `Array.isArray(args.events) ? args.events : []` turns every malformed input into an empty chain,
  and an empty chain is reported as {valid: true, total_events: 0}. `events` is declared required in the
  tool's inputSchema. A caller that passes the chain under the wrong key, or as an object, is told the
  audit trail verified.
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


VERIFY = "argus_audit_verify"


def _sealed():
    return _tool("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {"n": 1}}]})["result"]["structuredContent"]["events"]


def test_control_a_sealed_chain_verifies_and_a_changed_payload_does_not():
    events = _sealed()
    assert _tool(VERIFY, {"events": events})["result"]["structuredContent"]["valid"] is True
    events[0]["payload"]["n"] = 2
    assert _tool(VERIFY, {"events": events})["result"]["structuredContent"]["valid"] is False


def _reports_valid(resp: dict) -> bool:
    return (not _rejected(resp)) and resp["result"]["structuredContent"].get("valid") is True


def test_missing_events_is_not_reported_valid():
    assert not _reports_valid(_tool(VERIFY, {}))


def test_misspelled_events_key_is_not_reported_valid():
    events = _sealed()
    events[0]["payload"]["n"] = 2  # a tampered chain, passed under the wrong key
    assert not _reports_valid(_tool(VERIFY, {"event": events}))


def test_events_given_as_an_object_is_not_reported_valid():
    events = _sealed()
    events[0]["payload"]["n"] = 2
    assert not _reports_valid(_tool(VERIFY, {"events": {"0": events[0]}}))
