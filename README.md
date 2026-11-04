# Telarch Plugin for ChatGPT & Codex

Official **ChatGPT** and **Codex** plugin repository for [**Telarch**](https://telarch.ai) by [**Perseus Computing LLC**](https://perseuscomputing.com) (MIT License).

Telarch is a cognitive infrastructure suite built in Rust and Python for AI coding and work agents:
- **Kibisis:** Encrypted local memory vault with tenant scope isolation, epistemic trust gating (`candidate` vs. human-promoted `verified`), tombstones (`revoked`), supersession chains, and monotonic fencing leases (`1.8M` lease decisions/sec across 32 threads, zero split-brain).
- **Harpe:** Microsecond `0/1` dynamic programming knapsack context budgeter (`43 µs` for 200 items, zero token budget overruns, cryptographic policy digest).
- **Argus:** Tamper-evident linear RFC 8785 (JCS) canonical JSON SHA-256 hash-chain audit ledger (`1M` events verified in `~200 ms`).

Benchmark evidence, raw reproduction commands, and datasets are published at **[https://telarch.ai/evidence](https://telarch.ai/evidence)**.

---

## Included Plugin Packages

This repository provides two ready-to-use plugin distributions under [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json):

### 1. `plugins/telarch` — Universal ChatGPT (Web + Desktop) & Codex Plugin (`streamable-http` + MCP App UI)
- **Live MCP Endpoint:** `https://telarch.ai/mcp` (`type: "streamable-http"`, `auth.type: "none"`, stateless zero-retention Cloudflare Edge execution)
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
```bash
codex plugin marketplace add Perseus-Computing-LLC/telarch-openai-plugin
codex plugin install telarch
# Or for local air-gapped SQLCipher stdio mode:
codex plugin install telarch-local
```

### Connect Directly in ChatGPT (Web or Desktop)
Add `https://telarch.ai/mcp` as an MCP connection in ChatGPT Developer Mode, or install from the ChatGPT Plugin Directory.

---

## License

MIT License © 2026 Perseus Computing LLC. See [LICENSE](LICENSE).
