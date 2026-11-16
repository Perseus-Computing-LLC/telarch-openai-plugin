"""What argus_audit_seal returns must be accepted by argus_audit_verify, as returned.

Found in a ChatGPT session on 2026-11-16 against the directory listing of plugin 0.1.0. The client checks a tool
call against the tool descriptions it was given. Those were the 0.1.0 descriptions, where a sealed event's
``timestamp`` had to be a string, while the server sealed an undated event with ``timestamp: null``. The sealed
events could not be passed on to the verifier: with the null the client refused the call, and without the field
the server reports a malformed event.

Two things have to hold for the round trip, and both are checked here for events sealed without a timestamp,
with ``null`` and with a string:
  1. the server verifies its own sealed events;
  2. the ``inputSchema`` that tools/list publishes for argus_audit_verify allows those events, because a client
     may check the call against it before sending.
"""
from __future__ import annotations

import copy

import jsonschema
import pytest

from telarch_testlib import edge_rpc_many

EVENTS = [
    {"event_type": "tool_call", "actor": "agent-1", "payload": {}},
    {"event_type": "tool_result", "actor": "agent-1", "payload": {"status": "ok"}},
    {"event_type": "review", "actor": "thomas", "payload": {}},
]
STAMPS = ["2026-11-16T00:00:01Z", "2026-11-16T00:00:02Z", "2026-11-16T00:00:03Z"]


def _events(case: str) -> list:
    events = copy.deepcopy(EVENTS)
    for i, event in enumerate(events):
        if case == "null" or (case == "mixed" and i == 1):
            event["timestamp"] = None
        elif case == "string" or (case == "mixed" and i == 0):
            event["timestamp"] = STAMPS[i]
    return events  # case "omitted": no event has the field; "mixed": a string, a null and an omitted one


def _call(name: str, arguments: dict) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


def _seal(arguments: dict) -> dict:
    result = edge_rpc_many([_call("argus_audit_seal", arguments)])[0]["result"]
    assert not result.get("isError"), result
    return result["structuredContent"]


def _published_schema(tool: str) -> dict:
    listed = edge_rpc_many([{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}])[0]["result"]["tools"]
    return next(t for t in listed if t["name"] == tool)["inputSchema"]


CASES = ["omitted", "null", "string", "mixed"]


@pytest.mark.parametrize("case", CASES)
def test_the_server_verifies_the_events_it_sealed(case):
    sent = _events(case)
    sealed = _seal({"events": sent})
    # no time is invented: an undated event is returned with timestamp null, a dated one keeps its timestamp
    assert [e["timestamp"] for e in sealed["events"]] == [e.get("timestamp") for e in sent]
    answer = edge_rpc_many([_call("argus_audit_verify", {"events": sealed["events"]})])[0]
    assert "error" not in answer, answer
    verdict = answer["result"]["structuredContent"]
    assert verdict["valid"] is True, verdict["error_detail"]
    assert (verdict["total_events"], verdict["head_hash"], verdict["starts_at_genesis"]) == (3, sealed["head_hash"], True)


@pytest.mark.parametrize("case", CASES)
def test_the_published_verify_schema_allows_the_sealed_events(case):
    sealed = _seal({"events": _events(case)})
    errors = [e.message for e in jsonschema.Draft202012Validator(_published_schema("argus_audit_verify")).iter_errors({"events": sealed["events"]})]
    assert errors == [], f"a client that checks the call against tools/list refuses the server's own sealed events: {errors}"


@pytest.mark.parametrize("case", CASES)
def test_the_published_seal_schema_allows_each_way_of_giving_a_timestamp(case):
    errors = [e.message for e in jsonschema.Draft202012Validator(_published_schema("argus_audit_seal")).iter_errors({"events": _events(case)})]
    assert errors == [], errors


def test_a_continued_segment_sealed_without_timestamps_verifies_from_its_anchor():
    first = _seal({"events": _events("omitted")[:2]})
    second = _seal({"prev_hash": first["head_hash"], "events": [dict(_events("omitted")[2], sequence=3)]})
    answers = edge_rpc_many([
        _call("argus_audit_verify", {"prev_hash": first["head_hash"], "events": second["events"]}),
        _call("argus_audit_verify", {"events": first["events"] + second["events"]}),
    ])
    assert [a["result"]["structuredContent"]["valid"] for a in answers] == [True, True]


def test_an_undated_event_stays_undated_removing_or_filling_the_timestamp_breaks_the_chain():
    sealed = _seal({"events": _events("omitted")})["events"]
    removed = copy.deepcopy(sealed)
    del removed[1]["timestamp"]
    filled = copy.deepcopy(sealed)
    filled[1]["timestamp"] = STAMPS[1]
    verdicts = [a["result"]["structuredContent"] for a in edge_rpc_many([
        _call("argus_audit_verify", {"events": removed}), _call("argus_audit_verify", {"events": filled})])]
    assert [(v["valid"], v["first_broken_sequence"]) for v in verdicts] == [(False, 2), (False, 2)]


def test_the_chain_of_the_chatgpt_session_has_the_hashes_that_session_reported():
    """Known answer: the three events of the 2026-11-16 session with its timestamps, sealed by the server then."""
    sealed = _seal({"events": _events("string")})
    assert sealed["root_hash"] == "97f4c5c2499fefbceb68043cc0527be4f927569bf4a23678def89b7a8668fd44"
    assert sealed["head_hash"] == "6d450776cd008da4873bdf9326b15725fb995587d5fd68e1fa0bc4bd70d31eb6"
    tampered = copy.deepcopy(sealed["events"])
    tampered[1]["payload"]["status"] = "failed"
    # canonical_payload is optional for the verifier; without it the changed payload shows as a digest mismatch
    without_canonical = [{k: v for k, v in e.items() if k != "canonical_payload"} for e in tampered]
    verdicts = [a["result"]["structuredContent"] for a in edge_rpc_many([
        _call("argus_audit_verify", {"events": tampered}), _call("argus_audit_verify", {"events": without_canonical})])]
    assert [(v["valid"], v["first_broken_sequence"]) for v in verdicts] == [(False, 2), (False, 2)]
    assert "canonical_payload at sequence 2 is not the canonical form of payload" in verdicts[0]["error_detail"]
    assert "SHA-256 digest mismatch at sequence 2" in verdicts[1]["error_detail"]
