"""severity: low
finding: argus_audit_seal stamps an event that has no timestamp with a fixed date and hashes it into the chain
location: edge/telarch_edge_mcp.js:229 (seal: `String(ev.timestamp || "2026-11-04T00:00:00Z")`), :290 (verify applies the same constant)
effect: `timestamp` is optional in the tool's inputSchema. An audit event sealed without one comes back
  carrying a timestamp the caller never supplied and that is not the time of sealing; it is the same
  constant for every such event on every day, and it is covered by event_hash, so the sealed record
  asserts a time that nothing measured. A reader of the chain cannot tell a real 2026-11-04 event
  from one that had no time at all. The local server's argus_audit_append takes no timestamp from the
  caller; the ledger assigns it. The test accepts a refusal, an absent timestamp, or one within a day
  of the sealing time (so it would pass by coincidence if run on 2026-11-04 or 2026-11-05).
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


import datetime as dt

EVENT = {"event_type": "a", "actor": "x", "payload": {"n": 1}}


def _seal_one(event) -> dict:
    return _tool("argus_audit_seal", {"events": [event]})


def test_control_a_supplied_timestamp_is_kept_and_sealed():
    resp = _seal_one(dict(EVENT, timestamp="2030-01-02T03:04:05Z"))
    ev = resp["result"]["structuredContent"]["events"][0]
    assert ev["timestamp"] == "2030-01-02T03:04:05Z" and len(ev["event_hash"]) == 64


def test_an_event_without_a_timestamp_is_not_given_a_fixed_date():
    resp = _seal_one(EVENT)
    if _rejected(resp):
        return
    stamp = resp["result"]["structuredContent"]["events"][0].get("timestamp")
    if stamp in (None, ""):
        return
    when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    age = abs((dt.datetime.now(dt.timezone.utc) - when).total_seconds())
    assert age < 86400, f"event sealed with timestamp {stamp}, which the caller did not supply and is not the sealing time"
