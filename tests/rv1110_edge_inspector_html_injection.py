"""severity: medium
finding: the inspector UI resource writes tool-result text into the page with innerHTML and no escaping
location: edge/telarch_edge_mcp.js, constant INSPECTOR_HTML (the template string served for
  ui://telarch/inspector-v1.html). Line numbers below are inside that extracted HTML, not the JS file:
  line 377 (harpe item id/content), 389 (kibisis category/key/epistemic_state/content/status),
  410 (argus event_type/actor/payload); data arrives through applyServerPayload (329-360) from
  window.openai.toolOutput (460-461), window.openai.callTool results (298-299) and any "message"
  event with method ui/notifications/tool-result (264-275, no check of ev.source or ev.origin).
effect: record content, item ids, actors and event types are caller- or model-supplied strings that the
  tools echo back unchanged in structuredContent. A stored record whose content is
  `<img src=x onerror=...>` becomes live markup in the widget, which runs with the declared widget
  domain https://telarch.ai and can post tools/call messages to the host. Whether the host's own CSP
  stops inline handlers is outside this repository and was not tested (no browser, no network); the
  markup injection itself is shown here with a DOM stub.
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


MARK = "<img src=x onerror=window.__rv1110=1>"

DOM_STUB = r"""
const made = [];
const mkEl = (id) => { const el = {id, textContent: '', innerHTML: '', className: '', value: '4096', style: {}, dataset: {}, children: [],
  classList: {add() {}, remove() {}}, addEventListener() {}, appendChild(c) { this.children.push(c); }}; made.push(el); return el; };
const byId = new Map();
const document = {querySelectorAll: () => [], createElement: (t) => mkEl('<' + t + '>'),
  getElementById: (id) => { if (!byId.has(id)) byId.set(id, mkEl(id)); return byId.get(id); }};
const handlers = {};
const window = {addEventListener: (t, fn) => { handlers[t] = fn; }, parent: {postMessage() {}}, openai: {toolOutput: TOOL_OUTPUT}};
const fakeTimeout = () => 0;
const html = new Function(code + '\nreturn INSPECTOR_HTML;')();
const m = html.match(/<script[^>]*>([\s\S]*?)<\/script>/);
new Function('window', 'document', 'setTimeout', 'fetch', m[1])(window, document, fakeTimeout, async () => { throw new Error('no network'); });
return {rendered: made.map(e => e.innerHTML).filter(Boolean), texts: made.map(e => String(e.textContent)).filter(Boolean)};
"""


def _render(tool: str, args: dict) -> dict:
    script = (
        f"const TOOL_OUTPUT = (await call({json.dumps(tool)}, {json.dumps(args)})).result.structuredContent;\n" + DOM_STUB
    )
    return _node(script)


def test_control_plain_record_text_is_rendered_by_the_ui_script():
    out = _render("kibisis_resolve_memory", {"query": "", "records": [{"key": "k1", "category": "decision", "content": "plain rv1110 fact", "epistemic_state": "verified"}]})
    assert any("plain rv1110 fact" in h for h in out["rendered"])
    assert any("<kibisis-recall" in t for t in out["texts"])  # the envelope goes through textContent


def test_record_content_is_not_inserted_as_markup():
    out = _render("kibisis_resolve_memory", {"query": "", "records": [{"key": "k1", "category": "decision", "content": MARK, "epistemic_state": "verified"}]})
    assert not any(MARK in h for h in out["rendered"]), "record content reached innerHTML unescaped"


def test_harpe_item_content_is_not_inserted_as_markup():
    out = _render("harpe_synthesize_context", {"total_budget": 8000, "items": [{"id": "a", "content": MARK, "priority": 5}]})
    assert not any(MARK in h for h in out["rendered"]), "context item content reached innerHTML unescaped"


def test_argus_actor_is_not_inserted_as_markup():
    out = _render("argus_audit_seal", {"events": [{"event_type": "t", "actor": MARK, "payload": {}}]})
    assert not any(MARK in h for h in out["rendered"]), "audit event actor reached innerHTML unescaped"
