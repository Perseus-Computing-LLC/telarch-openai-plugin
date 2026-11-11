"""severity: medium
finding: harpe_synthesize_context ignores any budget above 8192 tokens under the default knapsack_dp policy
location: edge/telarch_edge_mcp.js:89 (`const cap = Math.min(remainingBudget, 8192)`), used at :91-109
effect: the dynamic programme runs over min(remaining budget, 8192) while the response still reports the
  full `effective_budget`. Items that fit the reported budget are pruned once the kept set would pass
  8192 tokens, and a single item larger than 8192 tokens is always pruned. The non-default policies
  (line 119-127) use the full budget, so the same input packs differently by policy for this reason alone.
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


def _synth(args: dict) -> dict:
    return _tool("harpe_synthesize_context", args)["result"]["structuredContent"]


def _words(n: int) -> str:
    return " ".join(f"w{i % 10}" for i in range(n))


BASE = {"reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0}


def test_control_two_items_inside_a_small_budget_are_both_kept():
    out = _synth({**BASE, "total_budget": 8000, "items": [
        {"id": "a", "content": _words(1000), "priority": 50},
        {"id": "b", "content": _words(1000), "priority": 50},
    ]})
    assert out["effective_budget"] == 8000
    assert sorted(out["included_ids"]) == ["a", "b"] and out["pruned_ids"] == []


def test_items_that_fit_the_reported_budget_are_kept():
    out = _synth({**BASE, "total_budget": 100000, "items": [
        {"id": "a", "content": _words(4400), "priority": 50},
        {"id": "b", "content": _words(4400), "priority": 50},
    ]})
    total = sum(i["tokens"] for i in out["included_items"] + out["pruned_items"])
    assert out["effective_budget"] == 100000 and total < out["effective_budget"]
    assert sorted(out["included_ids"]) == ["a", "b"], (
        f"{total} candidate tokens fit effective_budget={out['effective_budget']} but pruned_ids={out['pruned_ids']}"
    )


def test_single_item_larger_than_8192_tokens_is_kept_when_budget_allows():
    out = _synth({**BASE, "total_budget": 100000, "items": [{"id": "a", "content": _words(9000), "priority": 50}]})
    assert out["pruned_items"] or out["included_items"]
    assert out["included_ids"] == ["a"], f"item of {out['pruned_items'][0]['tokens']} tokens pruned under a 100000-token budget"
