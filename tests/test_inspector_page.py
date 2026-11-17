"""The inspector page (ui://telarch/inspector-v1.html): what its buttons call and what it claims.

Found in the ChatGPT desktop app on 2026-11-16 (issues 8 and 9). Until 0.2.3 "Verify Chain via MCP" called
argus_audit_seal with a chain written into the page and showed the answer as a verified chain, so the button
reported "verified" without the verifier being asked. The page script runs here in node against a small DOM
stand-in, with the host's callTool wired to the server's own handler.
"""
from __future__ import annotations

import json
import re

from telarch_testlib import edge_call, node

HARNESS = r"""
(async () => {
  const calls = [];
  const els = new Map();
  const mkEl = (id) => {
    let markup = '';
    return {id, textContent: '', className: '', value: '', style: {}, dataset: {}, children: [], listeners: {},
      get innerHTML() { return markup; },
      set innerHTML(v) { markup = String(v); this.children = []; },  // as in a browser: new markup replaces the children
      classList: {add() {}, remove() {}}, addEventListener(t, fn) { this.listeners[t] = fn; }, appendChild(c) { this.children.push(c); }};
  };
  const document = {querySelectorAll: () => [], createElement: (t) => mkEl('<' + t + '>'),
    getElementById: (id) => { if (!els.has(id)) els.set(id, mkEl(id)); return els.get(id); }};
  const openai = {callTool: async (name, args) => {
    calls.push({name, args: JSON.parse(JSON.stringify(args))});
    const answer = await edge.rpc({jsonrpc: '2.0', id: 1, method: 'tools/call', params: {name, arguments: args}});
    return answer.error ? {isError: true, content: [{type: 'text', text: answer.error.message}]} : answer.result;
  }};
  if (input.toolOutput !== undefined) openai.toolOutput = input.toolOutput;
  const window = {addEventListener() {}, parent: {postMessage() {}}, openai};
  const script = edge.html.match(/<script[^>]*>([\s\S]*?)<\/script>/)[1];
  new Function('window', 'document', 'setTimeout', 'fetch', 'navigator', script)(window, document, () => 0, async () => { throw new Error('no network'); }, {});
  const snap = () => ({
    banner: document.getElementById('argus-banner').textContent,
    banner_class: document.getElementById('argus-banner').className,
    head: document.getElementById('argus-head').textContent,
    events: document.getElementById('argus-events').children.map(c => c.innerHTML),
    harpe: document.getElementById('harpe-items').children.map(c => c.innerHTML),
    harpe_summary: document.getElementById('harpe-summary').textContent,
    budget: String(document.getElementById('budget-val').textContent),
    kibisis_meta: document.getElementById('kibisis-meta').textContent,
    status: document.getElementById('status-badge').textContent,
    sources: ['harpe', 'kibisis', 'argus'].map(tab => document.getElementById(tab + '-source').textContent),
    slider: (({min, max, value}) => ({min, max, value}))(document.getElementById('budget-slider')),
    kibisis: document.getElementById('kibisis-items').children.map(c => c.innerHTML),
  });
  const out = [{step: 'open', calls: 0, ...snap()}];
  for (const step of input.steps) {
    const before = calls.length;
    if (step.slider !== undefined) document.getElementById('budget-slider').value = String(step.slider);
    await document.getElementById(step.click).listeners.click({});
    out.push({step: step.click, calls: calls.slice(before), ...snap()});
  }
  done(out);
})();
"""


def run(steps, tool_output=None):
    payload = {"steps": [s if isinstance(s, dict) else {"click": s} for s in steps]}
    if tool_output is not None:
        payload["toolOutput"] = tool_output
    return node(HARNESS, payload)


def opened(arguments=None):
    return edge_call("telarch_open_inspector", arguments or {})["result"]["structuredContent"]


def page() -> str:
    return node("done(edge.html);")


