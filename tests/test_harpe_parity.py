"""The hosted worker and the local server must make the same Harpe decisions (review 2026-11-10, C01, E04-E07).

The reference is the harpe library, which the local server calls. For the same arguments both servers must
return the same effective budget and the same kept and pruned ids for every policy of the hosted enum, and they
must refuse the same calls. The cases are generated from a fixed seed, so a failure reproduces.
"""
from __future__ import annotations

import random

import pytest

from telarch_testlib import edge_rpc_many, isolate_environment, load_local_module, rejected

POLICIES = ["knapsack_dp", "lowest_priority", "fifo", "warm_prefix"]
COMPARED = ["policy_applied", "total_budget", "effective_budget", "consumed_tokens", "pruned_tokens", "control_overflow",
            "pinned_policy_digest", "included_ids", "pruned_ids"]
WORDS = ["alpha", "beta_gamma", "x", "deadbeefcafe0123", "0123456789abcdef0123", "naïve", "日本語のテキスト", "🙂", "a.b,c;d",
         "Zürich", "snake_case_name", "ΑΒΓ", "tab\tsep", "line\nbreak", "nbsp\u00a0here", "thin\u2009space", "zero\u200bwidth",
         "ffffffffffff", "CamelCaseWord", "12345678", "g" * 9, "ABCDEF12", "e\u0301", "\u3000ideographic", "\x1cfs", "\x85nel"]
SEPARATORS = [" ", "  ", "\n", "\t", "", "-", "\u2028"]


def _content(rng: random.Random) -> str:
    return "".join(rng.choice(WORDS) + rng.choice(SEPARATORS) for _ in range(rng.randint(0, rng.choice([3, 8, 30]))))


