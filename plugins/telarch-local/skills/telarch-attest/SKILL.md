---
name: telarch-attest
description: Use when verifying Telarch computation cards or receipts. Verify OKF Attested Computation sidecars and Argus receipt bindings.
---

# Telarch Attestation Verification

Verify deterministic computation attestations, OKF sidecar cards, and Argus audit ledger bindings.

## Operational Rules

1. **Deterministic and Offline**: Never invoke remote networks or LLMs for attestation verification.
2. **Bidirectional Binding**: Always verify both directions: the battery references the receipt sequence, and the receipt payload embeds the SHA-256 hashes of the battery and its card sidecar.
3. **Chain Continuity**: Confirm Argus ledger cryptographic hash chain verification passes up to the receipt sequence.
4. **Git Tree Verification**: Confirm computation entrypoint digest matches the recorded Git commit tree object.

## Supporting References

- See [Attested Computation Cards Specification](references/cards.md) for OKF §10.2 schema rules.
- See [Verification Guide](references/verification.md) for offline verification instructions.
