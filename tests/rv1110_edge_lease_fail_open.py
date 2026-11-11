"""severity: medium
finding: kibisis_lease_evaluate answers permitted:true when fencing_token or highest_token_seen is missing or not a number
location: edge/telarch_edge_mcp.js:711-727 (tools/call branch "kibisis_lease_evaluate")
effect: Number(undefined) and Number("abc") are NaN, and `NaN < highest` is false, so the stale-token
  check at line 715 is skipped and the handler returns {permitted: true, accepted_fencing_token: null,
  next_monotonic_token: null, holder_id: "undefined"}. The tool's declared inputSchema (lines 317-586,
  tool "kibisis_lease_evaluate") marks holder_id, fencing_token and highest_token_seen as required
  integers; the handler never checks them. A fencing check must fail closed.
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


LEASE = "kibisis_lease_evaluate"


def test_control_stale_token_is_rejected_and_fresh_token_is_permitted():
    stale = _tool(LEASE, {"holder_id": "w", "fencing_token": 1, "highest_token_seen": 100})
    assert _rejected(stale)
    assert "StaleFencingTokenError" in stale["result"]["content"][0]["text"]
    fresh = _tool(LEASE, {"holder_id": "w", "fencing_token": 101, "highest_token_seen": 100})
    assert fresh["result"]["structuredContent"]["permitted"] is True
    assert fresh["result"]["structuredContent"]["accepted_fencing_token"] == 101


def test_missing_required_arguments_are_not_permitted():
    resp = _tool(LEASE, {})
    assert _rejected(resp), f"lease evaluated with no arguments was permitted: {resp['result'].get('structuredContent')}"


def test_non_numeric_fencing_token_is_not_permitted():
    resp = _tool(LEASE, {"holder_id": "w", "fencing_token": "abc", "highest_token_seen": 100})
    assert _rejected(resp), f"non-numeric fencing token was permitted: {resp['result'].get('structuredContent')}"


def test_non_numeric_highest_token_seen_is_not_permitted():
    resp = _tool(LEASE, {"holder_id": "w", "fencing_token": 1, "highest_token_seen": "unknown"})
    assert _rejected(resp), f"token 1 permitted against an unparseable high-water mark: {resp['result'].get('structuredContent')}"
