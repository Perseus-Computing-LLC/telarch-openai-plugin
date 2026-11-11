"""severity: low
finding: harpe_synthesize_context knapsack values overflow 32 bits, so a priority of 2**31 or more loses to priority 1
location: edge/telarch_edge_mcp.js:91 (`new Int32Array(cap + 1)` table), :94 (`Math.max(1, priority)`), :97-98
effect: item value is stored in an Int32Array; 2147483648 wraps to -2147483648 and the item is never
  chosen. Summed priorities wrap the same way with many ordinary items of large priority. The declared
  schema gives `priority` as an integer with no maximum. Line 94 also maps every priority <= 0 to 1.
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


def _pick(items):
    args = {"total_budget": 6, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": items}
    return _tool("harpe_synthesize_context", args)["result"]["structuredContent"]["included_ids"]


TEXT = "alpha beta gamma delta"  # 6 tokens: exactly one item fits


def test_control_higher_priority_wins_inside_int32():
    assert _pick([{"id": "big", "content": TEXT, "priority": 2147483647}, {"id": "one", "content": TEXT, "priority": 1}]) == ["big"]


def test_priority_of_two_to_the_31_still_wins():
    assert _pick([{"id": "big", "content": TEXT, "priority": 2147483648}, {"id": "one", "content": TEXT, "priority": 1}]) == ["big"]
