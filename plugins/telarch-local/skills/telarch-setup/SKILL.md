---
name: telarch-setup
description: Use when initializing or verifying the Telarch plugin in ChatGPT or Codex. Check vault health, token budget, and audit chain.
---

# Telarch Onboarding & Setup

Verify that the local Telarch server (Kibisis memory vault, Harpe context budgeting, Argus SHA-256 audit ledger) is running and healthy on this machine.

## Procedure

1. Call `kibisis_health`. Report `scope`, `by_state` and `vault_storage`: `mode` is `encrypted` or `plain`, and `key_source` says where the key comes from.
2. Call `argus_audit_verify` with no arguments. It verifies this machine's ledger file from its first event and returns `valid`, `total_events` and `head_hash`.
3. Call `harpe_budget_evaluate` with `total_budget=8000`. With the default reserves (2048 + 1024 + 512) `available_context` is 4416.
4. Report the scope, the vault storage mode and the ledger head hash, and offer to store project conventions via `kibisis_remember` or to search stored memory via `kibisis_recall`.

## Operational Boundaries

- Do not invent vault entries, hashes or budget figures; report what the tools return.
- `kibisis_remember` always stores a `candidate`. It has no argument that sets a trust state; only a person can verify an entry, at a terminal, with `python3 -m kibisis.review`.
- If `vault_storage.mode` is `plain`, say so. Do not describe the vault as encrypted.
- A call with an argument the tool does not declare is refused (JSON-RPC error -32602); nothing is stored or changed by a refused call.
- See [Configuration Reference](references/config.md) for the data folder, the key file and the environment variables.
