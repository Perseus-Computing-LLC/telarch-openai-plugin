"""severity: medium
finding: tools/call never checks arguments against the tool's declared inputSchema; missing, mistyped and undeclared arguments return success
location: edge/telarch_edge_mcp.js:687-689 (arguments taken as-is) and each handler (:49-57, :695-699, :711-714); schemas at :317-586
effect: every tool in tools/list declares `required`, typed properties and additionalProperties:false,
  but tools/call coerces with Number()/String() and returns isError:false. harpe_budget_evaluate with
  total_budget "abc" returns total_budget:null and is_exceeded:false; harpe_synthesize_context with no
  arguments succeeds though total_budget and items are required; undeclared arguments are ignored.
  MCP 2025-06-18, Server Features > Tools > Security Considerations: "Servers MUST validate all tool
  inputs"; same page, Error Handling, lists invalid arguments as an error case.
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


def test_control_valid_arguments_succeed():
    resp = _tool("harpe_budget_evaluate", {"total_budget": 8000, "current_usage": 100})
    assert not _rejected(resp)
    assert resp["result"]["structuredContent"]["available_context"] == 8000 - 2048 - 1024 - 512


def test_declared_schema_requires_what_the_tests_below_omit():
    tools = {t["name"]: t for t in _node("return (await rpc({jsonrpc: '2.0', id: 1, method: 'tools/list'})).result.tools;")}
    synth = tools["harpe_synthesize_context"]["inputSchema"]
    assert set(synth["required"]) == {"total_budget", "items"} and synth["additionalProperties"] is False
    assert tools["harpe_budget_evaluate"]["inputSchema"]["properties"]["total_budget"]["type"] == "integer"


def test_wrong_type_for_declared_integer_is_rejected():
    resp = _tool("harpe_budget_evaluate", {"total_budget": "abc"})
    assert _rejected(resp), f"non-integer total_budget accepted: {resp['result'].get('structuredContent')}"


def test_missing_required_arguments_are_rejected():
    resp = _tool("harpe_synthesize_context", {})
    assert _rejected(resp), "call without the required total_budget and items succeeded"


def test_undeclared_argument_is_rejected():
    resp = _tool("harpe_budget_evaluate", {"total_budget": 8000, "curent_usage": 9000})
    assert _rejected(resp), "misspelled argument silently ignored under additionalProperties:false"


def test_items_of_the_wrong_shape_are_rejected():
    resp = _tool("harpe_synthesize_context", {"total_budget": 8000, "items": "one two three"})
    assert _rejected(resp), "items given as a string was treated as an empty list"
