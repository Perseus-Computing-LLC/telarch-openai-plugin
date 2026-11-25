"""The Harpe tab says when the budget is used up and what used it up (issue 17).

Found in ChatGPT on 2026-11-17 and again on 2026-11-25. Until 0.3.1 the inspector copied seven fields of the
harpe_synthesize_context result and left out the overflow fields, so:

- total_budget 200 with the pinned demonstration item read "Consumed: 19 tok (0.0%)", which looks like an
  empty window, while the pack was 19 tokens over its budget;
- total_budget 2000 with two unpinned items read "Consumed: 0 tok (0.0%)" and each row said it did not fit
  "in the 0 tok left after the always-kept items", although no item was always kept: the default reserves
  (3584) were larger than the whole budget, and nothing on the tab said so.

The page now carries the reserve and overflow fields, says which of the two took the room, and the tool
descriptions say that an item's size is counted from its text and how to pack without reserves.
"""
from __future__ import annotations

import pytest

from telarch_testlib import edge_call, isolate_environment, load_local_module, local_call, node
from test_inspector_page import opened, run

CHATGPT_ITEMS = [  # what ChatGPT sent on 2026-11-25 for "'design doc' (priority 10, 400 tokens), 'chat log' (priority 60, 900 tokens)"
    {"id": "design-doc", "content": "design doc", "priority": 10},
    {"id": "chat-log", "content": "chat log", "priority": 60},
]
FIELDS = ("reserved_total", "reserves_exceed_budget", "shortfall_tokens", "control_overflow", "over_budget", "overflow_tokens")


def structured(tool, args):
    answer = edge_call(tool, args)
    assert "result" in answer and not answer["result"].get("isError"), answer
    return answer["result"]["structuredContent"]


@pytest.fixture
def local(tmp_path, monkeypatch):
    isolate_environment(tmp_path, monkeypatch)
    return load_local_module().TelarchMCPServer()


def test_the_case_from_the_report_shows_the_overflow_and_the_reserves():
    shown = opened({"total_budget": 200})
    h = shown["harpe"]
    assert {k: h[k] for k in FIELDS} == {"reserved_total": 3584, "reserves_exceed_budget": True, "shortfall_tokens": 3384,
                                          "control_overflow": True, "over_budget": True, "overflow_tokens": 19}
    page = run([], shown)[0]
    assert page["harpe_summary"] == "Effective: 0 tok | Consumed: 19 tok (19 tok over the budget) | Pruned: 65 tok"
    assert "0.0%" not in page["harpe_summary"]
    assert page["harpe_bar"] == {"width": "100%", "className": "bar-fill over"}
    warning = page["harpe_warning"]
    assert "the reserves (completion 2048 + tools 1024 + margin 512) need 3584 tok, 3384 tok more than the 200-tok total budget" in warning
    assert "The always-kept items (pinned or priority 0) need 19 tok and are kept anyway, 19 tok over the 0 tok available." in warning
    rows = dict(zip([i["id"] for i in h["items"]], page["harpe"]))
    assert "always kept: pinned or priority 0, even over the budget" in rows["sys_invariants"]
    assert "the reserves (3584 tok) take the whole 200-tok budget" in rows["stale_scratch"]


def test_the_chatgpt_case_of_2026_11_25_names_the_reserves_and_not_always_kept_items():
    shown = opened({"total_budget": 2000, "items": CHATGPT_ITEMS})
    h = shown["harpe"]
    assert {k: h[k] for k in FIELDS} == {"reserved_total": 3584, "reserves_exceed_budget": True, "shortfall_tokens": 1584,
                                          "control_overflow": False, "over_budget": False, "overflow_tokens": 0}
    page = run([], shown)[0]
    assert page["harpe_summary"] == "Effective: 0 tok | Consumed: 0 tok (0.0%) | Pruned: 5 tok"
    assert page["harpe_warning"].startswith("No room for context: the reserves (completion 2048 + tools 1024 + margin 512) need 3584 tok, 1584 tok more than the 2000-tok total budget.")
    assert "set them to 0" in page["harpe_warning"]
    for row in page["harpe"]:
        assert "pruned: no tokens are left for context; the reserves (3584 tok) take the whole 2000-tok budget" in row
        assert "always-kept" not in row


def test_reserves_that_fill_the_budget_exactly_are_named_without_a_shortfall():
    page = run([], opened({"total_budget": 3584, "items": CHATGPT_ITEMS}))[0]
    assert page["harpe_warning"].startswith("No room for context: the reserves (completion 2048 + tools 1024 + margin 512) take the whole 3584-tok total budget.")
    assert all("take the whole 3584-tok budget" in row for row in page["harpe"])


