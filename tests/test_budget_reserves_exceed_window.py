"""harpe_budget_evaluate says outright when the reserves are larger than the window (issue 13).

Found on 2026-11-16: with total_budget 2000 and the default reserves (2048 + 1024 + 512 = 3584) the tool
returned available_context 0, utilization_pct 100 and is_exceeded false. Each figure is what the harpe
library's TokenBudget gives, and the two servers are held to the library, but together they read as "the
window is full and not exceeded" when in fact no context fits at all. Two fields now say so; the three
library figures are unchanged.
"""
from __future__ import annotations

import pytest
from harpe.models import TokenBudget

from telarch_testlib import edge_call, isolate_environment, load_local_module, local_call, node

CASES = [
    # arguments, reserved_total, available_context, reserves_exceed_budget, shortfall_tokens
    ({"total_budget": 2000}, 3584, 0, True, 1584),
    ({"total_budget": 3583}, 3584, 0, True, 1),
    ({"total_budget": 3584}, 3584, 0, False, 0),  # the reserves fill the window exactly: nothing is left, nothing is short
    ({"total_budget": 3585}, 3584, 1, False, 0),
    ({"total_budget": 8000}, 3584, 4416, False, 0),
    ({"total_budget": 100, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0}, 0, 100, False, 0),
    ({"total_budget": 100, "reserved_completion": 60, "reserved_tools": 30, "safety_margin": 20, "current_usage": 5}, 110, 0, True, 10),
]


@pytest.fixture
def local(tmp_path, monkeypatch):
    isolate_environment(tmp_path, monkeypatch)
    return load_local_module().TelarchMCPServer()


@pytest.mark.parametrize("args,reserved,available,exceed,shortfall", CASES, ids=[str(c[0]["total_budget"]) + "/" + str(c[1]) for c in CASES])
def test_both_servers_report_reserves_larger_than_the_window(local, args, reserved, available, exceed, shortfall):
    hosted = edge_call("harpe_budget_evaluate", args)["result"]["structuredContent"]
    here = local_call(local, "harpe_budget_evaluate", args)["result"]["structuredContent"]
    assert hosted == here
    assert hosted["reserved_total"] == reserved and hosted["available_context"] == available
    assert hosted["reserves_exceed_budget"] is exceed and hosted["shortfall_tokens"] == shortfall
    # a shortfall is reported exactly when the reserves exceed the window, and then nothing is available
    assert (hosted["shortfall_tokens"] > 0) == hosted["reserves_exceed_budget"]
    assert not hosted["reserves_exceed_budget"] or hosted["available_context"] == 0


@pytest.mark.parametrize("args", [c[0] for c in CASES], ids=[str(c[0]["total_budget"]) + "/" + str(c[1]) for c in CASES])
def test_the_three_library_figures_are_still_the_library_s(args):
    hosted = edge_call("harpe_budget_evaluate", args)["result"]["structuredContent"]
    budget = TokenBudget(
        total_budget=args["total_budget"],
        reserved_completion=args.get("reserved_completion", 2048),
        reserved_tools=args.get("reserved_tools", 1024),
        safety_margin=args.get("safety_margin", 512),
    )
    used = args.get("current_usage", 0)
    assert hosted["available_context"] == budget.available_context
    assert hosted["utilization_pct"] == round(budget.utilization_pct(used), 2)
    assert hosted["is_exceeded"] is budget.is_exceeded(used)


def test_the_case_from_the_report():
    out = edge_call("harpe_budget_evaluate", {"total_budget": 2000})["result"]["structuredContent"]
    assert out == {
        "total_budget": 2000,
        "reserved_total": 3584,
        "available_context": 0,
        "current_usage": 0,
        "utilization_pct": 100,
        "is_exceeded": False,
        "reserves_exceed_budget": True,
        "shortfall_tokens": 1584,
    }


def test_both_tool_descriptions_explain_the_new_fields_and_the_zero_case(local):
    hosted = next(t for t in node("done(edge.tools);") if t["name"] == "harpe_budget_evaluate")["description"]
    listed = local.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})["result"]["tools"]
    here = next(t for t in listed if t["name"] == "harpe_budget_evaluate")["description"]
    for text in (hosted, here):
        for word in ("reserves_exceed_budget", "shortfall_tokens", "reserved_total", "is_exceeded stays false while current_usage is 0"):
            assert word in text
