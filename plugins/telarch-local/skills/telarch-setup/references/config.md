# Telarch Local Server: Data Folder, Key and Environment

The local server (`server/telarch_mcp_server.py`) talks JSON-RPC over stdio and works on two local files: the Kibisis vault and the Argus ledger.

## Data folder

1. `PLUGIN_DATA` (set by the host), else `TELARCH_DATA_DIR`.
2. With neither: a per-user folder. `$XDG_DATA_HOME/telarch` or `~/.local/share/telarch` on Linux, `~/Library/Application Support/telarch` on macOS, `%LOCALAPPDATA%\telarch` on Windows.

The folder the server was started in is never used. Files in the data folder:

- `kibisis_vault.sqlite`: the memory vault.
- `vault.key`: the default key file (see below).
- `argus_ledger.jsonl`: the append-only audit ledger.

## Vault key

- Default: on first start the server creates `vault.key` beside the vault (32 random bytes as hex, file mode 0600) and the vault file is encrypted with it. This protects a vault file that is copied, synced or backed up without the key file. It does not protect against someone who can read the whole folder, because the key is in it.
- `KIBISIS_PASSPHRASE_FILE` or `KIBISIS_PASSPHRASE`: when one is set the server uses it and writes no key file, so the key stays out of the data folder.
- Losing the key (the key file or the passphrase) makes the vault unreadable. Back it up separately from the vault.
- A plain (unencrypted) vault with entries from an earlier plugin version is not converted. The server keeps serving it as it is and `kibisis_health` reports `vault_storage.mode: "plain"` with the reason.
- `KIBISIS_ALLOW_PLAINTEXT=1`: only when you set it yourself does the server create an unencrypted vault. The server never sets it.

## Environment variables

- `KIBISIS_DB_PATH`: path of the vault file. `KIBISIS_VAULT_PATH` is another name for it; `KIBISIS_DB_PATH` wins when both are set. The key file is created beside the vault.
- `ARGUS_LEDGER_PATH`: path of the ledger file.
- `KIBISIS_SCOPE`: the one scope the server works in. Without it the Kibisis library uses the project scope of the git checkout the server starts in, or `default` outside one.
- `KIBISIS_PASSPHRASE_FILE`, `KIBISIS_PASSPHRASE`, `KIBISIS_ALLOW_PLAINTEXT`: see "Vault key".
