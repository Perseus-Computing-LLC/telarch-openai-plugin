"""A refused call says which argument is at fault and carries a code that does not change (issue 12).

Before 0.3.0 a refusal was one sentence. A client that wanted to correct the call had to read the sentence,
and a client that wanted to tell two refusals apart had to match on its wording. Now:

- arguments that do not match the tool's inputSchema: JSON-RPC error -32602 as before, with
  ``error.data == {"code": "InvalidArguments", "path": ...}``;
- a rule of the tool refuses the call: a tool result with ``isError: true`` as before, with
  ``structuredContent.error == {"code", "path", "message"}``.

The sentences are unchanged. ``path`` is written from the tool's arguments ("items[1].id"), is "" for the
arguments object itself, and is null when no single argument is at fault.
"""
from __future__ import annotations

import re

import pytest

from telarch_testlib import EDGE_JS, edge_call, isolate_environment, load_local_module, local_call, node

HASH = "a" * 64

# tool, arguments, code, path. One case per code a call can reach.
REFUSED = [
    ("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {"n": 1.5}}]}, "FloatPayload", "events[0].payload.n"),
    ("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {"n": 9007199254740993}}]}, "UnsafeInteger", "events[0].payload.n"),
    ("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {}}], "prev_hash": "zz"}, "PrevHashFormat", "prev_hash"),
    ("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {}}], "prev_hash": HASH}, "SequenceRequired", "events[0].sequence"),
    ("argus_audit_seal", {"events": [{"event_type": "t", "actor": "a", "payload": {}, "sequence": 5}, {"event_type": "t", "actor": "a", "payload": {}, "sequence": 9}]},
     "SequenceOrder", "events[1].sequence"),
    ("harpe_synthesize_context", {"total_budget": 100, "items": [{"id": "a", "content": "x"}, {"id": "b", "content": "y"}, {"id": "a", "content": "z"}]},
     "DuplicateItemId", "items[2].id"),
    ("kibisis_resolve_memory", {"query": "", "requested_scope": "other"}, "ScopeIsolation", "requested_scope"),
    ("kibisis_resolve_memory", {"query": "", "records": [{"key": "k", "content": "a"}, {"key": "k", "content": "b"}]}, "DuplicateRecordKey", "records[1].key"),
    ("kibisis_resolve_memory", {"query": "", "records": [{"key": "a", "content": "a", "supersedes_key": "b"}, {"key": "b", "content": "b", "supersedes_key": "a"}]},
     "SupersessionLoop", "records[0].supersedes_key"),
    ("kibisis_resolve_memory", {"query": "", "write_attempt": {"origin": "model", "epistemic_state": "verified"}}, "EpistemicTrustViolation", "write_attempt.epistemic_state"),
    ("kibisis_lease_evaluate", {"holder_id": "w", "fencing_token": 1, "highest_token_seen": 2}, "StaleFencingToken", "fencing_token"),
    ("kibisis_lease_evaluate", {"holder_id": "w", "fencing_token": 2, "highest_token_seen": 2, "lease_expires_epoch": 100}, "LeaseClockMissing", "now_epoch"),
    ("kibisis_lease_evaluate", {"holder_id": "w", "fencing_token": 2, "highest_token_seen": 2, "lease_expires_epoch": 100, "now_epoch": 200}, "LeaseExpired", "lease_expires_epoch"),
]

# tool, arguments, path in error.data
MISMATCHED = [
    ("harpe_synthesize_context", {"total_budget": 100, "items": [{"id": "a", "content": "x", "role": "developer"}]}, "items[0].role"),
    ("harpe_synthesize_context", {"total_budget": 100}, "items"),
    ("harpe_synthesize_context", {"total_budget": 100, "items": [{"id": "a"}]}, "items[0].content"),
    ("harpe_synthesize_context", {"total_budget": 0, "items": []}, "total_budget"),
    ("harpe_synthesize_context", {"total_budget": 100, "items": [], "max_tokens": 5}, ""),
    ("harpe_synthesize_context", {"total_budget": 100, "items": [{"id": "a", "content": "x", "weight": 3}]}, "items[0]"),
    ("harpe_synthesize_context", [], ""),
    ("harpe_budget_evaluate", {"total_budget": 100, "current_usage": -1}, "current_usage"),
]


@pytest.fixture
def local(tmp_path, monkeypatch):
    isolate_environment(tmp_path, monkeypatch)
    return load_local_module().TelarchMCPServer()


@pytest.mark.parametrize("tool,args,code,path", REFUSED, ids=[c[2] for c in REFUSED])
def test_a_refusal_by_a_tool_carries_its_code_and_the_path_of_the_argument(tool, args, code, path):
    result = edge_call(tool, args)["result"]
    assert result["isError"] is True
    error = result["structuredContent"]["error"]
    assert error["code"] == code and error["path"] == path
    # the sentence is the one the text content carries, and it starts with the name the code is taken from
    assert error["message"] == result["content"][0]["text"]
    assert re.match(rf"{code}(Error)?\b", error["message"])
    assert set(result["structuredContent"]) == {"error"} and set(error) == {"code", "path", "message"}


def test_a_refusal_with_no_single_argument_at_fault_has_a_null_path():
    items = [{"id": "a", "content": "w " * 1_000_001}, {"id": "b", "content": "w " * 1_000_002}, {"id": "c", "content": "w " * 7}]
    args = {"total_budget": 2_000_000, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": items}
    error = edge_call("harpe_synthesize_context", args)["result"]["structuredContent"]["error"]
    assert error["code"] == "KnapsackTooLarge" and error["path"] is None


@pytest.mark.parametrize("tool,args,path", MISMATCHED, ids=[f"{c[0]}:{c[2] or 'arguments'}" for c in MISMATCHED])
def test_arguments_that_do_not_match_the_schema_name_the_path_in_error_data(tool, args, path):
    error = edge_call(tool, args)["error"]
    assert error["code"] == -32602
    assert error["data"] == {"code": "InvalidArguments", "path": path}
    # the sentence is unchanged from 0.2.3 and names the same place, spelled from the arguments object
    assert error["message"].startswith(f"Invalid arguments for tool {tool}: arguments" + ("." + path if path else " "))


def test_other_protocol_errors_carry_no_data():
    assert set(edge_call("no_such_tool", {})["error"]) == {"code", "message"}


def test_the_list_of_codes_is_exactly_what_the_server_can_raise():
    codes = node("done(new Function(code + '\\nreturn REFUSAL_CODES;')());")
    source = EDGE_JS.read_text(encoding="utf-8")
    raised = re.findall(r'new TelarchRefusal\(\s*"([A-Za-z]+)",', source)
    assert len(raised) == len(re.findall(r"new TelarchRefusal\(", source)), "a refusal is raised without a literal code"
    assert sorted(set(raised) | {"InvalidArguments"}) == sorted(codes) and len(codes) == len(set(codes))
    # every sentence starts with the name its code is taken from
    for name, lead in re.findall(r'new TelarchRefusal\(\s*"([A-Za-z]+)",[^\n]*?,\s*[`"]([A-Za-z]+)', source):
        assert lead in (name, name + "Error"), (name, lead)
    reached = {case[2] for case in REFUSED} | {"KnapsackTooLarge", "InvalidArguments"}
    # the rest sit behind the schema check or behind a size limit and are raised only if that check is changed
    assert set(codes) - reached == {"PayloadTooDeep", "UnsupportedPayload", "UnknownPolicy"}


def test_both_servers_give_the_same_code_and_path_for_the_tools_they_share(local):
    duplicate = {"total_budget": 100, "items": [{"id": "a", "content": "x"}, {"id": "a", "content": "y"}]}
    hosted = edge_call("harpe_synthesize_context", duplicate)["result"]
    here = local_call(local, "harpe_synthesize_context", duplicate)["result"]
    assert hosted["structuredContent"] == here["structuredContent"] == {
        "error": {"code": "DuplicateItemId", "path": "items[1].id", "message": 'DuplicateItemIdError: item id "a" occurs more than once; ids must be unique.'}
    }
    assert here["isError"] is True and here["content"][0]["text"] == here["structuredContent"]["error"]["message"]
    for tool, args, path in MISMATCHED:
        assert local_call(local, tool, args)["error"] == edge_call(tool, args)["error"], (tool, path)


def test_the_local_server_takes_the_code_of_a_ledger_refusal_from_the_library_error(local):
    result = local_call(local, "argus_audit_append", {"event_type": "t", "actor": "a", "payload": {"n": 1.5}})["result"]
    error = result["structuredContent"]["error"]
    # the same code as the hosted server gives a fraction; the library names no argument, so the path is null
    assert result["isError"] is True and error["code"] == "FloatPayload" and error["path"] is None
    assert error["message"].startswith("FloatPayloadError: ") and error["message"] == result["content"][0]["text"]


def test_the_initialize_instructions_say_where_the_code_is():
    info = node("(async () => done((await edge.rpc(input)).result))();", {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}})
    assert "structuredContent.error" in info["instructions"] and "error.data" in info["instructions"]