def test_every_element_the_script_looks_up_is_in_the_markup():
    # a wrong id passes in node, where the stand-in makes any element asked for, and throws at load in a browser
    html = page()
    script = re.search(r"<script[^>]*>([\s\S]*?)</script>", html).group(1)
    markup = html[: html.index("<script")]
    asked = set(re.findall(r'getElementById\("([^"]+)"\)', script))
    assert asked and not [name for name in sorted(asked) if f'id="{name}"' not in markup]
    for tab in ("harpe", "kibisis", "argus"):  # looked up with a computed id in this test's harness only
        assert f'id="{tab}-source"' in markup


def test_the_page_opens_with_a_sealed_chain_and_does_not_call_it_verified():
    first = run([])[0]
    assert first["banner"].startswith("SEALED, NOT YET VERIFIED: 3 events")
    assert "VERIFIED" not in "".join(first["events"]) and "ok" not in first["banner_class"]
    assert all(">SEALED<" in row for row in first["events"])


def test_verify_button_calls_the_verifier_with_the_chain_the_server_sealed():
    sealed = opened({"total_budget": 3640})
    after = run(["btn-verify"], sealed)[1]
    assert [c["name"] for c in after["calls"]] == ["argus_audit_verify"]
    assert after["calls"][0]["args"] == {"events": sealed["argus"]["events"]}
    assert after["banner"] == "CHAIN VALID: 3/3 events verified from GENESIS by argus_audit_verify"
    assert "ok" in after["banner_class"] and all(">VERIFIED<" in row for row in after["events"])
    assert after["head"] == sealed["argus"]["head_hash"]


def test_tamper_button_changes_one_payload_and_the_verifier_reports_where():
    sealed = opened()
    after = run(["btn-tamper"], sealed)[1]
    assert [c["name"] for c in after["calls"]] == ["argus_audit_verify"]
    sent = after["calls"][0]["args"]["events"]
    assert sent[1]["payload"]["savings_bp"] == 9999 and sent[1]["event_hash"] == sealed["argus"]["events"][1]["event_hash"]
    assert sent[0] == sealed["argus"]["events"][0] and sent[2] == sealed["argus"]["events"][2]
    assert after["banner"].startswith("CHAIN BROKEN AT SEQ #2: ") and "err" in after["banner_class"]
    marks = [re.search(r'<span class="badge [a-z]*">([A-Z ]+)</span>$', row).group(1) for row in after["events"]]
    assert marks == ["VERIFIED", "BROKEN HERE", "NOT CHECKED"]


def test_verify_after_a_tamper_checks_the_sealed_chain_again():
    sealed = opened()
    steps = run(["btn-tamper", "btn-verify"], sealed)
    assert steps[2]["calls"][0]["args"] == {"events": sealed["argus"]["events"]}
    assert steps[2]["banner"].startswith("CHAIN VALID: 3/3 events verified")


def test_no_button_seals_a_chain_written_into_the_page():
    html = page()
    script = re.search(r"<script[^>]*>([\s\S]*?)</script>", html).group(1)
    handlers = script[script.index('document.getElementById("btn-tamper")'):]
    assert "argus_audit_seal" not in handlers
    assert script.count("2026-11-04T00:00:02Z") == 1  # once, in the default state the server produced


def test_repack_sends_the_shown_items_and_seals_the_chain_again_with_the_new_numbers():
    sealed = opened()
    after = run([{"click": "btn-repack", "slider": 3700}], sealed)[1]
    assert [c["name"] for c in after["calls"]] == ["harpe_synthesize_context", "argus_audit_seal"]
    packed_args = after["calls"][0]["args"]
    assert packed_args["total_budget"] == 3700 and [i["id"] for i in packed_args["items"]] == [i["id"] for i in sealed["harpe"]["items"]]
    want = opened({"total_budget": 3700})
    assert after["calls"][1]["args"]["events"][1]["payload"] == want["argus"]["events"][1]["payload"]
    assert after["head"] == want["argus"]["head_hash"] and after["banner"].startswith("SEALED, NOT YET VERIFIED")
    assert after["budget"] == "3700"
    assert [re.search(r"<strong>(.*?)</strong>", r).group(1) for r in after["harpe"]] == [i["id"] for i in want["harpe"]["items"]]
    assert [re.search(r'">([A-Z ()]+)</span>$', r).group(1) for r in after["harpe"]] == [i["status"] for i in want["harpe"]["items"]]


