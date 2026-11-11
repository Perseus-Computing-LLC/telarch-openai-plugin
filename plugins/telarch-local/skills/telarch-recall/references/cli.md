# Telarch Recall: Tool and Command Reference (local server)

## Recall

```python
kibisis_recall(
    query="keyword search terms",
    category="decision",      # optional
    match="any",              # "any" (default) or "all"
    limit=10,
    include_candidates=True   # False returns verified entries only
)
```

Optional as well: `as_of_valid_time` (a Unix time: recall what was valid then). The scope is fixed when the server starts; there is no argument that selects another scope or a trust state, and a call that passes one is refused.

The result is a `<kibisis-recall>` envelope with one `<entry>` per match, each labelled with `category`, `key`, `state`, `author` and `updated`.

## Write and delete

```python
kibisis_remember(category="convention", key="python_runtime", content="We use Python 3.12 with uv.")
kibisis_forget(category="convention", key="python_runtime", reason="superseded")
```

`kibisis_remember` stores a candidate. `kibisis_forget` removes the text and keeps a digest, so the same value cannot be written again until a person lifts the tombstone.

## Review at a terminal

Verifying a candidate is a person's action. Point the commands at the plugin's vault and key (see the [configuration reference](../../telarch-setup/references/config.md) for the data folder), and run them from the folder the server runs in or set `KIBISIS_SCOPE`, so that they work in the same scope:

```bash
export KIBISIS_DB_PATH="$PLUGIN_DATA/kibisis_vault.sqlite"
export KIBISIS_PASSPHRASE_FILE="$PLUGIN_DATA/vault.key"

# list candidates waiting for review
python3 -m kibisis.review list
python3 -m kibisis.review list --category convention

# approve one entry (needs a terminal)
python3 -m kibisis.review approve convention python_runtime
```

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

Both tools subtract `reserved_completion` (default 2048), `reserved_tools` (1024) and `safety_margin` (512) from `total_budget`; `harpe_synthesize_context` returns the result as `effective_budget` and packs against it. At most 4096 items. `knapsack_dp` is exact; a call that would need more than 4,000,000 table cells is refused with an error that names the limit, never approximated. Token counts are Harpe's deterministic estimate, not a model tokenizer's count.

The Harpe library has no command-line interface; use the tools.