def test_with_room_and_no_always_kept_items_the_reason_says_tokens_available():
    args = {"total_budget": 3, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": CHATGPT_ITEMS}
    shown = opened(args)
    assert shown["harpe"]["effective_budget"] == 3 and not shown["harpe"]["reserves_exceed_budget"]
    page = run([], shown)[0]
    assert page["harpe_warning"] == "" and page["harpe_bar"]["className"] == "bar-fill"
    rows = dict(zip([i["id"] for i in CHATGPT_ITEMS], page["harpe"]))
    assert "kept: chosen for the 3 tok available" in rows["design-doc"]
    assert "pruned: it fits on its own" in rows["chat-log"]
    assert "always-kept" not in "".join(page["harpe"])


def test_the_demonstration_tab_still_says_nothing_is_wrong():
    page = run([])[0]
    assert page["harpe_warning"] == "" and page["harpe_bar"] == {"width": "67.86%", "className": "bar-fill"}
    assert page["harpe_summary"] == "Effective: 56 tok | Consumed: 38 tok (67.9%) | Pruned: 46 tok"


def test_a_pushed_harpe_result_carries_the_reserves_to_the_page():
    packed = structured("harpe_synthesize_context", {"total_budget": 2000, "items": CHATGPT_ITEMS})
    page = run([], packed)[0]
    assert page["sources"][0] == "Data from this conversation"
    assert "need 3584 tok, 1584 tok more than the 2000-tok total budget" in page["harpe_warning"]
    assert all("the reserves (3584 tok) take the whole 2000-tok budget" in row for row in page["harpe"])


def test_a_pushed_result_without_the_new_fields_is_still_read_from_its_numbers():
    # what a 0.3.0 server returned for a pinned 19-token item and total_budget 200
    old = structured("harpe_synthesize_context", {"total_budget": 200, "items": [{"id": "p", "content": "Enforce SQLCipher encryption and monotonic fencing tokens on every write.", "pinned": True}]})
    for k in ("reserved_total", "reserves_exceed_budget", "shortfall_tokens", "over_budget", "overflow_tokens"):
        old.pop(k)
    page = run([], old)[0]
    assert page["harpe_summary"] == "Effective: 0 tok | Consumed: 19 tok (19 tok over the budget) | Pruned: 0 tok"
    assert "take the whole 200-tok total budget" in page["harpe_warning"]


@pytest.mark.parametrize("args,reserved,exceed,shortfall", [
    ({"total_budget": 2000, "items": CHATGPT_ITEMS}, 3584, True, 1584),
    ({"total_budget": 3584, "items": CHATGPT_ITEMS}, 3584, False, 0),
    ({"total_budget": 50, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": CHATGPT_ITEMS}, 0, False, 0),
])
def test_both_servers_return_the_reserve_fields_from_harpe_synthesize_context(local, args, reserved, exceed, shortfall):
    hosted = structured("harpe_synthesize_context", args)
    here = local_call(local, "harpe_synthesize_context", args)["result"]["structuredContent"]
    for result in (hosted, here):
        assert (result["reserved_total"], result["reserves_exceed_budget"], result["shortfall_tokens"]) == (reserved, exceed, shortfall)


def test_with_the_reserves_at_0_the_items_are_packed_into_total_budget():
    packed = structured("harpe_synthesize_context", {"total_budget": 5, "reserved_completion": 0, "reserved_tools": 0, "safety_margin": 0, "items": CHATGPT_ITEMS})
    assert packed["effective_budget"] == 5 and packed["included_ids"] == ["design-doc", "chat-log"]


def test_descriptions_say_how_size_is_counted_and_how_to_pack_without_reserves(local):
    hosted = {t["name"]: t for t in node("done(edge.tools);")}
    listed = {t["name"]: t for t in local.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})["result"]["tools"]}
    for tools in (hosted, listed):
        props = tools["harpe_synthesize_context"]["inputSchema"]["properties"]
        assert "counted from its `content`" in props["items"]["description"]
        assert "no field for giving a token count" in props["items"]["description"]
        assert "set reserved_completion, reserved_tools and safety_margin to 0" in props["total_budget"]["description"]
        assert "reserves_exceed_budget" in tools["harpe_synthesize_context"]["description"]
    inspector = hosted["telarch_open_inspector"]["inputSchema"]["properties"]
    assert "set them to 0" in inspector["total_budget"]["description"]
    assert "no field for giving a token count" in inspector["items"]["description"]
