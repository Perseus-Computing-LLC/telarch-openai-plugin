"""severity: low
finding: tools/call for an unknown tool, or with params that are not an object, returns a result (isError) and not a JSON-RPC error
location: edge/telarch_edge_mcp.js:776-784 (unknown tool), :593 and :688-689 (params used without a shape check)
effect: MCP 2025-06-18, Server Features > Tools > Error Handling, puts "Unknown tools" and "Invalid
  arguments" under Protocol Errors and shows code -32602 with message "Unknown tool: invalid_tool_name";
  isError results are reserved for tool execution errors. JSON-RPC 2.0 section 5.1 defines -32602 for
  invalid method parameters. With params given as an array or a string the server answers
  "Unknown tool: " inside a successful response. The local server has the same behaviour for unknown tools.
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


def _rpc(req: dict) -> dict:
    return _node(f"return await rpc({json.dumps(req)});")


def test_control_unknown_method_is_a_jsonrpc_error():
    resp = _rpc({"jsonrpc": "2.0", "id": 1, "method": "nope"})
    assert resp["error"]["code"] == -32601 and "result" not in resp


def test_unknown_tool_is_invalid_params_error():
    resp = _rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "no_such_tool", "arguments": {}}})
    assert resp.get("error", {}).get("code") == -32602, f"got {resp}"


def test_array_params_for_tools_call_is_invalid_params_error():
    resp = _rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": ["harpe_budget_evaluate"]})
    assert resp.get("error", {}).get("code") == -32602, f"got {resp}"
