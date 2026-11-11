# Telarch Recall: Tool Reference (hosted server)

The hosted plugin has no command-line interface and stores nothing. Everything is a tool call.

## Resolve records

```python
kibisis_resolve_memory(
    query="SQLCipher",
    active_scope="default",
    records=[
        {"key": "db_engine_v1", "content": "Use unencrypted SQLite.", "epistemic_state": "verified"},
        {"key": "db_engine_v2", "content": "Use SQLCipher.", "epistemic_state": "verified", "supersedes_key": "db_engine_v1"},
    ],
)
```

- `query` is required; an empty string matches every active record.
- `requested_scope`, when given, must equal `active_scope`; otherwise the call is refused with `ScopeIsolationError`.
- `write_attempt={"origin": "model" or "user", "epistemic_state": ...}` evaluates the write gate: `verified` is accepted only with origin `user`; otherwise the call is refused with `EpistemicTrustViolation`.
- The result has `resolved_records`, `all_records_trace` (every record with its status), `records_source` and `envelope`.

## Check a fencing token

```python
kibisis_lease_evaluate(holder_id="worker-1", fencing_token=42, highest_token_seen=41)
```

A token below `highest_token_seen` is refused with `StaleFencingTokenError`. `lease_expires_epoch` and `now_epoch` (whole numbers) are optional: an expiry is checked against the `now_epoch` of the same call, and an expiry without `now_epoch` is refused (`LeaseClockMissingError`).

## Harpe

```python
harpe_budget_evaluate(total_budget=8000, current_usage=1200)

harpe_synthesize_context(
    total_budget=8000,
    policy="knapsack_dp",     # or "lowest_priority", "fifo", "warm_prefix"
    items=[
        {"id": "invariants", "content": "...", "pinned": True},
        {"id": "decision", "content": "...", "priority": 10},
        {"id": "scratch", "content": "...", "priority": 90},
    ],
)
```

Both tools subtract `reserved_completion` (default 2048), `reserved_tools` (1024) and `safety_margin` (512) from `total_budget`; `harpe_synthesize_context` returns the result as `effective_budget` and packs against it. Pinned items are kept even when they alone exceed the budget; the result then reports `over_budget` and `overflow_tokens`. At most 4096 items. `knapsack_dp` is exact; a call that would need more than 4,000,000 table cells is refused with an error that names the limit. Token counts are Harpe's deterministic estimate, not a model tokenizer's count.
