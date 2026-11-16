"""kibisis_resolve_memory: duplicate keys, supersession loops and a supersedes_key without a target.

Found by a test run in the ChatGPT desktop app on 2026-11-16 (issue 11). Until 0.2.3 the server resolved all
three without notice: two records under one key were both ACTIVE, two records that superseded each other were
both SUPERSEDED (nothing active, an empty envelope), and a supersedes_key that named no record was ignored.
"""
from __future__ import annotations

from telarch_testlib import edge_call, rejected

V = "verified"


def _call(records, query=""):
    return edge_call("kibisis_resolve_memory", {"query": query, "records": records})


def _refusal(records) -> str:
    answer = _call(records)
    assert rejected(answer), answer
    return answer["result"]["content"][0]["text"] if "result" in answer else answer["error"]["message"]


def _statuses(records) -> dict:
    answer = _call(records)
    assert not rejected(answer), answer
    out = answer["result"]["structuredContent"]
    return {f'{t["category"]}/{t["key"]}': t["status"] for t in out["all_records_trace"]}, out


def test_two_records_with_one_category_and_key_are_refused_and_named():
    text = _refusal([
        {"key": "other", "content": "zero", "epistemic_state": V},
        {"key": "same", "content": "one", "epistemic_state": V},
        {"key": "same", "content": "two", "epistemic_state": V},
    ])
    assert "DuplicateRecordKeyError" in text and '"same"' in text and "records[1]" in text and "records[2]" in text


def test_the_default_category_counts_as_the_category():
    # a record without `category` is in "decision", so it collides with one that says so
    text = _refusal([{"key": "k", "content": "one"}, {"key": "k", "category": "decision", "content": "two"}])
    assert "DuplicateRecordKeyError" in text and '"decision"' in text


def test_one_key_in_two_categories_is_allowed():
    statuses, out = _statuses([
        {"key": "k", "category": "decision", "content": "one", "epistemic_state": V},
        {"key": "k", "category": "convention", "content": "two", "epistemic_state": V},
    ])
    assert statuses == {"decision/k": "ACTIVE", "convention/k": "ACTIVE"} and out["resolved_count"] == 2


def test_a_loop_of_two_records_is_refused_and_names_both_keys():
    text = _refusal([
        {"key": "a", "content": "x one", "epistemic_state": V, "supersedes_key": "b"},
        {"key": "b", "content": "x two", "epistemic_state": V, "supersedes_key": "a"},
    ])
    assert "SupersessionLoopError" in text and '"a" supersedes "b" supersedes "a"' in text


def test_a_loop_of_three_records_is_refused_and_a_record_outside_it_is_not_named():
    text = _refusal([
        {"key": "start", "content": "s", "epistemic_state": V, "supersedes_key": "a"},
        {"key": "a", "content": "1", "epistemic_state": V, "supersedes_key": "b"},
        {"key": "b", "content": "2", "epistemic_state": V, "supersedes_key": "c"},
        {"key": "c", "content": "3", "epistemic_state": V, "supersedes_key": "a"},
    ])
    assert "SupersessionLoopError" in text and '"a" supersedes "b" supersedes "c" supersedes "a"' in text
    assert '"start"' not in text


def test_a_supersession_that_does_not_take_effect_closes_no_loop():
    # the candidate cannot displace the verified record, so only one direction holds
    statuses, _ = _statuses([
        {"key": "a", "content": "1", "epistemic_state": V, "supersedes_key": "b"},
        {"key": "b", "content": "2", "epistemic_state": "candidate", "supersedes_key": "a"},
    ])
    assert statuses == {"decision/a": "ACTIVE", "decision/b": "SUPERSEDED"}
    # a revoked record supersedes nothing and is not superseded
    statuses, _ = _statuses([
        {"key": "a", "content": "1", "epistemic_state": V, "supersedes_key": "b"},
        {"key": "b", "content": "2", "epistemic_state": "revoked", "supersedes_key": "a"},
    ])
    assert statuses == {"decision/a": "ACTIVE", "decision/b": "TOMBSTONED (REVOKED)"}


def test_a_record_that_names_itself_is_active_as_before():
    statuses, out = _statuses([{"key": "a", "content": "1", "epistemic_state": V, "supersedes_key": "a"}])
    assert statuses == {"decision/a": "ACTIVE"} and out["unresolved_supersedes"] == []


def test_a_supersedes_key_without_a_target_is_allowed_and_listed_once():
    statuses, out = _statuses([
        {"key": "a", "content": "1", "epistemic_state": V, "supersedes_key": "nope"},
        {"key": "b", "content": "2", "epistemic_state": V, "supersedes_key": "nope"},
        {"key": "c", "content": "3", "epistemic_state": "revoked", "supersedes_key": "gone"},
        {"key": "d", "content": "4", "epistemic_state": V, "supersedes_key": "a"},
    ])
    assert statuses == {"decision/a": "SUPERSEDED", "decision/b": "ACTIVE", "decision/c": "TOMBSTONED (REVOKED)", "decision/d": "ACTIVE"}
    assert out["unresolved_supersedes"] == ["nope", "gone"]


def test_the_demonstration_records_resolve_as_before():
    answer = edge_call("kibisis_resolve_memory", {"query": "SQLCipher encryption"})
    out = answer["result"]["structuredContent"]
    assert {t["key"]: t["status"] for t in out["all_records_trace"]} == {
        "db_engine_v1": "SUPERSEDED", "db_engine_v2": "ACTIVE", "temp_override": "TOMBSTONED (REVOKED)"}
    assert [r["key"] for r in out["resolved_records"]] == ["db_engine_v2"] and out["unresolved_supersedes"] == []


def test_a_chain_as_long_as_the_record_limit_resolves_in_either_order():
    n = 4096
    newest_last = [{"key": f"k{i}", "content": "c", "epistemic_state": V, **({"supersedes_key": f"k{i - 1}"} if i else {})} for i in range(n)]
    for records, survivor in ((newest_last, f"k{n - 1}"), (newest_last[::-1], f"k{n - 1}")):
        out = _call(records)["result"]["structuredContent"]
        assert [r["key"] for r in out["resolved_records"]] == [survivor]
        assert out["unresolved_supersedes"] == []


def test_a_loop_as_long_as_the_record_limit_is_refused_with_a_short_message():
    n = 4096
    records = [{"key": f"k{i}", "content": "c", "epistemic_state": V, "supersedes_key": f"k{(i + 1) % n}"} for i in range(n)]
    text = _refusal(records)
    assert "SupersessionLoopError" in text and f"({n} records in the loop)" in text and len(text) < 600


def test_the_tool_description_states_the_three_rules():
    from telarch_testlib import node
    tool = next(t for t in node("done(edge.tools);") if t["name"] == "kibisis_resolve_memory")
    for phrase in ("same category and key", "supersede each other in a loop", "unresolved_supersedes"):
        assert phrase in tool["description"], phrase
