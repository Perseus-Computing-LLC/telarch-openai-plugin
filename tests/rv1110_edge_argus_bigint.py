"""severity: low
finding: argus_audit_seal accepts integers beyond 2**53-1, so two different payloads seal to the same hash
location: edge/telarch_edge_mcp.js:31-35 (canonicalizeJson number branch tests Number.isInteger only), body parsed with JSON.parse at :862-866
effect: JSON.parse has already rounded 9007199254740993 to 9007199254740992 before the canonicaliser
  sees it, and the canonicaliser accepts any integral double. The sealed event and its hash then
  describe a number the caller did not send. plugins/telarch/skills/telarch-setup/SKILL.md:11 states
  RFC 8785 (JCS) canonical JSON; RFC 8785 section 3.2.2.3 rests on I-JSON (RFC 7493 section 2.2), which
  limits exact integers to [-(2**53)+1, (2**53)-1]. The local server refuses the same payload with
  IntegerRangeError, so the two servers disagree on what can be sealed.
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


def _seal_raw(n_literal: str) -> dict:
    body = '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"argus_audit_seal","arguments":{"events":[{"event_type":"t","actor":"a","timestamp":"2026-01-01T00:00:00Z","event_id":"e1","payload":{"n":' + n_literal + "}}]}}}"
    return _node(f"return (await post({json.dumps(body)})).json;")


def test_control_small_integers_hash_differently_and_floats_are_refused():
    one, two = _seal_raw("1"), _seal_raw("2")
    assert one["result"]["structuredContent"]["head_hash"] != two["result"]["structuredContent"]["head_hash"]
    assert _rejected(_seal_raw("1.5"))


def test_integers_past_two_to_the_53_do_not_collide():
    a, b = _seal_raw("9007199254740992"), _seal_raw("9007199254740993")
    collided = (not _rejected(a)) and (not _rejected(b)) and (
        a["result"]["structuredContent"]["head_hash"] == b["result"]["structuredContent"]["head_hash"]
    )
    assert not collided, "payloads n=2**53 and n=2**53+1 were both sealed with the same event hash"
