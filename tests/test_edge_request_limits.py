"""Stated limits of the hosted worker's HTTP entry (items the 2026-11-10 review listed as suspected).

Before the fix a POST body of any size and any nesting depth was read and parsed, a body sent as text/plain was
served, and a deeply nested payload came back as the JavaScript engine's own "Maximum call stack size exceeded".
Each limit is a named entry of TELARCH_LIMITS and the refusal names it. Nothing here talks to a live server.
"""
from __future__ import annotations

import json

from telarch_testlib import edge_http, node

JSON_HEADERS = {"content-type": "application/json", "accept": "application/json, text/event-stream"}
PING = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
PING_PREFIX = '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":"'
PING_SUFFIX = '"}}'


def _post(body, headers=None) -> dict:
    return edge_http([{"headers": JSON_HEADERS if headers is None else headers, "body": body}])[0]


def _error(response: dict) -> dict:
    return json.loads(response["text"])["error"]


def _seal_with_payload_depth(depth: int) -> str:
    # payload is an object; `depth` counts the containers from the request object down to the innermost one
    outer = 6  # request > params > arguments > events > event > payload
    inner = depth - outer
    nested = '{"k":' * (inner - 1) + "{}" + "}" * (inner - 1) if inner > 0 else "{}"
    return ('{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"argus_audit_seal","arguments":'
            '{"events":[{"event_type":"t","actor":"a","timestamp":null,"payload":{"p":' + nested + "}}]}}}")


def test_limits_are_stated_in_one_table():
    limits = node("done(edge.limits);")
    assert limits == {"max_body_bytes": 1048576, "max_json_depth": 64, "max_batch_messages": 16, "max_items": 4096,
                      "max_knapsack_cells": 4000000, "max_token_value": 2147483647}


def test_body_at_the_limit_is_served_and_one_byte_more_is_refused_with_413():
    room = 1048576 - len(PING_PREFIX) - len(PING_SUFFIX)
    at_limit, over = edge_http([
        {"headers": JSON_HEADERS, "body": {"prefix": PING_PREFIX, "repeat": "a", "times": room, "suffix": PING_SUFFIX}},
        {"headers": JSON_HEADERS, "body": {"prefix": PING_PREFIX, "repeat": "a", "times": room + 1, "suffix": PING_SUFFIX}},
    ])
    assert at_limit["status"] == 200 and json.loads(at_limit["text"]) == {"jsonrpc": "2.0", "id": 1, "result": {}}
    assert over["status"] == 413
    assert _error(over) == {"code": -32600, "message": "Request body exceeds the limit max_body_bytes=1048576"}


def test_body_size_is_counted_in_bytes_not_characters():
    # 400,000 three-byte characters: under the limit as characters, over it as UTF-8 bytes
    response = _post({"prefix": PING_PREFIX, "repeat": "\u20ac", "times": 400000, "suffix": PING_SUFFIX})
    assert response["status"] == 413


def test_a_declared_content_length_above_the_limit_is_refused_before_reading():
    response = _post(json.dumps(PING), dict(JSON_HEADERS, **{"content-length": "99999999"}))
    assert response["status"] == 413


def test_nesting_at_the_limit_is_parsed_and_one_level_more_is_refused():
    at_limit, over, absurd = edge_http([
        {"headers": JSON_HEADERS, "body": _seal_with_payload_depth(64)},
        {"headers": JSON_HEADERS, "body": _seal_with_payload_depth(65)},
        {"headers": JSON_HEADERS, "body": _seal_with_payload_depth(60000)},
    ])
    assert at_limit["status"] == 200 and json.loads(at_limit["text"])["result"]["isError"] is False
    for response in (over, absurd):
        assert response["status"] == 400
        assert _error(response) == {"code": -32600, "message": "Request body is nested deeper than the limit max_json_depth=64"}
        assert "call stack" not in response["text"]


def test_brackets_inside_a_string_do_not_count_as_nesting():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {"x": "[{" * 400 + '\\"' + "[" * 100}})
    assert _post(body)["status"] == 200


def test_a_post_that_is_not_json_is_refused_with_415():
    for content_type in ("text/plain", "application/x-www-form-urlencoded", "multipart/form-data; boundary=x", "application/jsonx"):
        response = _post(json.dumps(PING), {"content-type": content_type})
        assert response["status"] == 415, content_type
        assert _error(response)["code"] == -32600
    for content_type in ("application/json", "application/json; charset=utf-8", "Application/JSON"):
        assert _post(json.dumps(PING), {"content-type": content_type})["status"] == 200, content_type


def test_a_client_that_cannot_take_json_is_refused_with_406():
    for accept in ("text/event-stream", "text/html", "image/png, text/plain"):
        response = _post(json.dumps(PING), {"content-type": "application/json", "accept": accept})
        assert response["status"] == 406, accept
    for accept in ("application/json", "application/json, text/event-stream", "*/*", "application/*", "text/html, */*;q=0.1"):
        assert _post(json.dumps(PING), {"content-type": "application/json", "accept": accept})["status"] == 200, accept
    # no Accept header at all: served (the header is the client's duty, and JSON is all this server sends)
    assert _post(json.dumps(PING), {"content-type": "application/json"})["status"] == 200


def test_batches_are_limited_and_not_taken_under_2025_06_18():
    sixteen, seventeen, current = edge_http([
        {"headers": JSON_HEADERS, "body": json.dumps([PING] * 16)},
        {"headers": JSON_HEADERS, "body": json.dumps([PING] * 17)},
        {"headers": dict(JSON_HEADERS, **{"mcp-protocol-version": "2025-06-18"}), "body": json.dumps([PING] * 2)},
    ])
    assert sixteen["status"] == 200 and len(json.loads(sixteen["text"])) == 16
    assert seventeen["status"] == 400 and "max_batch_messages=16" in _error(seventeen)["message"]
    assert current["status"] == 400 and _error(current)["code"] == -32600


def test_refusals_carry_cors_headers_only_for_an_admitted_origin():
    listed, unlisted, none = edge_http([
        {"headers": dict(JSON_HEADERS, origin="https://chatgpt.com"), "body": "x" },
        {"headers": dict(JSON_HEADERS, origin="https://chatgpt.com.evil.example"), "body": json.dumps(PING)},
        {"headers": JSON_HEADERS, "body": "x"},
    ])
    assert listed["status"] == 400 and listed["headers"]["access-control-allow-origin"] == "https://chatgpt.com"
    assert unlisted["status"] == 403 and "access-control-allow-origin" not in unlisted["headers"]
    assert none["status"] == 400 and "access-control-allow-origin" not in none["headers"]
    for response in (listed, unlisted, none):
        assert "origin" in response["headers"].get("vary", "").lower()
