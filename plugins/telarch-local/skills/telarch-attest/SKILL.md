---
name: telarch-attest
description: Use when recording or verifying entries in the local Argus audit ledger. Append events, verify the SHA-256 chain, read the latest events.
---

# Telarch Audit Ledger (local server)

Record what was done in this machine's Argus ledger and verify that the ledger has not been edited.

## Operational Rules

1. **Append**: `argus_audit_append` takes `event_type`, `actor` and `payload` (an object) and returns `sequence`, `event_hash` and `prev_hash`.
2. **No floats in payloads**: a payload containing a non-integer number is refused (`FloatPayloadError`). Store basis points or a fixed-format string instead.
3. **Verify**: `argus_audit_verify` takes no arguments. It checks the whole ledger file from its first event and returns `valid`, `total_events`, `head_hash` and, when the chain is broken, `first_broken_sequence` and `error_detail`. It does not verify events passed to it; a call with arguments is refused.
4. **Read**: `argus_audit_tail` returns the latest events (`limit` 1 to 50, default 5).
5. Report the values the tools return. Do not state that a chain is valid without calling `argus_audit_verify`.

## Supporting References

- See [Verification Guide](references/verification.md).
