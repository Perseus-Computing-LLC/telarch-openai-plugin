# OKF Attested Computation Cards Specification

This reference defines the OKF v0.2 §10.2 card structure used for Telarch phase batteries.

## Schema Layout

An Attested Computation card sidecar (`*.card.json`) contains:

```json
{
  "okf_version": "0.2.0",
  "type": "Attested Computation",
  "title": "Telarch Phase Battery Attestation",
  "description": "Deterministic balance mark execution",
  "runtime": "python3.14-linux-x86_64",
  "parameters": [
    {"name": "mark", "type": "string", "required": true}
  ],
  "executor": {
    "resource": "ops/tci/run_mark.py",
    "receipt": ["sequence", "event_hash", "battery_sha256", "verdict"]
  },
  "attester": {
    "resource": "ops/tci/verify_attestation.py"
  },
  "computation": "ops/tci/telarch_balance.py",
  "computation_sha256": "<64-hex-sha256>",
  "argus_receipt_seq": 75048
}
```

## Conformance Requirements

1. `okf_version` must be `"0.2.0"`.
2. `type` must be `"Attested Computation"`.
3. `executor.receipt` must list required receipt fields or receipt object.
4. `computation_sha256` must match git blob hash or execution script digest.
5. `argus_receipt_seq` must bind to a valid `tci.phase_boundary` event in the Argus ledger.
