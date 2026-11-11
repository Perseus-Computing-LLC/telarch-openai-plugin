# Telarch Plugin for ChatGPT & Codex

Official **ChatGPT** and **Codex** plugin repository for [**Telarch**](https://telarch.ai) by [**Perseus Computing LLC**](https://perseuscomputing.com) (MIT License).

Telarch is three open-source libraries, in Rust and Python, that control what an AI agent reads and remembers and prove what it did:
- **Harpe** chooses what goes into each model call under a token budget, the same way every time; pinned items always stay. Median call time: 30.88 µs for 200 items with a 1,500-token budget.
- **Kibisis** keeps agent memory in an encrypted SQLite file on your disk (Python package), with recall by scope, trust state (`candidate` until a person marks it `verified`) and date, tombstones that stick, and one writer at a time through fencing leases: 1,687,776 lease operations per second from 32 threads in one process, with 0 double grants.
- **Argus** keeps a SHA-256 hash chain of what the agent did and names the first edited event: full verification at 2,474,296 events per second; an edit at event 500,000 of 1,000,000 is found in 197.2 ms.

Figures are medians of 5 runs with synthetic data on one AWS EC2 m8azn.metal-12xl bare-metal server, measured at Harpe 0.1.0-alpha.11, Kibisis 0.1.0-alpha.12 and Argus 0.1.0-alpha.8. Every run, its range and the command that reproduces it: **[telarch.ai/evidence](https://telarch.ai/evidence)**.

The two plugins in this repository expose a part of these libraries. The tool lists below say which part; the fencing leases, for example, are a feature of the Kibisis library that the local plugin has no tool for.

---

## Included Plugin Packages

This repository provides two ready-to-use plugin distributions under [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json):

### 1. `plugins/telarch` — Universal ChatGPT (Web + Desktop) & Codex Plugin (`streamable-http` + MCP App UI)
- **Live MCP Endpoint:** `https://telarch.ai/mcp` (`type: "streamable-http"`, `auth.type: "none"`; stateless, nothing is kept between calls)
- **What the tools work on:** the arguments of the call, nothing else. The server stores no memory, holds no lease table and keeps no ledger: `kibisis_resolve_memory` resolves the records passed to it (or three built-in demonstration records when none are passed, and says so), `kibisis_lease_evaluate` compares the numbers passed to it, and `argus_audit_seal` / `argus_audit_verify` hash the events passed to them.
- **Refusals instead of defaults:** arguments are checked against each tool's input schema (JSON-RPC error -32602). Stated limits per call: 1 MiB request body, JSON nesting depth 64, 16 messages per batch, 4,096 items, 4,000,000 knapsack table cells. A call above a limit is refused with an error that names it.
- **Interactive MCP App UI (`ui://telarch/inspector-v1.html`):** 3-tab interactive visual inspector (**Harpe 0/1 Knapsack**, **Kibisis Epistemic Memory**, **Argus SHA-256 Chain**) supporting inline cards, global sidebar entrypoints, and thread side-panel entrypoints.
- **Tools Exposed (7):**
  - `telarch_open_inspector`
  - `harpe_synthesize_context`
  - `harpe_budget_evaluate`
  - `kibisis_resolve_memory`
  - `kibisis_lease_evaluate`
  - `argus_audit_seal`
  - `argus_audit_verify`
- **Bundled Skills (3):** `telarch-setup`, `telarch-recall`, `telarch-attest`

### 2. `plugins/telarch-local` — Desktop-Only Local SQLCipher `stdio` Plugin
- **Local `stdio` MCP Server:** `server/telarch_mcp_server.py` (`"requires_local_executor": true`)
- Works on two local files, the `kibisis` vault and the append-only `argus-ledger` JSONL file, and calls the local `harpe` engine. The server has no network code of its own.
- **Where the files are:** `PLUGIN_DATA` (set by the host) or `TELARCH_DATA_DIR`; without either, a per-user folder (`$XDG_DATA_HOME/telarch` or `~/.local/share/telarch`; `~/Library/Application Support/telarch` on macOS; `%LOCALAPPDATA%\telarch` on Windows). Never the folder the server was started in. `KIBISIS_DB_PATH` (other name: `KIBISIS_VAULT_PATH`) and `ARGUS_LEDGER_PATH` move the two files.
- **Vault encryption:** by default the server creates a key file `vault.key` beside the vault on first start (mode 0600) and the vault is a SQLCipher-encrypted file. That protects a vault file that is copied, synced or backed up without the key file; it does not protect against a reader of the whole folder. Set `KIBISIS_PASSPHRASE_FILE` or `KIBISIS_PASSPHRASE` to keep the key out of the folder; then no key file is written. A plain vault left by an earlier plugin version is kept and served as it is, and `kibisis_health` reports it as `plain`.
- **Tools Exposed (10):** `kibisis_remember`, `kibisis_recall`, `kibisis_forget`, `kibisis_verify_ledger`, `kibisis_health`, `harpe_budget_evaluate`, `harpe_synthesize_context`, `argus_audit_append`, `argus_audit_verify`, `argus_audit_tail`.

---

## Quickstart

### Install in Codex CLI / Desktop

Add this repository as a plugin marketplace, then add a plugin by name (tested with Codex CLI 0.166.0):

```bash
codex plugin marketplace add Perseus-Computing-LLC/telarch-openai-plugin
# local stdio plugin, runs on your machine:
codex plugin add telarch-local@perseus-telarch-plugins
# or the hosted plugin, which calls https://telarch.ai/mcp:
codex plugin add app-6a5586fe76788191a23b6b2c873a44a6@perseus-telarch-plugins
```

`telarch-local` needs Python 3.11 or later with the three libraries installed. These are the versions the server is tested with (`kibisis` brings its SQLCipher module, `sqlcipher3`, as a dependency):

```bash
pip install kibisis==0.1.0a17 harpe==0.1.0a13 argus-ledger==0.1.0a9
```

### Connect Directly in ChatGPT (Web or Desktop)

Add `https://telarch.ai/mcp` as a custom app (connector) in ChatGPT developer mode. The app is in review with OpenAI and not listed in the ChatGPT app directory yet. Setup steps: [telarch.ai/chatgpt](https://telarch.ai/chatgpt).

---

## The Two Servers Are Not the Same

The hosted server computes on what a call passes in; the local server works on files on your machine. Tools with the same name:

| tool | hosted (`plugins/telarch`) | local (`plugins/telarch-local`) |
|---|---|---|
| `harpe_budget_evaluate` | same arguments, same result | same arguments, same result |
| `harpe_synthesize_context` | same arguments, same kept and pruned ids as the local server (both follow `harpe` 0.1.0a13); the result has extra display fields | reference behaviour |
| `argus_audit_verify` | verifies the `events` passed in the call | takes no arguments and verifies this machine's ledger file |

In `harpe_synthesize_context`, `priority` runs from 0 to 100 and a lower number is more important; pinned items and priority 0 items are always kept; the budget packed against is `total_budget` minus the three reserves and is returned as `effective_budget`.

## Tests

```bash
pip install pytest kibisis==0.1.0a17 harpe==0.1.0a13 argus-ledger==0.1.0a9
python -m pytest -q tests
```

The tests need Node.js 22 or later (they load `edge/telarch_edge_mcp.js` in `node`) and Python 3.11 or later. They run against temporary folders and contact no server. `.github/workflows/ci.yml` runs them on every push to `main` and on pull requests.

---

## License

MIT License © 2026 Perseus Computing LLC. See [LICENSE](LICENSE).
