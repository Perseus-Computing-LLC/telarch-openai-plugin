"""severity: low
finding: GET /mcp without an SSE Accept header answers 200 application/json; the transport allows only an event stream or 405
location: edge/telarch_edge_mcp.js:830-858 (GET branch; JSON server card at :841-857)
effect: MCP 2025-06-18, Base Protocol > Transports > Streamable HTTP > Listening for Messages from the
  Server, item 2: "The server MUST either return Content-Type: text/event-stream in response to this
  HTTP GET, or else return HTTP 405 Method Not Allowed". The worker returns a JSON description of the
  server with status 200. (With Accept: text/event-stream it returns a one-comment stream that ends at
  once; see the notes, 'Suspected, unconfirmed'.)
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


def test_control_get_with_sse_accept_returns_event_stream_and_put_is_405():
    out = _http("GET", {"Accept": "text/event-stream"})
    assert out["status"] == 200 and out["headers"]["content-type"].startswith("text/event-stream")
    assert _http("PUT", {"Accept": "*/*"})["status"] == 405


def test_get_without_sse_accept_is_event_stream_or_405():
    out = _http("GET", {"Accept": "application/json"})
    ok = out["status"] == 405 or out["headers"].get("content-type", "").startswith("text/event-stream")
    assert ok, f"status {out['status']} content-type {out['headers'].get('content-type')}"
