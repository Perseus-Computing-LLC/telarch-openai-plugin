"""severity: low
finding: a JSON-RPC response POSTed by the client is answered with a -32601 error object
location: edge/telarch_edge_mcp.js:587-598 and :808-812 (handleMcpRpcSingle treats any object with an id as a request)
effect: MCP 2025-06-18, Base Protocol > Transports > Streamable HTTP > Sending Messages to the Server,
  item 4: "If the input is a JSON-RPC response or notification: if the server accepts the input, the
  server MUST return HTTP status code 202 Accepted with no body"; otherwise an HTTP error status. The
  worker answers 200 with {"error": {"code": -32601, "message": "Method not found: undefined"}} carrying
  the client's own response id, which is a response to a response.
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


def _http(method: str, headers: dict, body=None) -> dict:
    init = {"method": method, "headers": headers}
    if body is not None:
        init["body"] = json.dumps(body)
    script = (
        f"const r = await http(new Request('https://x.invalid/mcp', {json.dumps(init)}));\n"
        "const h = {}; r.headers.forEach((v, k) => { h[k] = v; });\n"
        "return {status: r.status, headers: h, text: await r.text()};"
    )
    return _node(script)


PING = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def test_control_notification_is_202_with_no_body():
    out = _http("POST", JSON_HEADERS, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert out["status"] == 202 and out["text"] == ""


def test_posted_response_gets_no_jsonrpc_reply():
    out = _http("POST", JSON_HEADERS, {"jsonrpc": "2.0", "id": 7, "result": {}})
    assert out["text"] == "" and (out["status"] == 202 or out["status"] >= 400), f"status {out['status']} body {out['text']!r}"
