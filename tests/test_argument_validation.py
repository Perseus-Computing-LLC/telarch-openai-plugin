"""Both servers check tools/call arguments against the tool's own inputSchema before the handler runs
(review 2026-11-10: E10, L02, L06, C02 and the "raw exception text" and "lease expiry" notes).

A call that does not match is refused with JSON-RPC -32602 (MCP 2025-06-18, Tools, Error Handling: protocol
errors cover unknown tools and invalid arguments). The interpreter's exception text is never the answer.
"""
from __future__ import annotations

import copy

import pytest

from telarch_testlib import edge_rpc_many, isolate_environment, load_local_module, local_call, node, rejected

RUNTIME_TEXT = ("Cannot read properties", "is not a function", "is not iterable", "Maximum call stack", "Traceback",
                "KeyError", "TypeError", "AttributeError", "NoneType", "object has no attribute", "validation error for")

# A valid call for every tool of each server: the base that one violation at a time is applied to.
EDGE_VALID = {
    "harpe_synthesize_context": {"total_budget": 5000, "items": [{"id": "a", "content": "text", "priority": 5, "pinned": False, "role": "user"}]},
    "harpe_budget_evaluate": {"total_budget": 5000, "current_usage": 10},
    "kibisis_resolve_memory": {"query": "engine", "records": [{"key": "k", "content": "engine choice", "epistemic_state": "verified"}],
                               "write_attempt": {"origin": "user", "epistemic_state": "verified"}},
    "kibisis_lease_evaluate": {"holder_id": "w1", "fencing_token": 2, "highest_token_seen": 2, "lease_expires_epoch": 200, "now_epoch": 100},
    "argus_audit_seal": {"events": [{"event_type": "t", "actor": "a", "payload": {"n": 1}}]},
    "argus_audit_verify": None,  # filled by _edge_valid() with a chain the server sealed itself
    "telarch_open_inspector": {},
}
LOCAL_VALID = {
    "kibisis_remember": {"category": "decision", "key": "k", "content": "text"},
    "kibisis_recall": {"query": "text"},
    "kibisis_health": {},
    "harpe_budget_evaluate": {"total_budget": 5000},
    "harpe_synthesize_context": {"total_budget": 5000, "items": [{"id": "a", "content": "text"}]},
    "argus_audit_append": {"event_type": "t", "actor": "a", "payload": {"n": 1}},
    "argus_audit_verify": {},
    "argus_audit_tail": {"limit": 3},
}


def _edge_valid() -> dict:
    if EDGE_VALID["argus_audit_verify"] is None:
        sealed = edge_rpc_many([_request("argus_audit_seal", EDGE_VALID["argus_audit_seal"])])[0]["result"]["structuredContent"]
        EDGE_VALID["argus_audit_verify"] = {"events": sealed["events"]}
    return EDGE_VALID