def test_a_refused_call_leaves_the_page_as_it_was():
    sealed = opened()
    steps = run([{"click": "btn-repack", "slider": "not a number"}], sealed)  # total_budget is not a whole number: refused
    assert steps[1]["status"] == "Call refused" and [c["name"] for c in steps[1]["calls"]] == ["harpe_synthesize_context"]
    assert steps[1]["harpe"] == steps[0]["harpe"] and steps[1]["head"] == steps[0]["head"]


def test_the_default_state_is_what_the_server_returns_for_default_arguments():
    script = re.search(r"<script[^>]*>([\s\S]*?)</script>", page()).group(1)
    start = script.index("let state = ") + len("let state = ")
    state, _ = json.JSONDecoder().raw_decode(script[start:])
    want = opened()
    assert state == {k: want[k] for k in ("harpe", "kibisis", "argus")}
    assert run([])[0]["head"] == want["argus"]["head_hash"]


def test_each_harpe_row_says_why_it_was_kept_or_pruned_and_rows_keep_the_item_order():
    sealed = opened({"total_budget": 3640})
    first = run([], sealed)[0]
    rows = dict(zip([i["id"] for i in sealed["harpe"]["items"]], first["harpe"]))
    assert list(rows) == ["sys_invariants", "arch_decision", "stale_scratch"]
    assert "always kept: pinned or priority 0" in rows["sys_invariants"]
    assert "kept: chosen for the 37 tok left after the always-kept items" in rows["arch_decision"]
    assert "pruned: its 46 tok do not fit in the 37 tok left after the always-kept items" in rows["stale_scratch"]
    assert "a lower number is more important" in page()


def test_wording_version_and_wrapping():
    html = page()
    info = node("(async () => done((await edge.rpc({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-06-18',capabilities:{},clientInfo:{name:'t',version:'1'}}})).result.serverInfo))();")
    assert f'<span class="badge">v{info["version"]}</span>' in html
    assert f'appInfo: {{ name: "Telarch Inspector", version: "{info["version"]}" }}' in html
    assert "{{" not in html and "0.1.0" not in html
    assert "0/1" not in html and html.count("Exact Knapsack") == 2
    assert "<title>Telarch Inspector</title>" in html
    assert "break-all" not in html and "overflow-wrap: anywhere" in html and "white-space: nowrap" in html
    assert "Cryptographically Verified" not in html


def test_full_hashes_are_shown():
    sealed = opened()
    first = run([], sealed)[0]
    for row, event in zip(first["events"], sealed["argus"]["events"]):
        assert f'<span class="hash">{event["event_hash"]}</span>' in row and f'<span class="hash">{event["prev_hash"]}</span>' in row
    assert len(first["head"]) == 64


def test_no_served_text_says_0_1_knapsack():
    tools = node("done(edge.tools);")
    assert "0/1" not in json.dumps(tools)
    for method, params in (("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}), ("resources/list", {}), ("prompts/list", {})):
        answer = node("(async () => done(await edge.rpc(input)))();", {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        assert "0/1" not in json.dumps(answer), method


def test_the_kibisis_line_counts_the_records_shown():
    sealed = opened()
    assert run([], sealed)[0]["kibisis_meta"].startswith('Scope: default | Query: "SQLCipher encryption" | 1 active, 1 superseded, 1 revoked.')


def test_without_a_host_or_a_network_the_verify_button_claims_nothing():
    out = node(HARNESS.replace("const window = {addEventListener() {}, parent: {postMessage() {}}, openai};",
                               "const window = {addEventListener() {}, parent: {postMessage() {}}};")
               .replace("() => 0, async () => { throw", "(fn) => { fn(); return 0; }, async () => { throw"), {"steps": [{"click": "btn-verify"}]})
    assert out[1]["status"] == "MCP not reachable" and out[1]["banner"].startswith("SEALED, NOT YET VERIFIED")
