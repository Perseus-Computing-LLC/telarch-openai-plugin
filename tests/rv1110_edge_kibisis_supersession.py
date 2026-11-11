"""severity: medium
finding: kibisis_resolve_memory lets a revoked or candidate record supersede a verified record
location: edge/telarch_edge_mcp.js:178 (`supersededKeys` built from every record before any state is looked at), :187-194
effect: the set of superseded keys is collected from all input records, including ones that are then
  tombstoned as revoked. A verified record named by a revoked record's `supersedes_key` is dropped as
  SUPERSEDED and the resolution returns nothing. A `candidate` record (the state the docs give to
  unreviewed model writes) removes a verified record the same way and is returned in its place.
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


def _resolve(records):
    out = _tool("kibisis_resolve_memory", {"query": "", "records": records})["result"]["structuredContent"]
    return {t["key"]: t["status"] for t in out["all_records_trace"]}, [(r["key"], r["epistemic_state"]) for r in out["resolved_records"]]


def test_control_verified_record_supersedes_verified_record():
    trace, resolved = _resolve([
        {"key": "v1", "content": "old", "epistemic_state": "verified"},
        {"key": "v2", "content": "new", "epistemic_state": "verified", "supersedes_key": "v1"},
    ])
    assert trace == {"v1": "SUPERSEDED", "v2": "ACTIVE"}
    assert resolved == [("v2", "verified")]


def test_revoked_record_does_not_supersede():
    trace, resolved = _resolve([
        {"key": "v1", "content": "ground truth", "epistemic_state": "verified"},
        {"key": "bad", "content": "withdrawn", "epistemic_state": "revoked", "supersedes_key": "v1"},
    ])
    assert trace["bad"].startswith("TOMBSTONED")
    assert resolved == [("v1", "verified")], f"verified record suppressed by a revoked one: trace={trace}"


def test_candidate_record_does_not_displace_verified_record():
    _, resolved = _resolve([
        {"key": "v1", "content": "ground truth", "epistemic_state": "verified"},
        {"key": "guess", "content": "unreviewed model write", "epistemic_state": "candidate", "supersedes_key": "v1"},
    ])
    assert ("v1", "verified") in resolved, f"verified record replaced by {resolved}"
