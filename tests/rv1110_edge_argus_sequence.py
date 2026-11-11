"""severity: low
finding: argus_audit_seal seals, and argus_audit_verify reports valid, a chain whose sequence numbers repeat or go backwards
location: edge/telarch_edge_mcp.js:225 (seal takes any integer `sequence` from the caller), :271 (verify does the same and never compares it with the previous event)
effect: both tools describe a "linear SHA-256 hash-chain ... from GENESIS", and verify's description says
  it isolates "the exact sequence number of any mid-chain tampering". With caller-supplied sequences
  7, 7, 3 the chain is sealed and verified as valid, so `first_broken_sequence` cannot identify one
  event, and a consumer that orders or deduplicates by sequence reads a different history from the
  one the hashes cover. The local server's argus_audit_append takes no sequence from the caller; the
  ledger assigns it.
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


EVENTS = [{"event_type": "a", "actor": "x", "payload": {"n": i}} for i in range(3)]


def _sealed(events) -> dict:
    return _tool("argus_audit_seal", {"events": events})


def _strictly_increasing(seqs) -> bool:
    return all(b > a for a, b in zip(seqs, seqs[1:]))


def test_control_default_sequences_are_1_2_3_and_tampering_is_located():
    sealed = _sealed(EVENTS)["result"]["structuredContent"]["events"]
    assert [e["sequence"] for e in sealed] == [1, 2, 3]
    assert _tool("argus_audit_verify", {"events": sealed})["result"]["structuredContent"]["valid"] is True
    sealed[1]["payload"]["n"] = 99
    broken = _tool("argus_audit_verify", {"events": sealed})["result"]["structuredContent"]
    assert broken["valid"] is False and broken["first_broken_sequence"] == 2


def test_seal_does_not_emit_repeated_or_descending_sequences():
    resp = _sealed([dict(e, sequence=s) for e, s in zip(EVENTS, (7, 7, 3))])
    if _rejected(resp):
        return
    seqs = [e["sequence"] for e in resp["result"]["structuredContent"]["events"]]
    assert _strictly_increasing(seqs), f"sealed chain carries sequences {seqs}"


def test_verify_does_not_report_a_chain_with_repeated_sequences_as_valid():
    # fix/review-20261110: argus_audit_seal now refuses sequences 7, 7, 3 in one call, so the chain is built from
    # three one-event segments, each sealed onto the previous head. Every hash is genuine; only the numbering is bad.
    sealed, prev = [], "GENESIS"
    for e, s in zip(EVENTS, (7, 7, 3)):
        segment = _tool("argus_audit_seal", {"prev_hash": prev, "events": [dict(e, sequence=s)]})["result"]["structuredContent"]
        sealed += segment["events"]
        prev = segment["head_hash"]
    assert [e["sequence"] for e in sealed] == [7, 7, 3]
    resp = _tool("argus_audit_verify", {"events": sealed})
    assert _rejected(resp) or resp["result"]["structuredContent"]["valid"] is False, "sequences 7, 7, 3 verified as a valid linear chain"
