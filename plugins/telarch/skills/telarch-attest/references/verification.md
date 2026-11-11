# Verifying an Argus Chain (hosted server)

## Steps

1. Pass the sealed events, unchanged and in order, to `argus_audit_verify`. To check a segment that continues an earlier chain, also pass the earlier head hash as `prev_hash`.
2. `valid: true`: report `total_events`, `head_hash` and `starts_at_genesis`.
3. `valid: false`: report `first_broken_index`, `first_broken_sequence` and `error_detail` as returned. An event with a missing or altered field, a wrong hash, a wrong link or a sequence that does not follow the one before it makes the chain invalid.

## Limits of the check

- The server keeps no copy of any chain. It cannot tell whether events were removed from the end; compare `head_hash` with a value stored elsewhere.
- A chain that does not start at genesis is reported with `starts_at_genesis: false`.
- At most 4096 events per call.

## What this plugin does not do

Neither Telarch server reads computation cards, battery files or git trees. Verifying those is outside this plugin.
