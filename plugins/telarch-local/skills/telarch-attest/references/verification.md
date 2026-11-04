# Offline Attestation Verification Guide

This reference details offline, deterministic verification of Attested Computation cards.

## Verification Tool (`verify_attestation.py`)

Run verification without network or LLM calls:

```bash
python3 ops/tci/verify_attestation.py \
  --card phase-P16/battery-start.card.json \
  --battery phase-P16/battery-start.json
```

## Verification Checks

The verifier enforces:

1. **Card Conformance**: Validates card schema against OKF v0.2 §10.2 specifications.
2. **Chain Integrity**: Validates Argus ledger SHA-256 hash continuity from genesis to the receipt sequence.
3. **Bidirectional Binding**:
   - `battery.json` declares the receipt sequence number.
   - The Argus receipt payload embeds `battery_sha256` and `card_sha256`.
   - The card references the receipt sequence.
4. **Git Object Integrity**: Recomputes `computation_sha256` of the entrypoint file and verifies against the git tree at the recorded head.
