"""telarch_open_inspector shows the caller's own items, records and sealed events (issue 10).

Until 0.3.0 the inspector took a budget and a query and always showed three built-in items, three built-in
records and a built-in chain, so it could not be used to look at anything from the conversation. Each tab now
takes the data of the tool it belongs to, runs it through that tool's own handler, and says whether it shows
that data or the demonstration data.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from telarch_testlib import edge_call, node
from test_inspector_page import opened, run

FIXTURES = Path(__file__).resolve().parent / "fixtures"

ITEMS = [
    {"id": "rules", "content": "Never write outside the workspace. " * 4, "pinned": True, "role": "system"},
    {"id": "ticket", "content": "The customer reports that export fails for files above two gigabytes. " * 3, "priority": 10, "role": "user"},
    {"id": "log", "content": "retry attempt failed with status 503 " * 40, "priority": 80, "role": "tool"},
    {"id": "note", "content": "Short note.", "priority": 0},
]
HARPE_ARGS = {"total_budget": 200, "reserved_completion": 20, "reserved_tools": 10, "safety_margin": 5, "items": ITEMS}
RECORDS = [
    {"key": "region", "category": "decision", "content": "Deploy to eu-west-1.", "epistemic_state": "verified"},
    {"key": "region_v2", "category": "decision", "content": "Deploy to eu-central-1.", "epistemic_state": "verified", "supersedes_key": "region"},
    {"key": "rumour", "category": "insight", "content": "The region may move again.", "epistemic_state": "revoked"},
]
EVENTS_IN = [
    {"event_type": "deploy.start", "actor": "ci", "payload": {"build": 41}, "timestamp": "2026-11-17T09:00:00Z"},
    {"event_type": "deploy.finish", "actor": "ci", "payload": {"build": 41, "ok": True}, "timestamp": "2026-11-17T09:04:00Z"},
]


def structured(tool, args):
    answer = edge_call(tool, args)
    assert "result" in answer and not answer["result"].get("isError"), answer
    return answer["result"]["structuredContent"]


@pytest.fixture(scope="module")
def chain():
    return structured("argus_audit_seal", {"events": EVENTS_IN})["events"]


def test_without_data_the_inspector_shows_what_0_2_3_showed_and_says_it_is_a_demonstration():
    now = opened()
    assert now.pop("data_source") == {"harpe": "demonstration", "kibisis": "demonstration", "argus": "demonstration"}
    assert now["harpe"].pop("reserves") == {"reserved_completion": 2048, "reserved_tools": 1024, "safety_margin": 512}
    assert now == json.loads((FIXTURES / "inspector_default_0_2_3.json").read_text(encoding="utf-8"))


def test_the_harpe_tab_packs_the_caller_s_items_as_harpe_synthesize_context_does():
    shown = opened(HARPE_ARGS)
    packed = structured("harpe_synthesize_context", HARPE_ARGS)
    assert shown["data_source"] == {"harpe": "request", "kibisis": "demonstration", "argus": "demonstration"}
    harpe = shown["harpe"]
    for name in ("total_budget", "effective_budget", "consumed_tokens", "pruned_tokens", "utilization_pct", "pinned_policy_digest"):
        assert harpe[name] == packed[name], name
    assert harpe["effective_budget"] == 165 and harpe["policy"] == packed["policy_applied"] == "knapsack_dp"
    assert harpe["reserves"] == {"reserved_completion": 20, "reserved_tools": 10, "safety_margin": 5}
    assert [i["id"] for i in harpe["items"]] == [i["id"] for i in ITEMS]  # the order they were given in
    kept = {i["id"] for i in harpe["items"] if i["status"].startswith("INCLUDED")}
    assert kept == {i["id"] for i in packed["included_items"]} and {"rules", "note"} <= kept and "log" not in kept
    status = {i["id"]: i["status"] for i in harpe["items"]}
    assert status["rules"] == "INCLUDED (PINNED)" and status["note"] == "INCLUDED (PRIORITY 0)" and status["log"] == "PRUNED"
    assert status["ticket"] == "INCLUDED (KNAPSACK)"
    # no demonstration item is mixed in
    assert "sys_invariants" not in json.dumps(harpe)


def test_another_policy_is_applied_and_named():
    shown = opened({**HARPE_ARGS, "policy": "fifo"})
    packed = structured("harpe_synthesize_context", {**HARPE_ARGS, "policy": "fifo"})
    assert shown["harpe"]["policy"] == "fifo"
    assert {i["id"] for i in shown["harpe"]["items"] if i["status"] != "PRUNED"} == {i["id"] for i in packed["included_items"]}
    assert {i["status"] for i in shown["harpe"]["items"]} <= {"INCLUDED (PINNED)", "INCLUDED (PRIORITY 0)", "INCLUDED (FIFO)", "PRUNED"}


def test_the_kibisis_tab_resolves_the_caller_s_records_as_kibisis_resolve_memory_does():
    shown = opened({"records": RECORDS})
    resolved = structured("kibisis_resolve_memory", {"query": "", "records": RECORDS})
    assert shown["data_source"] == {"harpe": "demonstration", "kibisis": "request", "argus": "demonstration"}
    assert shown["kibisis"] == {"active_scope": "default", "query": "", "records": resolved["all_records_trace"], "envelope": resolved["envelope"]}
    assert {r["key"]: r["status"] for r in shown["kibisis"]["records"]}["region"] == "SUPERSEDED"
    assert "eu-central-1" in shown["kibisis"]["envelope"] and "eu-west-1" not in shown["kibisis"]["envelope"]
    narrowed = opened({"records": RECORDS, "query": "eu-central", "active_scope": "team-a"})["kibisis"]
    assert narrowed["query"] == "eu-central" and narrowed["active_scope"] == "team-a"


def test_the_argus_tab_shows_the_caller_s_chain_checked_not_sealed_again(chain):
    shown = opened({"events": chain})
    assert shown["data_source"]["argus"] == "request"
    assert shown["argus"] == structured("argus_audit_verify", {"events": chain})
    assert shown["argus"]["valid"] is True and shown["argus"]["events"] == chain
    # the harpe.context.pack event of the demonstration chain is not appended to it
    assert [e["event_type"] for e in shown["argus"]["events"]] == ["deploy.start", "deploy.finish"]


def test_a_chain_that_was_changed_is_shown_as_broken(chain):
    changed = json.loads(json.dumps(chain))
    changed[1]["payload"]["build"] = 42
    argus = opened({"events": changed})["argus"]
    assert argus["valid"] is False and argus["first_broken_sequence"] == 2 and argus["first_broken_index"] == 1
    assert "sequence 2" in argus["error_detail"]
    # an event that lacks its hash is not a schema matter: the verifier reports it, as argus_audit_verify does
    bare = [{"event_type": "t", "actor": "a", "payload": {}, "sequence": 1}]
    assert opened({"events": bare})["argus"] == structured("argus_audit_verify", {"events": bare})
    assert opened({"events": bare})["argus"]["valid"] is False


def test_all_three_tabs_can_take_data_in_one_call(chain):
    shown = opened({**HARPE_ARGS, "records": RECORDS, "events": chain})
    assert shown["data_source"] == {"harpe": "request", "kibisis": "request", "argus": "request"}
    assert "sys_invariants" not in json.dumps(shown) and "SQLCipher" not in json.dumps(shown)


REFUSED = {
    "duplicate item id": ({"items": [{"id": "a", "content": "x"}, {"id": "a", "content": "y"}]}, "DuplicateItemId", "items[1].id"),
    "duplicate record key": ({"records": [{"key": "k", "content": "a"}, {"key": "k", "content": "b"}]}, "DuplicateRecordKey", "records[1].key"),
}
MISMATCHED = {
    "role outside the enum": ({"items": [{"id": "a", "content": "x", "role": "developer"}]}, "items[0].role"),
    "record without content": ({"records": [{"key": "k"}]}, "records[0].content"),
    "events as an object": ({"events": {"sequence": 1}}, "events"),
    "undeclared argument": ({"chain": []}, ""),
    "items as text": ({"items": "a, b"}, "items"),
}


@pytest.mark.parametrize("label", sorted(REFUSED))
def test_the_rules_of_the_three_tools_apply_to_inspector_data(label):
    args, code, path = REFUSED[label]
    result = edge_call("telarch_open_inspector", args)["result"]
    assert result["isError"] is True and result["structuredContent"]["error"]["code"] == code
    assert result["structuredContent"]["error"]["path"] == path


@pytest.mark.parametrize("label", sorted(MISMATCHED))
def test_inspector_data_is_checked_against_the_schemas_of_the_three_tools(label):
    args, path = MISMATCHED[label]
    error = edge_call("telarch_open_inspector", args)["error"]
    assert error["code"] == -32602 and error["data"]["path"].startswith(path) and (path or error["data"]["path"] == "")


def test_the_inspector_shares_the_schemas_of_the_three_tools():
    tools = {t["name"]: t["inputSchema"]["properties"] for t in node("done(edge.tools);")}
    inspector = tools["telarch_open_inspector"]
    for name, owner in (("items", "harpe_synthesize_context"), ("records", "kibisis_resolve_memory"), ("events", "argus_audit_verify")):
        mine, theirs = dict(inspector[name]), dict(tools[owner][name])
        assert mine.pop("description") != theirs.pop("description")
        assert mine == theirs, name
    for name in ("reserved_completion", "reserved_tools", "safety_margin", "policy"):
        mine, theirs = dict(inspector[name]), dict(tools["harpe_synthesize_context"][name])
        mine.pop("description", None), theirs.pop("description", None)
        assert mine == theirs, name
    described = next(t for t in node("done(edge.tools);") if t["name"] == "telarch_open_inspector")["description"]
    assert "data_source" in described and "demonstration" in described and "It shows built-in demonstration data, not stored data" not in described


# ---- the page ---------------------------------------------------------------------------------------------

def test_the_page_labels_each_tab_with_where_its_data_came_from(chain):
    assert run([])[0]["sources"] == ["Demonstration data"] * 3
    assert run([], opened())[0]["sources"] == ["Demonstration data"] * 3
    mixed = run([], opened({**HARPE_ARGS, "events": chain}))[0]
    assert mixed["sources"] == ["Data from this conversation", "Demonstration data", "Data from this conversation"]


def test_the_page_shows_the_caller_s_items_and_a_slider_range_that_fits_them():
    shown = opened(HARPE_ARGS)
    first = run([], shown)[0]
    assert [re.search(r"<strong>(.*?)</strong>", row).group(1) for row in first["harpe"]] == [i["id"] for i in ITEMS]
    assert first["budget"] == "200" and first["slider"]["value"] == "200"
    # from the reserves (nothing fits) up to the budget at which every item fits
    everything = shown["harpe"]["consumed_tokens"] + shown["harpe"]["pruned_tokens"]
    assert first["slider"]["min"] == "35" and first["slider"]["max"] == str(35 + everything)
    assert structured("harpe_synthesize_context", {**HARPE_ARGS, "total_budget": 35 + everything})["pruned_items"] == []
    # the demonstration keeps the range written in the markup
    assert "min" not in run([], opened())[0]["slider"]


def test_repack_keeps_the_caller_s_reserves_policy_and_roles_and_leaves_their_chain_alone(chain):
    shown = opened({**HARPE_ARGS, "policy": "lowest_priority", "events": chain})
    after = run([{"click": "btn-repack", "slider": 120}], shown)[1]
    assert [c["name"] for c in after["calls"]] == ["harpe_synthesize_context"]  # the chain is not sealed again
    sent = after["calls"][0]["args"]
    assert sent["total_budget"] == 120 and sent["policy"] == "lowest_priority"
    assert {k: sent[k] for k in ("reserved_completion", "reserved_tools", "safety_margin")} == {"reserved_completion": 20, "reserved_tools": 10, "safety_margin": 5}
    assert [(i["id"], i.get("role")) for i in sent["items"]] == [(i["id"], i.get("role", "context")) for i in ITEMS]
    want = structured("harpe_synthesize_context", {**HARPE_ARGS, "policy": "lowest_priority", "total_budget": 120})
    kept = {re.search(r"<strong>(.*?)</strong>", row).group(1) for row in after["harpe"] if ">PRUNED<" not in row}
    assert kept == {i["id"] for i in want["included_items"]}
    assert after["head"] == chain[-1]["event_hash"] and after["sources"][0] == "Data from this conversation"


def test_the_page_calls_the_caller_s_chain_verified_because_the_server_verified_it(chain):
    first = run([], opened({"events": chain}))[0]
    assert first["banner"] == "CHAIN VALID: 2/2 events verified from GENESIS by argus_audit_verify"
    assert all(">VERIFIED<" in row for row in first["events"]) and first["head"] == chain[-1]["event_hash"]


def test_the_page_shows_a_changed_chain_as_broken_and_verify_does_not_clear_it(chain):
    changed = json.loads(json.dumps(chain))
    changed[0]["actor"] = "someone-else"
    steps = run(["btn-verify"], opened({"events": changed}))
    for step in steps:
        assert step["banner"].startswith("CHAIN BROKEN AT SEQ #1: ") and "err" in step["banner_class"]
    assert steps[1]["calls"][0]["args"] == {"events": changed}


def test_tamper_on_the_caller_s_chain_is_reported_and_verify_restores_it(chain):
    steps = run(["btn-tamper", "btn-verify"], opened({"events": chain}))
    assert steps[1]["banner"].startswith("CHAIN BROKEN AT SEQ #2: ")
    assert steps[1]["calls"][0]["args"]["events"][1]["payload"] == {"build": 41, "ok": True, "savings_bp": 9999}
    assert steps[2]["banner"].startswith("CHAIN VALID: 2/2 events verified")


def test_tamper_changes_a_payload_that_already_holds_the_tamper_value():
    sealed = structured("argus_audit_seal", {"events": [{"event_type": "a", "actor": "x", "payload": {}}, {"event_type": "b", "actor": "x", "payload": {"savings_bp": 9999}}]})
    after = run(["btn-tamper"], opened({"events": sealed["events"]}))[1]
    assert after["calls"][0]["args"]["events"][1]["payload"] == {"savings_bp": 9998}
    assert after["banner"].startswith("CHAIN BROKEN AT SEQ #2: ")


def test_recall_on_the_caller_s_records_sends_those_records():
    after = run(["btn-recall"], opened({"records": RECORDS}))[1]
    assert [c["name"] for c in after["calls"]] == ["kibisis_resolve_memory"]
    assert [r["key"] for r in after["calls"][0]["args"]["records"]] == [r["key"] for r in RECORDS]
    assert after["kibisis_meta"].startswith('Scope: default | Query: "" | 1 active, 1 superseded, 1 revoked.')
    assert after["sources"][1] == "Data from this conversation"


def test_a_tool_result_pushed_by_the_host_is_labelled_as_conversation_data():
    packed = structured("harpe_synthesize_context", HARPE_ARGS)
    first = run([], packed)[0]
    assert first["sources"] == ["Data from this conversation", "Demonstration data", "Demonstration data"]
    assert first["harpe_summary"].startswith("Effective: 165 tok")
