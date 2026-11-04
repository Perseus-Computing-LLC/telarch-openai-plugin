---
name: telarch-setup
description: Use when initializing or verifying the Telarch plugin in ChatGPT or Codex. Check vault health, token budget, and audit chain.
---

# Telarch Onboarding & Setup

Verify that the local Telarch cognitive infrastructure (Kibisis encrypted vault, Harpe context knapsack, and Argus SHA-256 audit ledger) is active and healthy for the current workspace.

## Procedure

1. Call `kibisis_health` to confirm the active project scope, encryption state, and stored entity counts.
2. Call `argus_audit_verify` to confirm the linear SHA-256 audit ledger has unbroken chain continuity from genesis.
3. Call `harpe_budget_evaluate` with `total_budget=8000` to verify deterministic context budget calculation.
4. Report the active scope, encryption status, and audit chain head hash to the user, and offer to store initial project conventions via `kibisis_remember` or query existing memories via `kibisis_recall`.

## Operational Boundaries

- Do not invent or fabricate vault entries, hashes, or budget figures.
- All writes via `kibisis_remember` are stored with `epistemic_state="candidate"` until promoted by a human reviewer (`python -m kibisis.review`).
- See [Configuration Reference](references/config.md) for environment variables (`KIBISIS_PASSPHRASE`, `KIBISIS_SCOPE`, `ARGUS_LEDGER_PATH`).
