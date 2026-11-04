# Telarch Environment & Configuration Reference

Telarch runs locally over stdio with zero network calls.

## Environment Variables

- `KIBISIS_VAULT_PATH`: Path to the SQLite/SQLCipher memory vault (defaults to `${PLUGIN_DATA}/vault.sqlite` or `.telarch/vault.sqlite`).
- `KIBISIS_PASSPHRASE`: Passphrase for SQLCipher / entry-level AES-GCM encryption.
- `KIBISIS_ALLOW_PLAINTEXT`: Set to `1` only for local unencrypted development/testing.
- `KIBISIS_SCOPE`: Optional fixed scope override (`default` or repo-derived scope).
- `ARGUS_LEDGER_PATH`: Path to the append-only SHA-256 JSONL audit ledger (defaults to `${PLUGIN_DATA}/argus_ledger.jsonl`).
