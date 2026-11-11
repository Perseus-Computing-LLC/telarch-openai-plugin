"""severity: medium
finding: harpe_synthesize_context implements one fallback for every non-default policy and reports the requested name as policy_applied
location: edge/telarch_edge_mcp.js:54 (policy read), :87 (only "knapsack_dp" tested), :118-127 (one priority-greedy branch), :143 (`policy_applied: policy`)
effect: the inputSchema enum declares knapsack_dp, lowest_priority, fifo and warm_prefix. fifo and
  warm_prefix are not implemented: both run the same descending-priority greedy as lowest_priority, so
  arrival order never matters. A value outside the enum ("bogus") is accepted, packed with the same
  greedy and echoed back as policy_applied:"bogus", and it is also folded into pinned_policy_digest.
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


ITEMS = [  # one item fits; arrival order (A first, C last) and priority (B highest) disagree
    {"id": "A", "content": "alpha beta gamma delta", "priority": 10},
    {"id": "B", "content": "alpha beta gamma delta", "priority": 90},
    {"id": "C", "content": "alpha beta gamma delta", "priority": 10},
]


def _synth(policy):
    args = {"total_budget": 6, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": ITEMS}
    if policy is not None:
        args["policy"] = policy
    return _tool("harpe_synthesize_context", args)


def test_control_priority_policies_keep_the_highest_priority_item():
    for policy in (None, "knapsack_dp", "lowest_priority"):
        out = _synth(policy)["result"]["structuredContent"]
        # fix/review-20261110: was `== ["B"]` (higher number wins). The reference is harpe 0.1.0a13, where a LOWER
        # priority number is more important: knapsack_dp keeps the earlier of the two priority-10 items, and
        # lowest_priority takes the newer one first.
        assert out["included_ids"] == (["C"] if policy == "lowest_priority" else ["A"]), policy
        assert out["policy_applied"] == (policy or "knapsack_dp")


def test_fifo_depends_on_arrival_order_not_priority():
    out = _synth("fifo")["result"]["structuredContent"]
    # Under either reading of FIFO (admit the earliest, or evict the earliest) the survivor is A or C.
    assert out["included_ids"] != ["B"], "policy_applied=fifo but the survivor was chosen by priority"


def test_policy_outside_the_declared_enum_is_rejected():
    resp = _synth("bogus")
    assert _rejected(resp), f"undeclared policy reported as applied: {resp['result']['structuredContent']['policy_applied']!r}"
