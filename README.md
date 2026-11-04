# Telarch Plugin for ChatGPT & Codex

Official **ChatGPT** and **Codex** plugin repository for [**Telarch**](https://telarch.ai) by [**Perseus Computing LLC**](https://perseuscomputing.com) (MIT License).

Telarch is three open-source libraries, in Rust and Python, that control what an AI agent reads and remembers and prove what it did:
- **Harpe** chooses what goes into each model call under a token budget, the same way every time; pinned items always stay. Median call time: 30.88 µs for 200 items with a 1,500-token budget.
- **Kibisis** keeps agent memory in an encrypted SQLite file on your disk (Python package), with recall by scope, trust state (`candidate` until a person marks it `verified`) and date, tombstones that stick, and one writer at a time through fencing leases: 1,687,776 lease operations per second from 32 threads in one process, with 0 double grants.
- **Argus** keeps a SHA-256 hash chain of what the agent did and names the first edited event: full verification at 2,474,296 events per second; an edit at event 500,000 of 1,000,000 is found in 197.2 ms.

Figures are medians of 5 runs with synthetic data on one AWS EC2 m8azn.metal-12xl bare-metal server, measured at Harpe 0.1.0-alpha.11, Kibisis 0.1.0-alpha.12 and Argus 0.1.0-alpha.8. Every run, its range and the command that reproduces it: **[telarch.ai/evidence](https://telarch.ai/evidence)**.

---

## Included Plugin Packages

This repository provides two ready-to-use plugin distributions under [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json):

### 1. `plugins/telarch` — Universal ChatGPT (Web + Desktop) & Codex Plugin (`streamable-http` + MCP App UI)
- **Live MCP Endpoint:** `https://telarch.ai/mcp` (`type: "streamable-http"`, `auth.type: "none"`; stateless, nothing is kept between calls)
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
- Runs 100% offline against a local SQLCipher AES-256 vault (`kibisis`), local `harpe` engine, and local append-only `argus-ledger` JSONL file in `${PLUGIN_DATA}`.
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

`telarch-local` needs Python 3.11 or later with the libraries installed. It keeps its vault and ledger in the plugin data folder (`PLUGIN_DATA`):

```bash
pip install harpe kibisis argus-ledger
```

### Connect Directly in ChatGPT (Web or Desktop)

Add `https://telarch.ai/mcp` as a custom app (connector) in ChatGPT developer mode. The app is in review with OpenAI and not listed in the ChatGPT app directory yet. Setup steps: [telarch.ai/chatgpt](https://telarch.ai/chatgpt).

---

## License

MIT License © 2026 Perseus Computing LLC. See [LICENSE](LICENSE).
