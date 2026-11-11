"""severity: medium
finding: harpe_synthesize_context allocates (items + 1) x 8193 Int32 cells with no limit on the number of items
location: edge/telarch_edge_mcp.js:91 (`Array.from({ length: n + 1 }, () => new Int32Array(cap + 1))`), :57 (no bound on args.items); schema `items` has no maxItems
effect: memory and CPU grow as items x min(budget, 8192) regardless of item size. A 144 kB request with
  5,000 one-word items and a 20,000-token budget asks for 163.9 MB of Int32Array (5001 x 8193 x 4),
  more than the 128 MB memory limit Cloudflare documents for a Worker isolate, and runs 41 million
  inner-loop steps. The
  endpoint is unauthenticated. This test replaces Int32Array with a counting stub that hands back one
  shared buffer, so nothing large is really allocated here; behaviour of a live isolate is not tested.
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


PRELUDE = (
    "let __bytes = 0; const __Real = Int32Array; let __shared = null;\n"
    "globalThis.Int32Array = function (n) { __bytes += n * 4; if (!__shared || __shared.length !== n) __shared = new __Real(n); return __shared; };\n"
)
WORKER_MEMORY_LIMIT = 128 * 1024 * 1024


def _alloc(n_items: int) -> dict:
    script = (
        f"const items = Array.from({{length: {n_items}}}, (_, i) => ({{id: 'i' + i, content: 'x'}}));\n"
        "const req = {jsonrpc: '2.0', id: 1, method: 'tools/call', params: {name: 'harpe_synthesize_context', arguments: "
        "{total_budget: 20000, reserved_completion: 0, reserved_tools: 0, safety_margin: 0, items}}};\n"
        "const bodyBytes = JSON.stringify(req).length; const res = await rpc(req);\n"
        "return {bodyBytes, bytes: __bytes, rejected: Boolean(res.error || res.result.isError)};"
    )
    return _node(script, prelude=PRELUDE)


def test_control_small_request_allocates_one_row_per_item():
    out = _alloc(3)
    assert out["rejected"] is False
    assert out["bytes"] == (3 + 1) * (8192 + 1) * 4


def test_request_under_1mb_cannot_ask_for_more_memory_than_an_isolate_has():
    out = _alloc(5000)
    assert out["bodyBytes"] < 1024 * 1024
    assert out["rejected"] or out["bytes"] < WORKER_MEMORY_LIMIT, (
        f"{out['bodyBytes']}-byte request made the handler request {out['bytes']} bytes of Int32Array"
    )
