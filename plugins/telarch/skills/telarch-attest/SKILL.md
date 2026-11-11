---
name: telarch-attest
description: Use when sealing or verifying an Argus SHA-256 audit chain. Seal a list of events into a hash chain and check a chain for edits.
---

# Telarch Audit Chains (hosted server)

Seal events into a SHA-256 hash chain and verify a chain that is passed in. The hosted server stores no ledger: the chain lives with the caller.

## Operational Rules

1. **Seal**: `argus_audit_seal` takes `events` (each with `event_type`, `actor` and `payload`) and returns them with `sequence`, `prev_hash` and `event_hash`, plus `head_hash`.
2. **Integers only**: a payload with a non-integer number is refused (`FloatPayloadError`), and so is an integer beyond 2**53 - 1 (`UnsafeIntegerError`). Use basis points or strings.
3. **Continue a chain**: pass the previous `head_hash` as `prev_hash` and give the first event its `sequence`.
4. **Verify**: `argus_audit_verify` takes the sealed `events` and recomputes every hash. It returns `valid`, `total_events`, `head_hash`, `anchor_prev_hash`, `starts_at_genesis` and, when broken, `first_broken_index`, `first_broken_sequence` and `error_detail`.
5. **Say what was proven**: `valid: true` means the events passed in are consistent with each other from `anchor_prev_hash` on. It proves the chain is complete only when `starts_at_genesis` is true and the caller compares `head_hash` with a value kept elsewhere.

## Supporting References

- See [Verification Guide](references/verification.md).
