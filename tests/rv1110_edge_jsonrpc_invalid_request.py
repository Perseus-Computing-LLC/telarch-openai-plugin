"""severity: low
finding: the worker does not detect invalid Request objects: empty batch and id-less invalid objects get 202 with no body; missing jsonrpc, object ids and non-string methods are served
location: edge/telarch_edge_mcp.js:596-598 (anything without `id` is treated as a notification before validation), :869-873 (empty batch), :587-593 (no check of jsonrpc, id type, method type)
effect: JSON-RPC 2.0 section 6: an empty batch array gets a single Invalid Request response; section 7
  examples: `[]` and `{"jsonrpc": "2.0", "method": 1, "params": "bar"}` both answer
  {"error": {"code": -32600}, "id": null}; section 4: jsonrpc MUST be exactly "2.0", id MUST be a
  String, Number or NULL, method is a String. Here `[]`, `{}` and `{"method": 1}` are answered 202 with
  an empty body, so a client with a malformed message waits for nothing; `{"id": 1, "method": "ping"}`
  and jsonrpc "1.0" are served; an id of {"a": 1} is echoed back; a numeric method with an id answers
  -32601 "Method not found: 5".
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


import pytest


def _post(body):
    return _node(f"return await post({json.dumps(body)});")


def test_control_parse_error_notification_and_valid_request():
    out = _node(
        "return {bad: await post('{not json'), note: await post({jsonrpc: '2.0', method: 'notifications/initialized'}),"
        " ping: await post({jsonrpc: '2.0', id: 'abc', method: 'ping'}), zero: await post({jsonrpc: '2.0', id: 0, method: 'ping'}),"
        " scalar: await post([1])};"
    )
    assert out["bad"]["status"] == 400 and out["bad"]["json"]["error"]["code"] == -32700 and out["bad"]["json"]["id"] is None
    assert out["note"]["status"] == 202 and out["note"]["text"] == ""
    assert out["ping"]["json"] == {"jsonrpc": "2.0", "id": "abc", "result": {}}
    assert out["zero"]["json"] == {"jsonrpc": "2.0", "id": 0, "result": {}}
    assert out["scalar"]["json"][0]["error"]["code"] == -32600 and out["scalar"]["json"][0]["id"] is None


def _is_invalid_request(out: dict) -> bool:
    j = out["json"]
    return isinstance(j, dict) and j.get("error", {}).get("code") == -32600 and j.get("id", "absent") is None


def test_empty_batch_is_invalid_request():
    out = _post([])
    assert _is_invalid_request(out), f"status={out['status']} body={out['text']!r}"


@pytest.mark.parametrize("body", [{}, {"jsonrpc": "2.0", "method": 1, "params": "bar"}, {"jsonrpc": "2.0"}], ids=["empty-object", "spec-example-method-1", "no-method"])
def test_invalid_object_without_id_is_answered_with_id_null(body):
    out = _post(body)
    assert _is_invalid_request(out), f"status={out['status']} body={out['text']!r}"


@pytest.mark.parametrize("body", [{"id": 1, "method": "ping"}, {"jsonrpc": "1.0", "id": 1, "method": "ping"}], ids=["jsonrpc-missing", "jsonrpc-1.0"])
def test_wrong_jsonrpc_member_is_invalid_request(body):
    out = _post(body)
    assert out["json"].get("error", {}).get("code") == -32600, f"served: {out['text']!r}"


def test_object_id_is_invalid_request():
    out = _post({"jsonrpc": "2.0", "id": {"a": 1}, "method": "ping"})
    assert out["json"].get("error", {}).get("code") == -32600, f"served: {out['text']!r}"


def test_non_string_method_is_invalid_request():
    out = _post({"jsonrpc": "2.0", "id": 1, "method": 5})
    assert out["json"]["error"]["code"] == -32600, f"got: {out['text']!r}"
