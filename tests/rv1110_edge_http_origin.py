"""severity: low
finding: /mcp never looks at the Origin header and sends Access-Control-Allow-Origin: * on every response
location: edge/telarch_edge_mcp.js:815-821 (MCP_CORS_HEADERS), :823-890 (no read of request.headers.get("Origin"))
effect: MCP 2025-06-18, Base Protocol > Transports > Streamable HTTP > Security Warning, item 1:
  "Servers MUST validate the Origin header on all incoming connections to prevent DNS rebinding
  attacks". Any web page can call every tool from a visitor's browser; Authorization is also in
  Access-Control-Allow-Headers although the server has no authentication. Impact is small while the
  endpoint stays anonymous and stateless (no cookies, no session, nothing stored), which is why this
  is low; it becomes a real exposure the day a credential or per-user state is added.
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


def test_control_request_without_origin_is_served_with_no_store():
    out = _http("POST", JSON_HEADERS, PING)
    assert out["status"] == 200 and out["headers"]["cache-control"] == "no-store"


def test_unlisted_origin_is_not_admitted():
    out = _http("POST", {**JSON_HEADERS, "Origin": "https://evil.example"}, PING)
    admitted = out["headers"].get("access-control-allow-origin") in ("*", "https://evil.example")
    assert out["status"] == 403 or not admitted, (
        f"status {out['status']}, Access-Control-Allow-Origin={out['headers'].get('access-control-allow-origin')!r}"
    )