def _request(name, arguments):
    return {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


def _wrong_value(schema: dict):
    """A value of a type the schema does not admit."""
    declared = schema.get("type")
    types = declared if isinstance(declared, list) else [declared]
    for candidate in ("text", 3, True, [], {}):
        kind = {str: "string", int: "integer", bool: "boolean", list: "array", dict: "object"}[type(candidate)]
        if kind not in types and not (kind == "integer" and "number" in types):
            return candidate
    return None


def _violations(schema: dict, valid: dict) -> list:
    """(label, arguments) pairs, each breaking the schema in exactly one place at the top level."""
    out = [("arguments is a list", []), ("arguments is a string", "x"), ("arguments is null", None)]
    properties = schema.get("properties", {})
    for name in schema.get("required", []):
        args = copy.deepcopy(valid)
        args.pop(name, None)
        out.append((f"missing {name}", args))
    if schema.get("additionalProperties") is False:
        out.append(("undeclared property", dict(copy.deepcopy(valid), not_in_the_schema=1)))
    for name, sub in properties.items():
        if "type" in sub and _wrong_value(sub) is not None:
            out.append((f"{name} of the wrong type", dict(copy.deepcopy(valid), **{name: _wrong_value(sub)})))
        if "enum" in sub:
            out.append((f"{name} outside its enum", dict(copy.deepcopy(valid), **{name: "no-such-choice"})))
        if "minimum" in sub:
            out.append((f"{name} below its minimum", dict(copy.deepcopy(valid), **{name: sub["minimum"] - 1})))
        if "maximum" in sub:
            out.append((f"{name} above its maximum", dict(copy.deepcopy(valid), **{name: sub["maximum"] + 1})))
        if sub.get("type") == "integer":
            out.append((f"{name} with a fraction", dict(copy.deepcopy(valid), **{name: 1.5})))
    return out


def _assert_invalid_params(answer: dict, tool: str, label: str):
    assert answer is not None and "error" in answer, f"{tool}: {label}: answered instead of refusing: {str(answer)[:300]}"
    assert answer["error"]["code"] == -32602, f"{tool}: {label}: {answer['error']}"
    assert answer["id"] == 7
    message = answer["error"]["message"]
    assert tool in message, message
    assert not any(marker in message for marker in RUNTIME_TEXT), message


def test_valid_base_calls_cover_every_hosted_tool_and_are_accepted():
    tools = node("done(edge.tools.map(t => t.name));")
    valid = _edge_valid()
    assert sorted(tools) == sorted(valid)
    for name, answer in zip(tools, edge_rpc_many([_request(n, valid[n]) for n in tools])):
        assert not rejected(answer), (name, answer)
    verified = edge_rpc_many([_request("argus_audit_verify", valid["argus_audit_verify"])])[0]["result"]["structuredContent"]
    assert verified["valid"] is True


def test_hosted_server_refuses_every_schema_violation_with_invalid_params():
    schemas = {t["name"]: t["inputSchema"] for t in node("done(edge.tools.map(t => ({name: t.name, inputSchema: t.inputSchema})));")}
    cases = [(name, label, args) for name in schemas for label, args in _violations(schemas[name], _edge_valid()[name])]
    assert len(cases) > 80
    answers = edge_rpc_many([_request(name, args) for name, _, args in cases])
    for (name, label, _), answer in zip(cases, answers):
        _assert_invalid_params(answer, name, label)


@pytest.fixture
def local(tmp_path, monkeypatch):
    isolate_environment(tmp_path, monkeypatch)
    return load_local_module().TelarchMCPServer()


def test_valid_base_calls_cover_local_tools_and_are_accepted(local):
    listed = {t["name"] for t in local.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}
    assert set(LOCAL_VALID) <= listed
    for name, args in LOCAL_VALID.items():
        assert not rejected(local_call(local, name, args)), name


def test_local_server_refuses_every_schema_violation_of_every_listed_tool(local):
    tools = local.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
    checked = 0
    for tool in tools:
        name, schema = tool["name"], tool["inputSchema"]
        # tools without a base call here are probed from an empty call; violations that need a valid base are skipped
        valid = LOCAL_VALID.get(name)
        for label, args in _violations(schema, valid if valid is not None else {}):
            if valid is None and not label.startswith(("arguments is", "missing", "undeclared")):
                continue
            _assert_invalid_params(local.handle_request(_request(name, args)), name, label)
            checked += 1
    assert checked > 80


def test_local_server_does_not_run_a_refused_write(local):
    before = local_call(local, "argus_audit_verify", {})["result"]["structuredContent"]["total_events"]
    for args in ({"event_type": "t", "actor": "a"}, {"event_type": "t", "actor": "a", "payload": {}, "extra": 1}, {"event_type": 5, "actor": "a", "payload": {}}):
        assert "error" in local_call(local, "argus_audit_append", args)
    assert "error" in local_call(local, "kibisis_remember", {"category": "decision", "key": "k"})
    assert local_call(local, "argus_audit_verify", {})["result"]["structuredContent"]["total_events"] == before


def test_local_argus_refusals_carry_the_library_sentence_not_a_traceback(local):
    answer = local_call(local, "argus_audit_append", {"event_type": "t", "actor": "a", "payload": {"ratio": 0.5}})
    assert answer["result"]["isError"] is True
    text = answer["result"]["content"][0]["text"]
    assert text.startswith("FloatPayloadError:") and "Traceback" not in text


def test_local_internal_error_does_not_return_exception_text(local, capsys):
    def boom(*args, **kwargs):
        raise RuntimeError("secret detail /home/someone/.config/private")

    local.harpe.synthesize = boom
    answer = local_call(local, "harpe_synthesize_context", LOCAL_VALID["harpe_synthesize_context"])
    assert answer == {"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": "Internal error while running tool harpe_synthesize_context"}}
    captured = capsys.readouterr()
    assert captured.out == "" and "secret detail" in captured.err  # the detail goes to the log, not to the caller


def test_hosted_internal_error_does_not_return_exception_text():
    # A handler that throws: arguments whose property read fails after validation has passed.
    out = node(
        """(async () => {
          let reads = 0;
          const args = new Proxy({total_budget: 5000}, {
            get(target, key) { if (key === 'total_budget' && ++reads > 1) throw new Error('secret detail from the runtime'); return target[key]; }
          });
          done(await edge.rpc({jsonrpc: '2.0', id: 1, method: 'tools/call', params: {name: 'harpe_budget_evaluate', arguments: args}}));
        })();"""
    )
    assert rejected(out)
    assert "secret detail" not in str(out) and "Internal error" in str(out)


def test_lease_expiry_must_be_a_whole_number():
    # Before the fix a non-numeric lease_expires_epoch compared false against the clock and the write was permitted.
    base = EDGE_VALID["kibisis_lease_evaluate"]
    bad = ["2026-01-01", "200", None, True, 1.5, [200], {"t": 200}]
    answers = edge_rpc_many([_request("kibisis_lease_evaluate", dict(base, lease_expires_epoch=v)) for v in bad])
    for value, answer in zip(bad, answers):
        _assert_invalid_params(answer, "kibisis_lease_evaluate", f"lease_expires_epoch={value!r}")
    answers = edge_rpc_many([_request("kibisis_lease_evaluate", dict(base, now_epoch=v)) for v in bad])
    for value, answer in zip(bad, answers):
        _assert_invalid_params(answer, "kibisis_lease_evaluate", f"now_epoch={value!r}")
    expired, no_clock, live = edge_rpc_many([
        _request("kibisis_lease_evaluate", dict(base, lease_expires_epoch=100, now_epoch=100)),
        _request("kibisis_lease_evaluate", {k: v for k, v in base.items() if k != "now_epoch"}),
        _request("kibisis_lease_evaluate", base),
    ])
    assert expired["result"]["isError"] is True and "LeaseExpiredError" in expired["result"]["content"][0]["text"]
    assert no_clock["result"]["isError"] is True and "now_epoch" in no_clock["result"]["content"][0]["text"]
    assert live["result"]["structuredContent"]["permitted"] is True


def test_whole_number_floats_are_integers_for_both_servers(local):
    # JSON has one number type: 5000.0 is the integer 5000 for a schema that says "integer"
    args = {"total_budget": 5000.0, "items": [{"id": "a", "content": "text", "priority": 5.0}]}
    edge = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]["result"]["structuredContent"]
    mine = local.handle_request(_request("harpe_synthesize_context", args))["result"]["structuredContent"]
    assert edge["included_ids"] == mine["included_ids"] == ["a"] and edge["total_budget"] == mine["total_budget"] == 5000
