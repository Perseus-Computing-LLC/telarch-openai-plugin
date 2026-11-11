"""kibisis_resolve_memory on the hosted worker: which records a call resolves, and that the result says so.

The app's published example ("Resolve active memory records in Kibisis for query 'SQLCipher' in scope 'default'")
passes no records and expects the built-in demonstration to answer. A call that does pass records must never
have demonstration records mixed in.
"""
from __future__ import annotations

from telarch_testlib import edge_call


def test_a_call_without_records_resolves_the_demonstration_records_and_says_so():
    out = edge_call("kibisis_resolve_memory", {"query": "SQLCipher", "active_scope": "default"})["result"]["structuredContent"]
    assert out["records_source"] == "demonstration"
    assert [r["key"] for r in out["resolved_records"]] == ["db_engine_v2"]
    statuses = {r["key"]: r["status"] for r in out["all_records_trace"]}
    assert statuses["db_engine_v1"] == "SUPERSEDED" and "REVOKED" in statuses["temp_override"]
    assert out["envelope"].startswith('<kibisis-recall trust="untrusted-stored-text" scope="default">')


def test_records_of_the_call_are_resolved_alone():
    mine = [{"key": "k", "content": "SQLCipher is our engine", "epistemic_state": "verified"}]
    out = edge_call("kibisis_resolve_memory", {"query": "SQLCipher", "records": mine})["result"]["structuredContent"]
    assert out["records_source"] == "request"
    assert [r["key"] for r in out["all_records_trace"]] == ["k"] and "db_engine" not in out["envelope"]


def test_an_empty_list_resolves_nothing():
    out = edge_call("kibisis_resolve_memory", {"query": "SQLCipher", "records": []})["result"]["structuredContent"]
    assert out["records_source"] == "request" and out["resolved_count"] == 0 and out["all_records_trace"] == []
    assert "db_engine" not in out["envelope"]