def _case(rng: random.Random) -> dict:
    items = []
    for index in range(rng.randint(0, rng.choice([3, 8, 14]))):
        item = {"id": f"i{index}", "content": _content(rng)}
        if rng.random() < 0.85:
            item["priority"] = rng.choice([0, 1, 10, 10, 50, 50, 90, 100, rng.randint(0, 100)])
        if rng.random() < 0.25:
            item["pinned"] = rng.random() < 0.6
        if rng.random() < 0.3:
            item["role"] = rng.choice(["system", "user", "assistant", "tool", "context"])
        items.append(item)
    total = sum(len(i["content"]) for i in items) // 4
    args = {"items": items, "total_budget": rng.choice([1, 5, 20, 60, max(1, total // 2), max(1, total), total + 50, 4000])}
    if rng.random() < 0.7:
        args.update(reserved_completion=rng.choice([0, 0, 3, 10]), reserved_tools=rng.choice([0, 0, 2]), safety_margin=rng.choice([0, 0, 1, 5]))
    return args


def _cases() -> list:
    rng = random.Random(20261110)
    out = []
    for _ in range(160):
        args = _case(rng)
        for policy in POLICIES:
            out.append(dict(args, policy=policy))
        out.append(args)  # no policy: both servers must apply the same default
    return out


def _request(name: str, arguments: dict) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


@pytest.fixture
def local(tmp_path, monkeypatch):
    isolate_environment(tmp_path, monkeypatch)
    return load_local_module().TelarchMCPServer()


def test_both_servers_keep_and_prune_the_same_items_for_every_policy(local):
    cases = _cases()
    hosted = edge_rpc_many([_request("harpe_synthesize_context", c) for c in cases])
    kept_something = pruned_something = 0
    for args, edge_answer in zip(cases, hosted):
        local_answer = local.handle_request(_request("harpe_synthesize_context", args))
        assert not rejected(edge_answer) and not rejected(local_answer), (args, edge_answer, local_answer)
        e, l = edge_answer["result"]["structuredContent"], local_answer["result"]["structuredContent"]
        assert {k: e[k] for k in COMPARED} == {k: l[k] for k in COMPARED}, args
        assert sorted(e["included_ids"] + e["pruned_ids"]) == sorted(i["id"] for i in args["items"])
        kept_something += bool(e["included_ids"])
        pruned_something += bool(e["pruned_ids"])
    # the generator must exercise both outcomes, or the comparison above proves little
    assert kept_something > len(cases) // 4 and pruned_something > len(cases) // 4


def test_both_servers_report_the_same_budget(local):
    rng = random.Random(7)
    cases = [{"total_budget": 8000}, {"total_budget": 1}, {"total_budget": 3584, "current_usage": 0}, {"total_budget": 3585, "current_usage": 1}]
    for _ in range(200):
        args = {"total_budget": rng.choice([1, 100, 4096, 8000, 200000, 2147483647])}
        for name in ("reserved_completion", "reserved_tools", "safety_margin", "current_usage"):
            if rng.random() < 0.6:
                args[name] = rng.choice([0, 1, 7, 512, 1024, 2048, rng.randint(0, 9000)])
        cases.append(args)
    hosted = edge_rpc_many([_request("harpe_budget_evaluate", c) for c in cases])
    for args, edge_answer in zip(cases, hosted):
        local_answer = local.handle_request(_request("harpe_budget_evaluate", args))
        assert edge_answer["result"]["structuredContent"] == local_answer["result"]["structuredContent"], args


def test_default_reserves_are_subtracted_by_both_servers(local):
    args = {"total_budget": 4000, "items": [{"id": "a", "content": "word " * 300}, {"id": "b", "content": "word " * 300}]}
    edge_out = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]["result"]["structuredContent"]
    local_out = local.handle_request(_request("harpe_synthesize_context", args))["result"]["structuredContent"]
    assert edge_out["effective_budget"] == local_out["effective_budget"] == 4000 - 2048 - 1024 - 512
    assert edge_out["included_ids"] == local_out["included_ids"] == ["a"]


REFUSED_BY_BOTH = {
    "policy outside the enum": {"total_budget": 100, "policy": "truncate_tail", "items": []},
    "priority above 100": {"total_budget": 100, "items": [{"id": "a", "content": "x", "priority": 101}]},
    "negative priority": {"total_budget": 100, "items": [{"id": "a", "content": "x", "priority": -1}]},
    "fractional priority": {"total_budget": 100, "items": [{"id": "a", "content": "x", "priority": 1.5}]},
    "duplicate ids": {"total_budget": 100, "items": [{"id": "a", "content": "x"}, {"id": "a", "content": "y"}]},
    "role outside the enum": {"total_budget": 100, "items": [{"id": "a", "content": "x", "role": "developer"}]},
    "empty id": {"total_budget": 100, "items": [{"id": "", "content": "x"}]},
    "zero budget": {"total_budget": 0, "items": []},
    "budget as text": {"total_budget": "100", "items": []},
    "undeclared argument": {"total_budget": 100, "items": [], "max_tokens": 5},
    "undeclared item field": {"total_budget": 100, "items": [{"id": "a", "content": "x", "weight": 3}]},
    "null item": {"total_budget": 100, "items": [None]},
    "more items than max_items": {"total_budget": 100, "items": [{"id": str(n), "content": ""} for n in range(4097)]},
}


@pytest.mark.parametrize("label", sorted(REFUSED_BY_BOTH))
def test_both_servers_refuse_the_same_calls(local, label):
    args = REFUSED_BY_BOTH[label]
    edge_answer = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]
    local_answer = local.handle_request(_request("harpe_synthesize_context", args))
    assert rejected(edge_answer), f"hosted server answered: {label}"
    assert rejected(local_answer), f"local server answered: {label}"
    assert ("error" in edge_answer) == ("error" in local_answer)
    if "error" in edge_answer:
        assert edge_answer["error"]["code"] == local_answer["error"]["code"] == -32602
        assert edge_answer["error"]["message"] == local_answer["error"]["message"]
    else:
        assert edge_answer["result"]["content"][0]["text"] == local_answer["result"]["content"][0]["text"]


def test_a_knapsack_above_the_stated_limit_is_refused_by_both_and_names_the_limit(local):
    # 3 items of coprime sizes against a capacity of 2,000,000 tokens: 3 x 2,000,001 cells > 4,000,000
    items = [{"id": "a", "content": "w " * 1_000_001}, {"id": "b", "content": "w " * 1_000_002}, {"id": "c", "content": "w " * 7}]
    args = {"total_budget": 2_000_000, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": items}
    edge_answer = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]
    local_answer = local.handle_request(_request("harpe_synthesize_context", args))
    for answer in (edge_answer, local_answer):
        assert answer["result"]["isError"] is True and "structuredContent" not in answer["result"]
        assert "max_knapsack_cells=4000000" in answer["result"]["content"][0]["text"]
    assert edge_answer["result"]["content"][0]["text"] == local_answer["result"]["content"][0]["text"]
    # the same items under a policy with no table are packed, by both, identically
    cheap = dict(args, policy="lowest_priority")
    e = edge_rpc_many([_request("harpe_synthesize_context", cheap)])[0]["result"]["structuredContent"]
    l = local.handle_request(_request("harpe_synthesize_context", cheap))["result"]["structuredContent"]
    assert e["included_ids"] == l["included_ids"] and e["effective_budget"] == l["effective_budget"] == 2_000_000


def test_a_large_budget_is_optimised_exactly_not_capped(local):
    # Before the fix the hosted table stopped at 8192 tokens while the answer still reported the full budget.
    items = [{"id": f"i{n}", "content": "w " * 3000, "priority": 50} for n in range(4)]
    args = {"total_budget": 9000, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": items}
    e = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]["result"]["structuredContent"]
    l = local.handle_request(_request("harpe_synthesize_context", args))["result"]["structuredContent"]
    assert e["effective_budget"] == l["effective_budget"] == 9000
    assert e["included_ids"] == l["included_ids"] and len(e["included_ids"]) == 3 and e["consumed_tokens"] == 9000


def test_a_huge_budget_that_holds_everything_needs_no_table(local):
    # 3 x 6,000,001 cells would be above the limit, but when every candidate fits there is nothing to optimise.
    items = [{"id": "a", "content": "w " * 1_000_001}, {"id": "b", "content": "w " * 1_000_002}, {"id": "c", "content": "w " * 7}]
    args = {"total_budget": 6_000_000, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": items}
    e = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]["result"]["structuredContent"]
    l = local.handle_request(_request("harpe_synthesize_context", args))["result"]["structuredContent"]
    assert e["included_ids"] == l["included_ids"] == ["a", "b", "c"] and e["pruned_ids"] == l["pruned_ids"] == []
    assert e["consumed_tokens"] == l["consumed_tokens"] == 2_000_010


def test_a_knapsack_just_under_the_limit_is_solved_identically(local):
    # 190 candidates x 20,001 capacities = 3,800,190 cells, below max_knapsack_cells
    rng = random.Random(3)
    items = [{"id": f"i{n}", "content": "w " * rng.randint(50, 400), "priority": rng.randint(1, 100)} for n in range(190)]
    args = {"total_budget": 20000, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": items}
    e = edge_rpc_many([_request("harpe_synthesize_context", args)])[0]["result"]["structuredContent"]
    l = local.handle_request(_request("harpe_synthesize_context", args))["result"]["structuredContent"]
    assert e["included_ids"] == l["included_ids"] and 0 < len(e["pruned_ids"]) < 190
    assert e["consumed_tokens"] == l["consumed_tokens"] <= 20000
