# Verifying the Local Argus Ledger

The ledger is one append-only JSONL file (`argus_ledger.jsonl` in the data folder, or the path in `ARGUS_LEDGER_PATH`). Each event stores the hash of the event before it, so an edit, a removal or a reordering changes every later hash.

## Steps

1. Call `argus_audit_verify` (no arguments).
2. `valid: true`: report `total_events` and `head_hash`. Keeping the head hash somewhere else is what lets a later check notice that the end of the file was cut off; a shortened ledger is still a valid chain on its own.
3. `valid: false`: report `first_broken_sequence` and `error_detail` as returned. Do not append further events until a person has looked at the file.
4. To show recent activity, call `argus_audit_tail`.

## What this plugin does not do

Neither Telarch server reads computation cards, battery files or git trees. Verifying those is outside this plugin.
