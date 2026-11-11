// Telarch Streamable-HTTP MCP Server + Interactive MCP App UI (Cloudflare Edge)
// MIT License (c) 2026 Perseus Computing LLC

const OPENAI_APPS_CHALLENGE_TOKEN = "tvvlXj9ABL4IHa4f6ecObVVH3P-6FniKSZQ6xTuvDYw";

const INSPECTOR_URI = "ui://telarch/inspector-v1.html";

const INSPECTOR_HTML = "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>Telarch Cognitive Infrastructure Inspector</title>\n<style>\n  :root {\n    --bg: #0b101b;\n    --panel: #121a2b;\n    --border: #23324d;\n    --text: #e6edf7;\n    --muted: #8fa3c0;\n    --accent: #4da3ff;\n    --ok: #2ecc71;\n    --warn: #f39c12;\n    --err: #ff5c5c;\n    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;\n    --sans: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;\n  }\n  * { box-sizing: border-box; }\n  body {\n    margin: 0;\n    padding: 14px;\n    font-family: var(--sans);\n    background: var(--bg);\n    color: var(--text);\n    font-size: 13px;\n    line-height: 1.45;\n  }\n  .header {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    border-bottom: 1px solid var(--border);\n    padding-bottom: 10px;\n    margin-bottom: 12px;\n  }\n  .brand {\n    display: flex;\n    align-items: center;\n    gap: 8px;\n    font-weight: 700;\n    font-size: 14px;\n    letter-spacing: 0.02em;\n  }\n  .badge {\n    font-family: var(--mono);\n    font-size: 11px;\n    padding: 2px 7px;\n    border-radius: 4px;\n    background: rgba(77,163,255,0.14);\n    color: var(--accent);\n    border: 1px solid rgba(77,163,255,0.35);\n  }\n  .badge.ok { background: rgba(46,204,113,0.14); color: var(--ok); border-color: rgba(46,204,113,0.35); }\n  .badge.warn { background: rgba(243,156,18,0.14); color: var(--warn); border-color: rgba(243,156,18,0.35); }\n  .badge.err { background: rgba(255,92,92,0.14); color: var(--err); border-color: rgba(255,92,92,0.35); }\n  .tabs {\n    display: flex;\n    gap: 6px;\n    margin-bottom: 12px;\n  }\n  .tab {\n    flex: 1;\n    padding: 7px 10px;\n    background: var(--panel);\n    color: var(--muted);\n    border: 1px solid var(--border);\n    border-radius: 6px;\n    cursor: pointer;\n    font-weight: 600;\n    font-size: 12px;\n    text-align: center;\n  }\n  .tab.active {\n    color: var(--text);\n    border-color: var(--accent);\n    background: rgba(77,163,255,0.12);\n  }\n  .card {\n    background: var(--panel);\n    border: 1px solid var(--border);\n    border-radius: 8px;\n    padding: 12px;\n    margin-bottom: 10px;\n  }\n  .row {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    gap: 8px;\n    margin-bottom: 8px;\n  }\n  .bar-wrap {\n    height: 12px;\n    background: #080c14;\n    border-radius: 6px;\n    overflow: hidden;\n    border: 1px solid var(--border);\n    margin: 8px 0;\n  }\n  .bar-fill {\n    height: 100%;\n    background: linear-gradient(90deg, #2b7de9, #2ecc71);\n    transition: width 0.2s ease;\n  }\n  .item-list {\n    display: flex;\n    flex-direction: column;\n    gap: 6px;\n    margin-top: 8px;\n  }\n  .item {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    padding: 6px 8px;\n    border-radius: 5px;\n    background: #0d1422;\n    border: 1px solid var(--border);\n    font-size: 12px;\n  }\n  .mono { font-family: var(--mono); font-size: 11px; color: var(--muted); word-break: break-all; }\n  button.btn {\n    background: #1b6ef3;\n    color: #fff;\n    border: none;\n    border-radius: 5px;\n    padding: 6px 11px;\n    font-size: 12px;\n    font-weight: 600;\n    cursor: pointer;\n  }\n  button.btn.secondary {\n    background: transparent;\n    border: 1px solid var(--border);\n    color: var(--text);\n  }\n  button.btn.danger {\n    background: rgba(255,92,92,0.18);\n    border: 1px solid rgba(255,92,92,0.45);\n    color: var(--err);\n  }\n  input[type=\"range\"] { width: 160px; }\n  .hidden { display: none; }\n</style>\n</head>\n<body>\n  <div class=\"header\">\n    <div class=\"brand\">\n      <span>TELARCH</span>\n      <span class=\"badge\">Kibisis · Harpe · Argus</span>\n    </div>\n    <span id=\"status-badge\" class=\"badge ok\">MCP Ready</span>\n  </div>\n\n  <div class=\"tabs\">\n    <button class=\"tab active\" data-tab=\"harpe\">Harpe 0/1 Knapsack</button>\n    <button class=\"tab\" data-tab=\"kibisis\">Kibisis Memory</button>\n    <button class=\"tab\" data-tab=\"argus\">Argus SHA-256 Chain</button>\n  </div>\n\n  <!-- TAB 1: HARPE -->\n  <div id=\"panel-harpe\" class=\"panel\">\n    <div class=\"card\">\n      <div class=\"row\">\n        <strong>0/1 Knapsack Context Budgeter</strong>\n        <div>\n          <label for=\"budget-slider\" class=\"mono\">Total Budget: <span id=\"budget-val\">3600</span> tok</label>\n          <input id=\"budget-slider\" type=\"range\" min=\"3580\" max=\"3750\" step=\"5\" value=\"3640\">\n        </div>\n      </div>\n      <div class=\"bar-wrap\"><div id=\"harpe-bar\" class=\"bar-fill\" style=\"width: 72%\"></div></div>\n      <div class=\"row mono\">\n        <span id=\"harpe-summary\">Effective: 56 tokens | Consumed: 42 tokens (75.0%)</span>\n        <button id=\"btn-repack\" class=\"btn\">Re-Pack via MCP</button>\n      </div>\n      <div class=\"mono\" style=\"margin-top:4px\">Policy Digest: <span id=\"harpe-digest\">sha256:8f9c...</span></div>\n      <div id=\"harpe-items\" class=\"item-list\"></div>\n    </div>\n  </div>\n\n  <!-- TAB 2: KIBISIS -->\n  <div id=\"panel-kibisis\" class=\"panel hidden\">\n    <div class=\"card\">\n      <div class=\"row\">\n        <strong>Epistemic Vault &amp; Conflict Resolution</strong>\n        <button id=\"btn-recall\" class=\"btn\">Resolve Conflicts via MCP</button>\n      </div>\n      <div class=\"mono\" id=\"kibisis-meta\">Scope: default | Active Filter: verified + candidate (revoked &amp; superseded excluded)</div>\n      <div id=\"kibisis-items\" class=\"item-list\"></div>\n      <pre id=\"kibisis-envelope\" class=\"mono\" style=\"background:#080c14;padding:8px;border-radius:5px;border:1px solid var(--border);margin-top:8px;white-space:pre-wrap;\"></pre>\n    </div>\n  </div>\n\n  <!-- TAB 3: ARGUS -->\n  <div id=\"panel-argus\" class=\"panel hidden\">\n    <div class=\"card\">\n      <div class=\"row\">\n        <strong>RFC 8785 Canonical JSON SHA-256 Audit Chain</strong>\n        <div style=\"display:flex;gap:6px;\">\n          <button id=\"btn-tamper\" class=\"btn danger\">Simulate Mid-Chain Tamper</button>\n          <button id=\"btn-verify\" class=\"btn\">Verify Chain via MCP</button>\n        </div>\n      </div>\n      <div id=\"argus-banner\" class=\"badge ok\" style=\"display:inline-block;margin-bottom:8px;\">CHAIN VALID — 3/3 Events Cryptographically Verified from GENESIS</div>\n      <div id=\"argus-events\" class=\"item-list\"></div>\n    </div>\n  </div>\n\n<script type=\"module\">\n  // Default authoritative state\n  let state = {\n    \"harpe\": {\n      \"total_budget\": 3640,\n      \"effective_budget\": 56,\n      \"consumed_tokens\": 39,\n      \"pruned_tokens\": 46,\n      \"utilization_pct\": 69.64,\n      \"pinned_policy_digest\": \"cafe934dfa8d52cab4344dc561586dbd21abc66489654f54d38327e5dda5cbce\",\n      \"items\": [\n        {\n          \"id\": \"sys_invariants\",\n          \"content\": \"Enforce SQLCipher encryption and monotonic fencing tokens on every write.\",\n          \"role\": \"context\",\n          \"priority\": 0,\n          \"pinned\": true,\n          \"tokens\": 19,\n          \"status\": \"INCLUDED (PINNED)\"\n        },\n        {\n          \"id\": \"arch_decision\",\n          \"content\": \"Use the exact 0/1 knapsack DP for deterministic context packing under budget.\",\n          \"role\": \"context\",\n          \"priority\": 10,\n          \"pinned\": false,\n          \"tokens\": 20,\n          \"status\": \"INCLUDED (KNAPSACK)\"\n        },\n        {\n          \"id\": \"stale_scratch\",\n          \"content\": \"Verbose historical debug trace from the deprecated prototype build: retry loop dumps, allocator statistics and unfiltered request logs, kept for reference only and safe to drop first.\",\n          \"role\": \"context\",\n          \"priority\": 85,\n          \"pinned\": false,\n          \"tokens\": 46,\n          \"status\": \"PRUNED\"\n        }\n      ]\n    },\n    \"kibisis\": {\n      \"active_scope\": \"default\",\n      \"query\": \"SQLCipher encryption\",\n      \"records\": [\n        {\n          \"key\": \"db_engine_v1\",\n          \"category\": \"decision\",\n          \"content\": \"Use unencrypted SQLite for local storage.\",\n          \"epistemic_state\": \"verified\",\n          \"status\": \"SUPERSEDED\"\n        },\n        {\n          \"key\": \"db_engine_v2\",\n          \"category\": \"decision\",\n          \"content\": \"Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).\",\n          \"epistemic_state\": \"verified\",\n          \"supersedes_key\": \"db_engine_v1\",\n          \"status\": \"ACTIVE\"\n        },\n        {\n          \"key\": \"temp_override\",\n          \"category\": \"convention\",\n          \"content\": \"Allow plaintext fallback in production.\",\n          \"epistemic_state\": \"revoked\",\n          \"status\": \"TOMBSTONED (REVOKED)\"\n        }\n      ],\n      \"envelope\": \"\\u003ckibisis-recall trust=\\\"untrusted-stored-text\\\" scope=\\\"default\\\">\\n- [decision/db_engine_v2] (verified): Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).\\n\\u003c/kibisis-recall>\"\n    },\n    \"argus\": {\n      \"valid\": true,\n      \"total_events\": 3,\n      \"root_hash\": \"26fed160404022047c0fe2c7f18eb8f7f49f997d9bb59f27497b6d181aa36cfb\",\n      \"head_hash\": \"45c96d6dc40d04a44ac39b5a94709af7d402621e36eaa9780b16a5d844ceb78d\",\n      \"first_broken_sequence\": null,\n      \"first_broken_index\": null,\n      \"error_detail\": null,\n      \"anchor_prev_hash\": \"GENESIS\",\n      \"starts_at_genesis\": true,\n      \"events\": [\n        {\n          \"sequence\": 1,\n          \"event_id\": \"evt_0001\",\n          \"event_type\": \"kibisis.lease.acquire\",\n          \"actor\": \"worker-a\",\n          \"timestamp\": \"2026-11-04T00:00:01Z\",\n          \"payload\": {\n            \"fencing_token\": 1,\n            \"ttl_s\": 30\n          },\n          \"canonical_payload\": \"{\\\"fencing_token\\\":1,\\\"ttl_s\\\":30}\",\n          \"prev_hash\": \"GENESIS\",\n          \"event_hash\": \"26fed160404022047c0fe2c7f18eb8f7f49f997d9bb59f27497b6d181aa36cfb\"\n        },\n        {\n          \"sequence\": 2,\n          \"event_id\": \"evt_0002\",\n          \"event_type\": \"harpe.context.pack\",\n          \"actor\": \"worker-a\",\n          \"timestamp\": \"2026-11-04T00:00:02Z\",\n          \"payload\": {\n            \"consumed_tokens\": 39,\n            \"savings_bp\": 5412\n          },\n          \"canonical_payload\": \"{\\\"consumed_tokens\\\":39,\\\"savings_bp\\\":5412}\",\n          \"prev_hash\": \"26fed160404022047c0fe2c7f18eb8f7f49f997d9bb59f27497b6d181aa36cfb\",\n          \"event_hash\": \"7a1e08b1b554f402a2698e45cc9587eed3cc6e4555c56e796c2b005f943efc9e\"\n        },\n        {\n          \"sequence\": 3,\n          \"event_id\": \"evt_0003\",\n          \"event_type\": \"kibisis.vault.write\",\n          \"actor\": \"worker-a\",\n          \"timestamp\": \"2026-11-04T00:00:03Z\",\n          \"payload\": {\n            \"fencing_token\": 1,\n            \"key\": \"db_engine_v2\"\n          },\n          \"canonical_payload\": \"{\\\"fencing_token\\\":1,\\\"key\\\":\\\"db_engine_v2\\\"}\",\n          \"prev_hash\": \"7a1e08b1b554f402a2698e45cc9587eed3cc6e4555c56e796c2b005f943efc9e\",\n          \"event_hash\": \"45c96d6dc40d04a44ac39b5a94709af7d402621e36eaa9780b16a5d844ceb78d\"\n        }\n      ]\n    }\n  };\n\n  // Tab switching\n  document.querySelectorAll(\".tab\").forEach(btn => {\n    btn.addEventListener(\"click\", () => {\n      document.querySelectorAll(\".tab\").forEach(b => b.classList.remove(\"active\"));\n      document.querySelectorAll(\".panel\").forEach(p => p.classList.add(\"hidden\"));\n      btn.classList.add(\"active\");\n      document.getElementById(\"panel-\" + btn.dataset.tab).classList.remove(\"hidden\");\n    });\n  });\n\n  // Tool output is data, never markup: every value placed into innerHTML goes through esc().\n  const ESC_MAP = { \"&\": \"&amp;\", \"<\": \"&lt;\", \">\": \"&gt;\", '\"': \"&quot;\", \"'\": \"&#x27;\", \"`\": \"&#x60;\" };\n  function esc(value) {\n    return String(value ?? \"\").replace(/[&<>\"'`]/g, ch => ESC_MAP[ch]);\n  }\n\n  // JSON-RPC 2.0 MCP Apps postMessage bridge\n  let rpcId = 1;\n  const pending = new Map();\n\n  window.addEventListener(\"message\", (ev) => {\n    if (ev.source !== window.parent) return; // only the host frame speaks on this bridge\n    const msg = ev.data;\n    if (!msg || typeof msg !== \"object\") return;\n    if (msg.id && pending.has(msg.id)) {\n      const { resolve } = pending.get(msg.id);\n      pending.delete(msg.id);\n      resolve(msg.result || msg.error);\n      return;\n    }\n    if (msg.method === \"ui/notifications/tool-result\" && msg.params?.structuredContent) {\n      applyServerPayload(msg.params.structuredContent);\n    }\n  });\n\n  function sendRpc(method, params) {\n    return new Promise((resolve) => {\n      const id = rpcId++;\n      pending.set(id, { resolve });\n      window.parent.postMessage({ jsonrpc: \"2.0\", id, method, params }, \"*\");\n      setTimeout(() => {\n        if (pending.has(id)) {\n          pending.delete(id);\n          resolve(null);\n        }\n      }, 2500);\n    });\n  }\n\n  async function callMcpTool(name, args) {\n    const statusBadge = document.getElementById(\"status-badge\");\n    statusBadge.textContent = \"Calling \" + name + \"…\";\n    statusBadge.className = \"badge warn\";\n    if (window.openai?.callTool) {\n      try {\n        const res = await window.openai.callTool(name, args);\n        if (res?.structuredContent) applyServerPayload(res.structuredContent);\n        statusBadge.textContent = \"MCP Synced\";\n        statusBadge.className = \"badge ok\";\n        return res;\n      } catch (_) {}\n    }\n    const rpcRes = await sendRpc(\"tools/call\", { name, arguments: args });\n    if (rpcRes?.structuredContent) {\n      applyServerPayload(rpcRes.structuredContent);\n      statusBadge.textContent = \"MCP Synced\";\n      statusBadge.className = \"badge ok\";\n      return rpcRes;\n    }\n    // Direct fallback to https://telarch.ai/mcp when running standalone\n    try {\n      const r = await fetch(\"https://telarch.ai/mcp\", {\n        method: \"POST\",\n        headers: { \"Content-Type\": \"application/json\" },\n        body: JSON.stringify({ jsonrpc: \"2.0\", id: rpcId++, method: \"tools/call\", params: { name, arguments: args } })\n      });\n      const j = await r.json();\n      if (j?.result?.structuredContent) {\n        applyServerPayload(j.result.structuredContent);\n        statusBadge.textContent = \"MCP Synced\";\n        statusBadge.className = \"badge ok\";\n      } else {\n        statusBadge.textContent = \"Call refused\";\n        statusBadge.className = \"badge warn\";\n      }\n    } catch (_) {\n      statusBadge.textContent = \"Local Preview\";\n      statusBadge.className = \"badge ok\";\n    }\n  }\n\n  function applyServerPayload(sc) {\n    if (!sc) return;\n    if (sc.harpe) state.harpe = sc.harpe;\n    if (sc.kibisis) state.kibisis = sc.kibisis;\n    if (sc.argus) state.argus = sc.argus;\n    if (sc.policy_applied && sc.included_items) {\n      state.harpe = {\n        total_budget: sc.total_budget,\n        effective_budget: sc.effective_budget,\n        consumed_tokens: sc.consumed_tokens,\n        pruned_tokens: sc.pruned_tokens,\n        utilization_pct: sc.utilization_pct,\n        pinned_policy_digest: sc.pinned_policy_digest,\n        items: [\n          ...sc.included_items.map(i => ({ ...i, status: i.pinned ? \"INCLUDED (PINNED)\" : \"INCLUDED (KNAPSACK)\" })),\n          ...sc.pruned_items.map(i => ({ ...i, status: \"PRUNED\" }))\n        ]\n      };\n    }\n    if (sc.envelope && sc.resolved_records) {\n      state.kibisis = {\n        active_scope: sc.active_scope,\n        query: sc.query,\n        records: sc.all_records_trace || sc.resolved_records,\n        envelope: sc.envelope\n      };\n    }\n    if (typeof sc.valid === \"boolean\" && sc.events) {\n      state.argus = sc;\n    }\n    render();\n  }\n\n  function render() {\n    // Render Harpe\n    const h = state.harpe;\n    document.getElementById(\"budget-val\").textContent = h.total_budget;\n    const pct = Math.min(100, Math.max(0, h.utilization_pct || 0));\n    document.getElementById(\"harpe-bar\").style.width = pct + \"%\";\n    document.getElementById(\"harpe-summary\").textContent =\n      `Effective: ${h.effective_budget} tok | Consumed: ${h.consumed_tokens} tok (${pct.toFixed(1)}%) | Pruned: ${h.pruned_tokens} tok`;\n    document.getElementById(\"harpe-digest\").textContent = \"sha256:\" + String(h.pinned_policy_digest).slice(0, 24) + \"…\";\n    const hList = document.getElementById(\"harpe-items\");\n    hList.innerHTML = \"\";\n    (h.items || []).forEach(it => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const status = String(it.status ?? \"\");\n      const cls = status.startsWith(\"INCLUDED\") ? \"ok\" : \"warn\";\n      div.innerHTML = `<div><strong>${esc(it.id)}</strong> (prio ${esc(it.priority)}, ${esc(it.tokens ?? \"?\")} tok)<div class=\"mono\">${esc(it.content)}</div></div><span class=\"badge ${cls}\">${esc(status)}</span>`;\n      hList.appendChild(div);\n    });\n\n    // Render Kibisis\n    const k = state.kibisis;\n    const kList = document.getElementById(\"kibisis-items\");\n    kList.innerHTML = \"\";\n    (k.records || []).forEach(rec => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const status = String(rec.status ?? \"\");\n      const cls = status === \"ACTIVE\" ? \"ok\" : (status.includes(\"TOMBSTONE\") ? \"err\" : \"warn\");\n      div.innerHTML = `<div><strong>${esc(rec.category)}/${esc(rec.key)}</strong> [${esc(rec.epistemic_state)}]<div class=\"mono\">${esc(rec.content)}</div></div><span class=\"badge ${cls}\">${esc(status)}</span>`;\n      kList.appendChild(div);\n    });\n    document.getElementById(\"kibisis-envelope\").textContent = k.envelope || \"\";\n\n    // Render Argus\n    const a = state.argus;\n    const banner = document.getElementById(\"argus-banner\");\n    if (a.valid) {\n      banner.className = \"badge ok\";\n      banner.textContent = `CHAIN VALID — ${a.events.length}/${a.events.length} Events Verified from ${a.starts_at_genesis === false ? \"the supplied anchor\" : \"GENESIS\"} (Head: ${String(a.head_hash || \"\").slice(0, 16)}…)`;\n    } else {\n      banner.className = \"badge err\";\n      banner.textContent = `CHAIN BROKEN AT ${a.first_broken_sequence == null ? \"EVENT INDEX \" + a.first_broken_index : \"SEQ #\" + a.first_broken_sequence}: ${a.error_detail}`;\n    }\n    const aList = document.getElementById(\"argus-events\");\n    aList.innerHTML = \"\";\n    (a.events || []).forEach((ev, evIndex) => {\n      if (!ev || typeof ev !== \"object\") return;\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const broken = !a.valid && (a.first_broken_index === undefined ? a.first_broken_sequence === ev.sequence : a.first_broken_index === evIndex);\n      div.innerHTML = `<div><strong>#${esc(ev.sequence)} ${esc(ev.event_type)}</strong> (${esc(ev.actor)})<div class=\"mono\">payload: ${esc(JSON.stringify(ev.payload))}</div><div class=\"mono\">prev: ${esc(String(ev.prev_hash).slice(0,16))}… → hash: ${esc(String(ev.event_hash).slice(0,16))}…</div></div><span class=\"badge ${broken ? 'err' : 'ok'}\">${broken ? 'BROKEN HERE' : 'SEALED'}</span>`;\n      aList.appendChild(div);\n    });\n  }\n\n  document.getElementById(\"budget-slider\").addEventListener(\"input\", (e) => {\n    document.getElementById(\"budget-val\").textContent = e.target.value;\n  });\n\n  document.getElementById(\"btn-repack\").addEventListener(\"click\", () => {\n    const totalBudget = parseInt(document.getElementById(\"budget-slider\").value, 10);\n    callMcpTool(\"harpe_synthesize_context\", {\n      total_budget: totalBudget,\n      policy: \"knapsack_dp\",\n      items: [\n        {\n          \"id\": \"sys_invariants\",\n          \"content\": \"Enforce SQLCipher encryption and monotonic fencing tokens on every write.\",\n          \"priority\": 0,\n          \"pinned\": true\n        },\n        {\n          \"id\": \"arch_decision\",\n          \"content\": \"Use the exact 0/1 knapsack DP for deterministic context packing under budget.\",\n          \"priority\": 10,\n          \"pinned\": false\n        },\n        {\n          \"id\": \"stale_scratch\",\n          \"content\": \"Verbose historical debug trace from the deprecated prototype build: retry loop dumps, allocator statistics and unfiltered request logs, kept for reference only and safe to drop first.\",\n          \"priority\": 85,\n          \"pinned\": false\n        }\n      ]\n    });\n  });\n\n  document.getElementById(\"btn-recall\").addEventListener(\"click\", () => {\n    callMcpTool(\"kibisis_resolve_memory\", {\n      active_scope: \"default\",\n      requested_scope: \"default\",\n      query: \"SQLCipher encryption\",\n      records: (state.kibisis.records || []).map(r => {\n        const rec = { key: r.key, category: r.category, content: r.content, epistemic_state: r.epistemic_state };\n        if (typeof r.supersedes_key === \"string\") rec.supersedes_key = r.supersedes_key;\n        return rec;\n      })\n    });\n  });\n\n  document.getElementById(\"btn-tamper\").addEventListener(\"click\", () => {\n    const tampered = JSON.parse(JSON.stringify(state.argus.events));\n    if (tampered.length >= 2) {\n      tampered[1].payload.savings_bp = 9999; // Mutate payload without re-sealing hash chain\n    }\n    callMcpTool(\"argus_audit_verify\", { events: tampered });\n  });\n\n  document.getElementById(\"btn-verify\").addEventListener(\"click\", () => {\n    callMcpTool(\"argus_audit_seal\", {\n      events: [\n        { event_type: \"kibisis.lease.acquire\", actor: \"worker-a\", payload: { fencing_token: 1, ttl_s: 30 }, timestamp: \"2026-11-04T00:00:01Z\" },\n        { event_type: \"harpe.context.pack\", actor: \"worker-a\", payload: { consumed_tokens: 34, savings_bp: 6540 }, timestamp: \"2026-11-04T00:00:02Z\" },\n        { event_type: \"kibisis.vault.write\", actor: \"worker-a\", payload: { fencing_token: 1, key: \"db_engine_v2\" }, timestamp: \"2026-11-04T00:00:03Z\" }\n      ]\n    });\n  });\n\n  // Initialize bridge & render\n  if (window.openai?.toolOutput) {\n    applyServerPayload(window.openai.toolOutput);\n  } else {\n    render();\n  }\n  sendRpc(\"ui/initialize\", {\n    protocolVersion: \"2025-06-18\",\n    appInfo: { name: \"Telarch Inspector\", version: \"0.1.0\" },\n    appCapabilities: {}\n  }).then(() => {\n    window.parent.postMessage({ jsonrpc: \"2.0\", method: \"ui/notifications/initialized\", params: {} }, \"*\");\n  });\n</script>\n</body>\n</html>";

// ---------------------------------------------------------------------------------------------------------
// Stated limits. A call above one of them is refused with an error that names the limit; nothing is
// silently capped or truncated.
// ---------------------------------------------------------------------------------------------------------
const TELARCH_LIMITS = {
  max_body_bytes: 1048576,          // one POST body
  max_json_depth: 64,               // nesting depth of a request body, and of a payload that is hashed
  max_batch_messages: 16,           // JSON-RPC messages in one batch (protocol revisions before 2025-06-18)
  max_items: 4096,                  // harpe items, kibisis records, argus events per call
  max_knapsack_cells: 4000000,      // (unpinned items that fit) x (capacity / gcd(token counts) + 1)
  max_token_value: 2147483647       // any token quantity in a budget
};

// A refusal the caller caused and can correct. Its message is written here, never taken from the runtime.
class TelarchRefusal extends Error {
  constructor(message) {
    super(message);
    this.name = "TelarchRefusal";
  }
}

// What Python's str.isspace() accepts, so token counts agree with the harpe library.
const HARPE_PIECE_RE = /[A-Za-z0-9_]+|[^\t\n\v\f\r\x1c-\x1f \x85\xa0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/gu;
const HARPE_HEX_RUN_RE = /[0-9a-fA-F]{8,}/g;

// Token estimate of harpe 0.1.0a13 HeuristicTokenCounter: the larger of (pieces + hex extras) and a quarter of
// the code points, rounded up. A piece is a run of ASCII letters, digits and underscores, or one other
// non-whitespace code point. Every run of 8 or more hex digits adds floor(length / 3).
function countTokens(text) {
  const s = typeof text === "string" ? text : "";
  if (!s) return 0;
  const pieces = s.match(HARPE_PIECE_RE) || [];
  let extras = 0;
  for (const piece of pieces) {
    if (piece.length >= 8) {
      const runs = piece.match(HARPE_HEX_RUN_RE);
      if (runs) {
        for (const run of runs) extras += Math.floor(run.length / 3);
      }
    }
  }
  let codePoints = 0;
  for (const _ch of s) codePoints++;
  return Math.max(pieces.length + extras, Math.floor((codePoints + 3) / 4));
}

// WebCrypto SHA-256 hex digest
async function sha256Hex(input) {
  const bytes = new TextEncoder().encode(String(input));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, "0")).join("");
}

// RFC 8785 (JCS) canonical JSON serializer for the subset Argus admits: null, booleans, strings, arrays, objects
// and integers inside the IEEE-754 safe range. A fraction, or an integer that JSON.parse can no longer tell from
// its neighbours (beyond 2**53 - 1), is refused: two different payloads must never serialize to one string.
function canonicalizeJson(val, path = "payload", depth = 0) {
  if (depth > TELARCH_LIMITS.max_json_depth) {
    throw new TelarchRefusal(`PayloadTooDeepError at ${path}: nested deeper than the limit max_json_depth=${TELARCH_LIMITS.max_json_depth}.`);
  }
  if (val === null) return "null";
  const t = typeof val;
  if (t === "boolean") return val ? "true" : "false";
  if (t === "number") {
    if (!Number.isFinite(val) || !Number.isInteger(val)) {
      throw new TelarchRefusal(`FloatPayloadError at ${path}: a non-integer number is rejected for canonical SHA-256 hashing; express fractions as integer basis points (*_bp).`);
    }
    if (!Number.isSafeInteger(val)) {
      throw new TelarchRefusal(`UnsafeIntegerError at ${path}: integers beyond +/-9007199254740991 (2**53 - 1) cannot be hashed exactly; send them as strings.`);
    }
    return String(val);
  }
  if (t === "string") return JSON.stringify(val);
  if (Array.isArray(val)) {
    return "[" + val.map((item, idx) => canonicalizeJson(item, `${path}[${idx}]`, depth + 1)).join(",") + "]";
  }
  if (t === "object") {
    const keys = Object.keys(val).sort();
    return "{" + keys.map(k => JSON.stringify(k) + ":" + canonicalizeJson(val[k], `${path}.${k}`, depth + 1)).join(",") + "}";
  }
  throw new TelarchRefusal(`UnsupportedPayloadError at ${path}: only JSON values can be hashed.`);
}

// Order of Python str comparison (by code point), which differs from JavaScript's (by UTF-16 unit).
function compareCodePoints(a, b) {
  const ia = a[Symbol.iterator]();
  const ib = b[Symbol.iterator]();
  for (;;) {
    const ra = ia.next();
    const rb = ib.next();
    if (ra.done || rb.done) return ra.done === rb.done ? 0 : (ra.done ? -1 : 1);
    const ca = ra.value.codePointAt(0);
    const cb = rb.value.codePointAt(0);
    if (ca !== cb) return ca < cb ? -1 : 1;
  }
}

function harpeDigestField(value) {
  return String(value).replace(/\\/g, "\\\\").replace(/:/g, "\\:").replace(/\n/g, "\\n");
}

// harpe.engine.pinned_policy_digest for items that carry no dimension: sha256 over one record per never-pruned
// item, "role:None:id:content\n", sorted by (role, id); "empty_policy" when nothing is pinned.
async function harpePinnedPolicyDigest(pinnedItems) {
  if (pinnedItems.length === 0) return "empty_policy";
  const ordered = [...pinnedItems].sort((a, b) => compareCodePoints(a.role, b.role) || compareCodePoints(a.id, b.id));
  let text = "";
  for (const it of ordered) {
    text += harpeDigestField(it.role) + ":None:" + harpeDigestField(it.id) + ":" + harpeDigestField(it.content) + "\n";
  }
  return sha256Hex(text);
}

function gcdInt(a, b) {
  while (b !== 0) {
    const t = a % b;
    a = b;
    b = t;
  }
  return a;
}

// Python round(x, 2) for x >= 0: toFixed rounds an exact tie up, Python rounds it to even.
function roundHalfEven2(x) {
  const eighths = x * 8;
  if (Number.isInteger(eighths) && eighths % 2 !== 0 && Math.abs(x) < 1e12) {
    const lower = Math.floor(x * 100);
    return (lower % 2 === 0 ? lower : lower + 1) / 100;
  }
  return Number(x.toFixed(2));
}

function harpeAvailable(args) {
  const totalBudget = args.total_budget;
  const reservedCompletion = args.reserved_completion ?? 2048;
  const reservedTools = args.reserved_tools ?? 1024;
  const safetyMargin = args.safety_margin ?? 512;
  return Math.max(0, totalBudget - reservedCompletion - reservedTools - safetyMargin);
}

function runHarpeBudget(args) {
  const avail = harpeAvailable(args);
  const used = args.current_usage ?? 0;
  return {
    total_budget: args.total_budget,
    available_context: avail,
    current_usage: used,
    utilization_pct: avail > 0 ? roundHalfEven2((used / avail) * 100) : 100,
    is_exceeded: used > avail
  };
}

function harpeTakeInOrder(ordered, capacity) {
  const taken = new Set();
  let left = capacity;
  for (const it of ordered) {
    if (it.tokens <= left) {
      taken.add(it);
      left -= it.tokens;
    }
  }
  return taken;
}

// Utility harpe gives an item that has no relevance metadata and is as recent as the reference time:
// 100 * (0.5 * (100 - priority) / 100 + 0.3 * 0.5 + 0.2 * 1.0), never below 0.01. Lower priority number = more useful.
function harpeUtility(priority) {
  const rrf = Math.max(0.0, (100.0 - priority) / 100.0);
  const utility = 100.0 * (0.50 * rrf + 0.30 * 0.5 + 0.20 * 1.0);
  return Math.max(0.01, utility);
}

// Exact 0/1 knapsack as harpe solves it: weights max(1, tokens); items heavier than the capacity are left out;
// weights and capacity are divided by their common divisor; one-row DP over float utilities in input order,
// an item recorded as taken only where it strictly improves the cell (ties go to the earlier item).
function harpeKnapsack(items, capacity) {
  const taken = new Set();
  const n = items.length;
  if (n === 0 || capacity <= 0) return taken;
  const weights = items.map(it => Math.max(1, it.tokens));
  const fit = [];
  for (let i = 0; i < n; i++) {
    if (weights[i] <= capacity) fit.push(i);
  }
  if (fit.length === 0) return taken;
  let fitTotal = 0;
  let divisor = 0;
  for (const i of fit) {
    fitTotal += weights[i];
    divisor = gcdInt(divisor, weights[i]);
  }
  if (fitTotal <= capacity) {
    // Everything that fits alone also fits together; with positive utilities that is the optimum.
    for (const i of fit) taken.add(items[i]);
    return taken;
  }
  const cap = Math.floor(capacity / divisor);
  const width = cap + 1;
  const cells = fit.length * width;
  if (cells > TELARCH_LIMITS.max_knapsack_cells) {
    throw new TelarchRefusal(
      `KnapsackTooLargeError: ${fit.length} candidate items x (capacity ${capacity} / common divisor ${divisor} + 1) = ${cells} cells, ` +
      `above the limit max_knapsack_cells=${TELARCH_LIMITS.max_knapsack_cells}. Nothing was packed. ` +
      "Send fewer items, a smaller budget, or use policy lowest_priority, fifo or warm_prefix."
    );
  }
  const dp = new Float64Array(width);
  const keep = new Int32Array(Math.ceil(cells / 32));
  for (let k = 0; k < fit.length; k++) {
    const w = weights[fit[k]] / divisor;
    const u = harpeUtility(items[fit[k]].priority);
    const base = k * width;
    for (let c = cap; c >= w; c--) {
      const cand = dp[c - w] + u;
      if (cand > dp[c]) {
        dp[c] = cand;
        const bit = base + c;
        keep[bit >>> 5] |= 1 << (bit & 31);
      }
    }
  }
  let c = cap;
  for (let k = fit.length - 1; k >= 0; k--) {
    const bit = k * width + c;
    if (keep[bit >>> 5] & (1 << (bit & 31))) {
      taken.add(items[fit[k]]);
      c -= weights[fit[k]] / divisor;
    }
  }
  return taken;
}

// Which prunable items stay, per policy, as harpe 0.1.0a13 decides it. `index` is the position in the caller's
// list and stands for arrival time: the first item is the oldest.
function harpeSelect(policy, unpinned, capacity) {
  if (policy === "lowest_priority") {
    const ordered = [...unpinned].sort((a, b) => (a.priority - b.priority) || (b.index - a.index));
    return harpeTakeInOrder(ordered, capacity);
  }
  if (policy === "fifo") {
    return harpeTakeInOrder([...unpinned].sort((a, b) => b.index - a.index), capacity);
  }
  if (policy === "warm_prefix") {
    const taken = new Set();
    const prefixBudget = Math.floor(capacity / 2);
    let prefixTokens = 0;
    let head = 0;
    while (head < unpinned.length && prefixTokens + unpinned[head].tokens <= prefixBudget) {
      taken.add(unpinned[head]);
      prefixTokens += unpinned[head].tokens;
      head++;
    }
    let tailTokens = 0;
    let tail = unpinned.length - 1;
    while (tail >= head && tailTokens + unpinned[tail].tokens <= capacity - prefixTokens) {
      taken.add(unpinned[tail]);
      tailTokens += unpinned[tail].tokens;
      tail--;
    }
    return taken;
  }
  if (policy === "knapsack_dp") {
    return harpeKnapsack(unpinned, capacity);
  }
  throw new TelarchRefusal(`UnknownPolicyError: policy must be one of ${HARPE_POLICIES.join(", ")}.`);
}

const HARPE_POLICIES = ["knapsack_dp", "lowest_priority", "fifo", "warm_prefix"];

// Context synthesizer with the semantics of harpe 0.1.0a13 ContextBudgetEngine.synthesize (Harpe)
async function runHarpeSynthesize(args) {
  const totalBudget = args.total_budget;
  const policy = args.policy ?? "knapsack_dp";
  const effectiveBudget = harpeAvailable(args);

  const seen = new Set();
  const items = args.items.map((it, index) => {
    if (seen.has(it.id)) {
      throw new TelarchRefusal(`DuplicateItemIdError: item id ${JSON.stringify(it.id)} occurs more than once; ids must be unique.`);
    }
    seen.add(it.id);
    return {
      id: it.id,
      content: it.content,
      role: it.role ?? "context",
      priority: it.priority ?? 50,
      pinned: it.pinned ?? false,
      tokens: countTokens(it.content),
      index
    };
  });

  // Pinned and priority-0 items are never pruned, even when they alone exceed the budget.
  const neverPruned = items.filter(i => i.pinned || i.priority === 0);
  const unpinned = items.filter(i => !(i.pinned || i.priority === 0));
  const pinnedTokens = neverPruned.reduce((acc, i) => acc + i.tokens, 0);
  const controlOverflow = pinnedTokens > effectiveBudget;

  let kept = new Set(neverPruned);
  let overflowTokens = 0;
  if (pinnedTokens >= effectiveBudget) {
    overflowTokens = pinnedTokens - effectiveBudget;
  } else {
    for (const it of harpeSelect(policy, unpinned, effectiveBudget - pinnedTokens)) kept.add(it);
  }

  const publicItem = ({ index, ...rest }) => rest;
  const includedItems = items.filter(i => kept.has(i)).map(publicItem);
  const prunedItems = items.filter(i => !kept.has(i)).map(publicItem);
  const consumedTokens = includedItems.reduce((acc, i) => acc + i.tokens, 0);
  const prunedTokens = prunedItems.reduce((acc, i) => acc + i.tokens, 0);
  const totalCandidateTokens = consumedTokens + prunedTokens;
  const tokensSavedBp = totalCandidateTokens > 0 ? Math.round((prunedTokens / totalCandidateTokens) * 10000) : 0;
  const utilizationPct = effectiveBudget > 0 ? Number(((consumedTokens / effectiveBudget) * 100).toFixed(2)) : 0;

  return {
    policy_applied: policy,
    total_budget: totalBudget,
    effective_budget: effectiveBudget,
    consumed_tokens: consumedTokens,
    pruned_tokens: prunedTokens,
    utilization_pct: utilizationPct,
    tokens_saved_bp: tokensSavedBp,
    control_overflow: controlOverflow,
    over_budget: overflowTokens > 0,
    overflow_tokens: overflowTokens,
    pinned_policy_digest: await harpePinnedPolicyDigest(neverPruned),
    included_ids: includedItems.map(i => i.id),
    pruned_ids: prunedItems.map(i => i.id),
    included_items: includedItems,
    pruned_items: prunedItems
  };
}

function escapeText(value) {
  return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeAttr(value) {
  return escapeText(value).replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
}

// Demonstration records: what kibisis_resolve_memory resolves when a call passes no `records` at all (the
// result then says records_source "demonstration"), and what telarch_open_inspector shows.
const KIBISIS_DEMO_RECORDS = [
  { key: "db_engine_v1", category: "decision", content: "Use unencrypted SQLite for local storage.", epistemic_state: "verified" },
  { key: "db_engine_v2", category: "decision", content: "Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).", epistemic_state: "verified", supersedes_key: "db_engine_v1" },
  { key: "temp_override", category: "convention", content: "Allow plaintext fallback in production.", epistemic_state: "revoked" }
];

// Epistemic memory resolver & conflict filter (Kibisis). Stateless: it works on the records of this one call.
function runKibisisResolve(args) {
  const activeScope = args.active_scope ?? "default";
  const requestedScope = args.requested_scope ?? activeScope;
  if (requestedScope !== activeScope) {
    throw new TelarchRefusal(`ScopeIsolationError: cross-scope memory access denied (requested_scope=${JSON.stringify(requestedScope)} != active_scope=${JSON.stringify(activeScope)}).`);
  }
  // Write gate, fail closed: only a write that names origin "user" may carry epistemic_state "verified".
  if (args.write_attempt !== undefined) {
    const attempt = args.write_attempt;
    if (attempt.epistemic_state === "verified" && attempt.origin !== "user") {
      throw new TelarchRefusal("EpistemicTrustViolation: model-originated writes cannot self-promote to epistemic_state='verified'; store as 'candidate' for human review.");
    }
  }

  const query = (args.query ?? "").toLowerCase().trim();
  const queryTerms = query.split(/\s+/).filter(Boolean);
  const recordsSource = args.records === undefined ? "demonstration" : "request";
  const records = (args.records ?? KIBISIS_DEMO_RECORDS).map(r => ({
    key: r.key,
    category: r.category ?? "decision",
    content: r.content,
    epistemic_state: r.epistemic_state ?? "candidate",
    supersedes_key: r.supersedes_key
  }));

  // A record supersedes another only if it is not revoked, does not name itself, and is verified whenever the
  // record it replaces is verified: a candidate, disputed or withdrawn record never displaces a verified one.
  const superseded = new Set();
  for (const r of records) {
    if (r.supersedes_key === undefined || r.supersedes_key === r.key || r.epistemic_state === "revoked") continue;
    for (const target of records) {
      if (target === r || target.key !== r.supersedes_key || target.epistemic_state === "revoked") continue;
      if (target.epistemic_state === "verified" && r.epistemic_state !== "verified") continue;
      superseded.add(target);
    }
  }

  const trace = [];
  const activeRecords = [];
  for (const r of records) {
    const { key, category, content } = r;
    const state = r.epistemic_state;
    const entry = { key, category, content, epistemic_state: state };
    if (r.supersedes_key !== undefined) entry.supersedes_key = r.supersedes_key;
    if (state === "revoked") {
      trace.push({ ...entry, status: "TOMBSTONED (REVOKED)" });
      continue;
    }
    if (superseded.has(r)) {
      trace.push({ ...entry, status: "SUPERSEDED" });
      continue;
    }
    const textLower = `${key} ${category} ${content}`.toLowerCase();
    const hits = queryTerms.length === 0 ? 1 : queryTerms.filter(t => textLower.includes(t)).length;
    if (hits > 0) {
      activeRecords.push({ key, category, content, epistemic_state: state, match_score: hits, status: "ACTIVE" });
    }
    trace.push({ ...entry, status: "ACTIVE" });
  }

  // Stored text is escaped, so no record and no scope name can close the envelope or add an attribute to it.
  const lines = activeRecords.map(r => `- [${escapeText(r.category)}/${escapeText(r.key)}] (${r.epistemic_state}): ${escapeText(r.content)}`);
  const envelope = `<kibisis-recall trust="untrusted-stored-text" scope="${escapeAttr(activeScope)}">\n` +
    (lines.length ? lines.join("\n") : "(no matching active records)") +
    `\n</kibisis-recall>`;

  return {
    active_scope: activeScope,
    query: args.query ?? "",
    resolved_count: activeRecords.length,
    resolved_records: activeRecords,
    all_records_trace: trace,
    records_source: recordsSource,
    envelope
  };
}

// Fencing-token check on the numbers of this one call (Kibisis). The worker keeps no lease table.
function runKibisisLease(args) {
  const token = args.fencing_token;
  const highest = args.highest_token_seen;
  const holder = JSON.stringify(args.holder_id);
  if (token < highest) {
    throw new TelarchRefusal(`StaleFencingTokenError: holder ${holder} presented fencing_token=${token} < highest_token_seen=${highest}. Split-brain write rejected.`);
  }
  if (args.lease_expires_epoch !== undefined) {
    if (args.now_epoch === undefined) {
      throw new TelarchRefusal("LeaseClockMissingError: lease_expires_epoch was given without now_epoch; expiry cannot be evaluated, so the write is not permitted.");
    }
    if (args.now_epoch >= args.lease_expires_epoch) {
      throw new TelarchRefusal(`LeaseExpiredError: holder ${holder} lease expired at ${args.lease_expires_epoch} (now=${args.now_epoch}). Write rejected.`);
    }
  }
  return {
    permitted: true,
    resource: args.resource ?? "vault:default",
    holder_id: args.holder_id,
    accepted_fencing_token: token,
    next_monotonic_token: token + 1
  };
}

const ARGUS_GENESIS = "GENESIS";
const ARGUS_HASH_RE = /^[0-9a-f]{64}$/;
const ARGUS_EVENT_FIELDS = ["sequence", "event_id", "event_type", "actor", "timestamp", "payload", "canonical_payload", "prev_hash", "event_hash"];

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function argusEnvelope(ev, prevHash) {
  return canonicalizeJson({
    actor: ev.actor,
    event_id: ev.event_id,
    event_type: ev.event_type,
    payload: ev.payload,
    prev_hash: prevHash,
    sequence: ev.sequence,
    timestamp: ev.timestamp
  }, "event");
}

// Argus canonical-JSON SHA-256 chain sealer. Stateless: it seals the events of this one call, chained from
// prev_hash (GENESIS unless the caller continues an earlier segment).
async function runArgusSeal(args) {
  const startHash = args.prev_hash ?? ARGUS_GENESIS;
  if (startHash !== ARGUS_GENESIS && !ARGUS_HASH_RE.test(startHash)) {
    throw new TelarchRefusal("PrevHashFormatError: prev_hash must be \"GENESIS\" or the 64 lowercase hex characters of the previous head_hash.");
  }
  if (startHash !== ARGUS_GENESIS && args.events[0].sequence === undefined) {
    throw new TelarchRefusal("SequenceRequiredError: a segment that continues an earlier chain (prev_hash is not GENESIS) must give `sequence` on its first event.");
  }
  let prevHash = startHash;
  let prevSeq = null;
  const sealed = [];
  for (let i = 0; i < args.events.length; i++) {
    const ev = args.events[i];
    const expectedSeq = prevSeq === null ? (ev.sequence ?? 1) : prevSeq + 1;
    if (ev.sequence !== undefined && ev.sequence !== expectedSeq) {
      throw new TelarchRefusal(`SequenceOrderError: events[${i}].sequence is ${ev.sequence} but the chain is linear and needs ${expectedSeq}; sequences rise by exactly one.`);
    }
    const seq = expectedSeq;
    const event = {
      sequence: seq,
      event_id: ev.event_id ?? `evt_${String(seq).padStart(4, "0")}`,
      event_type: ev.event_type,
      actor: ev.actor,
      // No timestamp is invented: an event the caller did not date is sealed with timestamp null.
      timestamp: ev.timestamp ?? null,
      payload: ev.payload
    };
    const canonicalPayload = canonicalizeJson(event.payload, `events[${i}].payload`);
    const eventHash = await sha256Hex(argusEnvelope(event, prevHash));
    sealed.push({ ...event, canonical_payload: canonicalPayload, prev_hash: prevHash, event_hash: eventHash });
    prevHash = eventHash;
    prevSeq = seq;
  }
  return {
    valid: true,
    total_events: sealed.length,
    root_hash: sealed[0].event_hash,
    head_hash: sealed[sealed.length - 1].event_hash,
    first_broken_sequence: null,
    first_broken_index: null,
    error_detail: null,
    anchor_prev_hash: startHash,
    starts_at_genesis: startHash === ARGUS_GENESIS,
    events: sealed
  };
}

// Why a supplied event cannot be a sealed Argus event, or null. Nothing is coerced or defaulted: a field that
// is missing or has another type than the sealer writes is a broken event, not a guess at what was meant.
function argusEventShapeError(ev) {
  if (!isPlainObject(ev)) return "event is not an object";
  for (const field of Object.keys(ev)) {
    if (!ARGUS_EVENT_FIELDS.includes(field)) return `field ${JSON.stringify(field)} is not part of a sealed event and is not covered by the hash`;
  }
  if (!Number.isSafeInteger(ev.sequence) || ev.sequence < 1) return "sequence is missing or is not a positive integer";
  for (const field of ["event_id", "event_type", "actor", "prev_hash", "event_hash"]) {
    if (typeof ev[field] !== "string") return `${field} is missing or is not a string`;
  }
  if (!("timestamp" in ev) || (ev.timestamp !== null && typeof ev.timestamp !== "string")) return "timestamp is missing or is neither a string nor null";
  if (!isPlainObject(ev.payload)) return "payload is missing or is not an object";
  if ("canonical_payload" in ev && typeof ev.canonical_payload !== "string") return "canonical_payload is not a string";
  return null;
}

// Verifies the chain passed in. It proves that these events are unaltered and linked to each other from
// `anchor_prev_hash`; it cannot know about events removed from the end, so the caller compares head_hash and
// total_events with values it trusts.
async function runArgusVerify(args) {
  const events = args.events;
  const first = events[0];
  const anchor = args.prev_hash ?? (isPlainObject(first) && typeof first.prev_hash === "string" ? first.prev_hash : ARGUS_GENESIS);
  const hashOf = ev => (isPlainObject(ev) && typeof ev.event_hash === "string" ? ev.event_hash : null);
  const broken = (index, detail) => {
    const seq = isPlainObject(events[index]) && Number.isSafeInteger(events[index].sequence) ? events[index].sequence : null;
    return {
      valid: false,
      total_events: events.length,
      root_hash: hashOf(first),
      head_hash: hashOf(events[events.length - 1]),
      first_broken_sequence: seq,
      first_broken_index: index,
      error_detail: detail,
      anchor_prev_hash: anchor,
      starts_at_genesis: anchor === ARGUS_GENESIS,
      events
    };
  };
  if (anchor !== ARGUS_GENESIS && !ARGUS_HASH_RE.test(anchor)) {
    return broken(0, "chain anchor is neither GENESIS nor a 64-character lowercase hex SHA-256 digest");
  }
  let expectedPrev = anchor;
  let prevSeq = null;
  for (let i = 0; i < events.length; i++) {
    const ev = events[i];
    const shapeError = argusEventShapeError(ev);
    if (shapeError) return broken(i, `malformed event at index ${i}: ${shapeError}`);
    const seq = ev.sequence;
    if (prevSeq !== null && seq !== prevSeq + 1) {
      return broken(i, `sequence break at index ${i}: expected ${prevSeq + 1}, found ${seq}`);
    }
    if (ev.prev_hash !== expectedPrev) {
      return broken(i, `prev_hash mismatch at sequence ${seq}: expected ${expectedPrev}, found ${ev.prev_hash}`);
    }
    let computedHash;
    try {
      if ("canonical_payload" in ev && ev.canonical_payload !== canonicalizeJson(ev.payload, `events[${i}].payload`)) {
        return broken(i, `canonical_payload at sequence ${seq} is not the canonical form of payload`);
      }
      computedHash = await sha256Hex(argusEnvelope(ev, expectedPrev));
    } catch (err) {
      if (err instanceof TelarchRefusal) return broken(i, `event at sequence ${seq} cannot be hashed: ${err.message}`);
      throw err;
    }
    if (ev.event_hash !== computedHash) {
      return broken(i, `SHA-256 digest mismatch at sequence ${seq}: recorded ${ev.event_hash}, computed ${computedHash}`);
    }
    expectedPrev = computedHash;
    prevSeq = seq;
  }
  return {
    valid: true,
    total_events: events.length,
    root_hash: events[0].event_hash,
    head_hash: events[events.length - 1].event_hash,
    first_broken_sequence: null,
    first_broken_index: null,
    error_detail: null,
    anchor_prev_hash: anchor,
    starts_at_genesis: anchor === ARGUS_GENESIS,
    events
  };
}

const TOKEN_QUANTITY = { type: "integer", minimum: 0, maximum: TELARCH_LIMITS.max_token_value };
const TOTAL_BUDGET = { type: "integer", minimum: 1, maximum: TELARCH_LIMITS.max_token_value };
const HARPE_ROLES = ["system", "user", "assistant", "tool", "context"];
const EPISTEMIC_STATES = ["candidate", "verified", "disputed", "revoked"];

const MCP_TOOLS = [
  {
    name: "harpe_synthesize_context",
    title: "Synthesize & Prune Context (0/1 Knapsack)",
    description: "Use this when you need to pack candidate context items deterministically into a strict token budget. Same selection as the harpe 0.1.0a13 library: the budget optimised against is total_budget minus the three reserves (returned as effective_budget); pinned items and priority-0 items are always kept; the rest are chosen by `policy`. Priority runs 0-100 and a LOWER number is MORE important. The position of an item in `items` is its age: first = oldest. Limits: at most 4096 items, and knapsack_dp is refused (nothing packed, error names max_knapsack_cells) when candidates x (capacity / common divisor of token counts + 1) exceeds 4,000,000. Token counts are a deterministic estimate, not a model tokenizer.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { ...TOTAL_BUDGET, description: "Total model context budget in tokens." },
        reserved_completion: { ...TOKEN_QUANTITY, description: "Tokens reserved for completion output.", default: 2048 },
        reserved_tools: { ...TOKEN_QUANTITY, description: "Tokens reserved for tool schemas.", default: 1024 },
        safety_margin: { ...TOKEN_QUANTITY, description: "Safety margin buffer in tokens.", default: 512 },
        policy: {
          type: "string",
          enum: HARPE_POLICIES,
          default: "knapsack_dp",
          description: "How unpinned items are chosen. knapsack_dp: exact 0/1 knapsack on utility (falls with the priority number). lowest_priority: lowest priority number first, newer first among equals, each taken if it still fits. fifo: newest first, each taken if it still fits. warm_prefix: oldest items up to half the capacity, then newest items into the rest."
        },
        items: {
          type: "array",
          maxItems: TELARCH_LIMITS.max_items,
          description: "Candidate context items to pack, oldest first. Ids must be unique.",
          items: {
            type: "object",
            properties: {
              id: { type: "string", minLength: 1 },
              content: { type: "string" },
              role: { type: "string", enum: HARPE_ROLES, default: "context" },
              priority: { type: "integer", minimum: 0, maximum: 100, default: 50, description: "0-100, lower = more important; 0 is never pruned." },
              pinned: { type: "boolean", default: false, description: "Kept even when the pinned items alone exceed the budget (then control_overflow is true)." }
            },
            required: ["id", "content"],
            additionalProperties: false
          }
        }
      },
      required: ["total_budget", "items"],
      additionalProperties: false
    },
    annotations: {
      title: "Synthesize & Prune Context",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      "openai/toolInvocation/invoking": "Solving 0/1 context knapsack…",
      "openai/toolInvocation/invoked": "Context packed within token budget."
    }
  },
  {
    name: "harpe_budget_evaluate",
    title: "Evaluate Token Budget & Margins",
    description: "Use this when you need to compute available context tokens, safety margin deductions, and utilization percentage for a model token window.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { ...TOTAL_BUDGET, description: "Total context window size in tokens." },
        reserved_completion: { ...TOKEN_QUANTITY, default: 2048 },
        reserved_tools: { ...TOKEN_QUANTITY, default: 1024 },
        safety_margin: { ...TOKEN_QUANTITY, default: 512 },
        current_usage: { ...TOKEN_QUANTITY, default: 0 }
      },
      required: ["total_budget"],
      additionalProperties: false
    },
    annotations: {
      title: "Evaluate Token Budget",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      "openai/toolInvocation/invoking": "Evaluating token window…",
      "openai/toolInvocation/invoked": "Token budget evaluated."
    }
  },
  {
    name: "kibisis_resolve_memory",
    title: "Resolve Epistemic Memory & Conflicts",
    description: "Use this to work out which of the memory records you pass in `records` are active: revoked records are tombstoned, superseded records are dropped (a record that is not verified never displaces a verified one), a requested scope other than the active scope is refused, and a write_attempt that claims epistemic_state 'verified' without origin 'user' is refused. Active records matching `query` are returned in a <kibisis-recall trust=\"untrusted-stored-text\"> envelope with markup characters escaped. Stateless: this server stores no memory. It resolves the records of this call; when `records` is left out it resolves three built-in demonstration records and the result says records_source \"demonstration\".",
    inputSchema: {
      type: "object",
      properties: {
        active_scope: { type: "string", default: "default", description: "Active workspace/tenant scope." },
        requested_scope: { type: "string", description: "Requested scope. Must equal active_scope; when omitted it is taken to be active_scope." },
        query: { type: "string", description: "Search keywords to match against active memory records. An empty string matches every active record." },
        write_attempt: {
          type: "object",
          description: "Optional write gate evaluation: refused unless origin is 'user' or epistemic_state is not 'verified'.",
          properties: {
            origin: { type: "string", enum: ["model", "user"] },
            epistemic_state: { type: "string", enum: EPISTEMIC_STATES }
          },
          required: ["origin", "epistemic_state"],
          additionalProperties: false
        },
        records: {
          type: "array",
          maxItems: TELARCH_LIMITS.max_items,
          description: "Memory records to resolve across supersession and revocation chains. Left out: three built-in demonstration records. An empty list resolves nothing.",
          items: {
            type: "object",
            properties: {
              key: { type: "string", minLength: 1 },
              category: { type: "string", default: "decision" },
              content: { type: "string" },
              epistemic_state: { type: "string", enum: EPISTEMIC_STATES, default: "candidate" },
              supersedes_key: { type: "string" }
            },
            required: ["key", "content"],
            additionalProperties: false
          }
        }
      },
      required: ["query"],
      additionalProperties: false
    },
    annotations: {
      title: "Resolve Epistemic Memory",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      "openai/toolInvocation/invoking": "Resolving epistemic memory state…",
      "openai/toolInvocation/invoked": "Memory conflicts resolved."
    }
  },
  {
    name: "kibisis_lease_evaluate",
    title: "Evaluate Monotonic Fencing Lease",
    description: "Use this to evaluate whether a concurrent agent holder's fencing token and lease expiry permit a vault mutation or must be rejected to prevent split-brain writes. It checks only the numbers of this call (this server keeps no lease table): a token below highest_token_seen is refused, an expired lease is refused, and lease_expires_epoch without now_epoch is refused.",
    inputSchema: {
      type: "object",
      properties: {
        resource: { type: "string", default: "vault:default" },
        holder_id: { type: "string", minLength: 1, description: "Agent worker identifier." },
        fencing_token: { type: "integer", minimum: 0, maximum: 9007199254740990, description: "Holder's fencing token." },
        highest_token_seen: { type: "integer", minimum: 0, maximum: 9007199254740991, description: "Highest monotonic fencing token recorded by the vault." },
        lease_expires_epoch: { type: "integer", description: "Lease expiration Unix timestamp (whole seconds). Needs now_epoch." },
        now_epoch: { type: "integer", description: "Current Unix timestamp (whole seconds)." }
      },
      required: ["holder_id", "fencing_token", "highest_token_seen"],
      additionalProperties: false
    },
    annotations: {
      title: "Evaluate Monotonic Fencing Lease",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      "openai/toolInvocation/invoking": "Checking monotonic fencing lease…",
      "openai/toolInvocation/invoked": "Fencing token evaluated."
    }
  },
  {
    name: "argus_audit_seal",
    title: "Seal RFC 8785 SHA-256 Audit Chain",
    description: "Use this to compute canonical RFC 8785 (JCS) JSON and linear SHA-256 hash-chain digests for a sequence of agent audit events, from GENESIS or from the head_hash of an earlier segment (prev_hash; then the first event must give its sequence). Sequences rise by exactly one. Rejects fractions (use integer basis points *_bp) and integers beyond +/-(2**53 - 1) (send them as strings). An event without a timestamp is sealed with timestamp null; no time is invented. Stateless: the sealed events are returned, not stored.",
    inputSchema: {
      type: "object",
      properties: {
        prev_hash: { type: "string", default: "GENESIS", description: "\"GENESIS\", or the 64 lowercase hex characters of the head_hash this segment continues." },
        events: {
          type: "array",
          minItems: 1,
          maxItems: TELARCH_LIMITS.max_items,
          items: {
            type: "object",
            properties: {
              sequence: { type: "integer", minimum: 1, maximum: TELARCH_LIMITS.max_token_value },
              event_id: { type: "string", minLength: 1 },
              event_type: { type: "string" },
              actor: { type: "string" },
              timestamp: { type: ["string", "null"] },
              payload: { type: "object" }
            },
            required: ["event_type", "actor", "payload"],
            additionalProperties: false
          }
        }
      },
      required: ["events"],
      additionalProperties: false
    },
    annotations: {
      title: "Seal SHA-256 Audit Chain",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      "openai/toolInvocation/invoking": "Sealing RFC 8785 SHA-256 hash chain…",
      "openai/toolInvocation/invoked": "Audit chain sealed."
    }
  },
  {
    name: "argus_audit_verify",
    title: "Verify SHA-256 Audit Ledger Continuity",
    description: "Use this to cryptographically verify a linear SHA-256 Argus audit chain and isolate the first event that is altered, malformed, out of sequence or unlinked. Pass the sealed events exactly as argus_audit_seal returned them; a missing or retyped field makes the chain invalid, nothing is defaulted. The result proves the listed events are unaltered and linked from anchor_prev_hash (starts_at_genesis says whether that is GENESIS). It cannot detect events removed from the end of the list: compare head_hash and total_events with values you already trust.",
    inputSchema: {
      type: "object",
      properties: {
        prev_hash: { type: "string", description: "Optional trusted anchor: the hash the first event must link to (\"GENESIS\" or a 64-character head_hash). When omitted the first event's own prev_hash is the anchor and is reported as anchor_prev_hash." },
        events: {
          type: "array",
          minItems: 1,
          maxItems: TELARCH_LIMITS.max_items,
          description: "Sealed events in order. Each needs sequence (positive integer), event_id, event_type, actor, prev_hash, event_hash (strings), timestamp (string or null) and payload (object); canonical_payload is checked when present. Defects inside an event are reported as valid:false, not as a call error.",
          items: { type: "object" }
        }
      },
      required: ["events"],
      additionalProperties: false
    },
    annotations: {
      title: "Verify SHA-256 Audit Chain",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      "openai/toolInvocation/invoking": "Verifying SHA-256 audit chain…",
      "openai/toolInvocation/invoked": "Audit chain verification complete."
    }
  },
  {
    name: "telarch_open_inspector",
    title: "Open Telarch Cognitive Infrastructure Inspector",
    description: "Render the interactive Telarch Inspector UI for exploring Harpe 0/1 knapsack token packing, Kibisis epistemic memory conflict resolution, and Argus SHA-256 audit chain verification. It shows built-in demonstration data, not stored data.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { ...TOTAL_BUDGET, default: 3640, description: "Initial token budget for the Harpe inspector tab." },
        query: { type: "string", default: "SQLCipher encryption", description: "Initial memory query for the Kibisis inspector tab." }
      },
      additionalProperties: false
    },
    annotations: {
      title: "Open Telarch Inspector UI",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    _meta: {
      ui: { resourceUri: INSPECTOR_URI },
      "openai/outputTemplate": INSPECTOR_URI,
      "openai/ui": {
        entrypoints: [{ type: "global" }, { type: "thread" }]
      },
      "openai/toolInvocation/invoking": "Launching Telarch Inspector…",
      "openai/toolInvocation/invoked": "Telarch Inspector active."
    }
  }
];

// Demonstration data of the inspector. Priorities follow harpe: 0-100, lower = more important.
const INSPECTOR_DEMO_ITEMS = [
  { id: "sys_invariants", content: "Enforce SQLCipher encryption and monotonic fencing tokens on every write.", priority: 0, pinned: true },
  { id: "arch_decision", content: "Use the exact 0/1 knapsack DP for deterministic context packing under budget.", priority: 10, pinned: false },
  { id: "stale_scratch", content: "Verbose historical debug trace from the deprecated prototype build: retry loop dumps, allocator statistics and unfiltered request logs, kept for reference only and safe to drop first.", priority: 85, pinned: false }
];

async function runInspector(args) {
  const harpeRes = await runHarpeSynthesize({
    total_budget: args.total_budget ?? 3640,
    policy: "knapsack_dp",
    items: INSPECTOR_DEMO_ITEMS
  });
  const kibisisRes = runKibisisResolve({
    active_scope: "default",
    requested_scope: "default",
    query: args.query ?? "SQLCipher encryption",
    records: KIBISIS_DEMO_RECORDS
  });
  const argusRes = await runArgusSeal({
    events: [
      { event_type: "kibisis.lease.acquire", actor: "worker-a", payload: { fencing_token: 1, ttl_s: 30 }, timestamp: "2026-11-04T00:00:01Z" },
      { event_type: "harpe.context.pack", actor: "worker-a", payload: { consumed_tokens: harpeRes.consumed_tokens, savings_bp: harpeRes.tokens_saved_bp }, timestamp: "2026-11-04T00:00:02Z" },
      { event_type: "kibisis.vault.write", actor: "worker-a", payload: { fencing_token: 1, key: "db_engine_v2" }, timestamp: "2026-11-04T00:00:03Z" }
    ]
  });
  return {
    status: "inspector_ready",
    harpe: {
      total_budget: harpeRes.total_budget,
      effective_budget: harpeRes.effective_budget,
      consumed_tokens: harpeRes.consumed_tokens,
      pruned_tokens: harpeRes.pruned_tokens,
      utilization_pct: harpeRes.utilization_pct,
      pinned_policy_digest: harpeRes.pinned_policy_digest,
      items: [
        ...harpeRes.included_items.map(i => ({ ...i, status: i.pinned ? "INCLUDED (PINNED)" : "INCLUDED (KNAPSACK)" })),
        ...harpeRes.pruned_items.map(i => ({ ...i, status: "PRUNED" }))
      ]
    },
    kibisis: {
      active_scope: kibisisRes.active_scope,
      query: kibisisRes.query,
      records: kibisisRes.all_records_trace,
      envelope: kibisisRes.envelope
    },
    argus: argusRes
  };
}

const MCP_TOOL_HANDLERS = {
  harpe_synthesize_context: runHarpeSynthesize,
  harpe_budget_evaluate: runHarpeBudget,
  kibisis_resolve_memory: runKibisisResolve,
  kibisis_lease_evaluate: runKibisisLease,
  argus_audit_seal: runArgusSeal,
  argus_audit_verify: runArgusVerify,
  telarch_open_inspector: runInspector
};

// ---------------------------------------------------------------------------------------------------------
// Argument validation: tools/call arguments are checked against the tool's own inputSchema before its handler
// runs. Supported keywords: type, enum, minimum, maximum, minLength, minItems, maxItems, items, properties,
// required, additionalProperties:false. Returns a sentence about the first violation, or null.
// ---------------------------------------------------------------------------------------------------------
function schemaTypeMatches(type, value) {
  switch (type) {
    case "object": return isPlainObject(value);
    case "array": return Array.isArray(value);
    case "string": return typeof value === "string";
    case "boolean": return typeof value === "boolean";
    case "integer": return typeof value === "number" && Number.isSafeInteger(value);
    case "number": return typeof value === "number" && Number.isFinite(value);
    case "null": return value === null;
    default: return false;
  }
}

function quoteName(name) {
  const text = JSON.stringify(String(name));
  return text.length > 82 ? text.slice(0, 80) + "…\"" : text;
}

function schemaViolation(schema, value, path) {
  if (schema.type !== undefined) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some(t => schemaTypeMatches(t, value))) {
      const wanted = types.map(t => (t === "integer" ? "an integer (whole number within +/-(2**53 - 1))" : (t === "null" ? "null" : `of type ${t}`))).join(" or ");
      return `${path} must be ${wanted}`;
    }
  }
  if (schema.enum !== undefined && !schema.enum.includes(value)) {
    return `${path} must be one of: ${schema.enum.join(", ")}`;
  }
  if (typeof value === "number") {
    if (schema.minimum !== undefined && value < schema.minimum) return `${path} must be >= ${schema.minimum}`;
    if (schema.maximum !== undefined && value > schema.maximum) return `${path} must be <= ${schema.maximum}`;
  } else if (typeof value === "string") {
    if (schema.minLength !== undefined && value.length < schema.minLength) return `${path} must have at least ${schema.minLength} character(s)`;
  } else if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) return `${path} must have at least ${schema.minItems} item(s)`;
    if (schema.maxItems !== undefined && value.length > schema.maxItems) return `${path} has ${value.length} items, above the limit of ${schema.maxItems}`;
    if (schema.items !== undefined) {
      for (let i = 0; i < value.length; i++) {
        const inner = schemaViolation(schema.items, value[i], `${path}[${i}]`);
        if (inner) return inner;
      }
    }
  } else if (isPlainObject(value)) {
    const properties = schema.properties || {};
    for (const name of schema.required || []) {
      if (!Object.hasOwn(value, name)) return `${path}.${name} is required`;
    }
    for (const name of Object.keys(value)) {
      if (Object.hasOwn(properties, name)) {
        const inner = schemaViolation(properties[name], value[name], `${path}.${name}`);
        if (inner) return inner;
      } else if (schema.additionalProperties === false) {
        return `${path} has no property ${quoteName(name)}`;
      }
    }
  }
  return null;
}

// ---------------------------------------------------------------------------------------------------------
// JSON-RPC 2.0 / MCP message handling. Returns the response object, or null when the message needs no reply
// (a notification, or a response posted by the client).
// ---------------------------------------------------------------------------------------------------------
const MCP_PROTOCOL_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18"];
const MCP_LATEST_PROTOCOL_VERSION = "2025-06-18";

const INSPECTOR_RESOURCE_META = () => ({
  ui: {
    prefersBorder: true,
    domain: "https://telarch.ai",
    csp: {
      connectDomains: ["https://telarch.ai"],
      resourceDomains: []
    }
  }
});

function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

function isRpcId(value) {
  return typeof value === "string" || (typeof value === "number" && Number.isFinite(value));
}

async function mcpToolsCall(id, params) {
  if (typeof params.name !== "string") {
    return rpcError(id, -32602, "Invalid params: tools/call needs a string `name`");
  }
  const name = params.name;
  const tool = MCP_TOOLS.find(t => t.name === name);
  if (!tool) {
    return rpcError(id, -32602, `Unknown tool: ${quoteName(name).slice(1, -1)}`);
  }
  const args = params.arguments === undefined ? {} : params.arguments;
  const violation = schemaViolation(tool.inputSchema, args, "arguments");
  if (violation) {
    return rpcError(id, -32602, `Invalid arguments for tool ${name}: ${violation}`);
  }
  let payload;
  try {
    payload = await MCP_TOOL_HANDLERS[name](args);
  } catch (err) {
    if (err instanceof TelarchRefusal) {
      return { jsonrpc: "2.0", id, result: { content: [{ type: "text", text: err.message }], isError: true } };
    }
    // The runtime's exception text stays on the server.
    return rpcError(id, -32603, `Internal error while running tool ${name}`);
  }
  return {
    jsonrpc: "2.0",
    id,
    result: {
      structuredContent: payload,
      content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
      isError: false
    }
  };
}

async function handleMcpRpcSingle(req) {
  if (!isPlainObject(req)) {
    return rpcError(null, -32600, "Invalid Request: a JSON-RPC message is an object");
  }
  const hasId = Object.hasOwn(req, "id");
  const idOk = hasId && isRpcId(req.id);
  const replyId = idOk ? req.id : null;
  if (req.jsonrpc !== "2.0") {
    return rpcError(replyId, -32600, "Invalid Request: `jsonrpc` must be \"2.0\"");
  }
  if (hasId && !idOk) {
    return rpcError(null, -32600, "Invalid Request: `id` must be a string or a number");
  }
  if (!Object.hasOwn(req, "method")) {
    // A response posted by the client (this server sends no requests, so there is nothing to match it to).
    if (hasId && (Object.hasOwn(req, "result") || Object.hasOwn(req, "error"))) return null;
    return rpcError(replyId, -32600, "Invalid Request: `method` is missing");
  }
  if (typeof req.method !== "string") {
    return rpcError(replyId, -32600, "Invalid Request: `method` must be a string");
  }
  // JSON-RPC notifications have no id and get no reply.
  if (!hasId) return null;

  const id = req.id;
  const method = req.method;
  if (Object.hasOwn(req, "params") && !isPlainObject(req.params)) {
    return rpcError(id, -32602, "Invalid params: `params` must be an object");
  }
  const params = req.params ?? {};

  if (method === "initialize") {
    if (params.protocolVersion !== undefined && typeof params.protocolVersion !== "string") {
      return rpcError(id, -32602, "Invalid params: `protocolVersion` must be a string");
    }
    const requestedVersion = params.protocolVersion ?? MCP_LATEST_PROTOCOL_VERSION;
    const protocolVersion = MCP_PROTOCOL_VERSIONS.includes(requestedVersion) ? requestedVersion : MCP_LATEST_PROTOCOL_VERSION;
    return {
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion,
        capabilities: {
          tools: { listChanged: false },
          resources: { subscribe: false, listChanged: false }
        },
        serverInfo: {
          name: "telarch-mcp",
          version: "0.1.0"
        },
        instructions: "Stateless tools; nothing is stored between calls. Use harpe_synthesize_context for 0/1 knapsack token packing (priority 0-100, lower = more important), kibisis_resolve_memory to resolve the memory records you pass in and frame them in an escaped <kibisis-recall> envelope, argus_audit_seal / argus_audit_verify for RFC 8785 SHA-256 audit chains (safe integers and strings only; no fractions), and telarch_open_inspector for interactive visualization of demonstration data. Arguments are checked against each tool's inputSchema; a call that does not match is refused."
      }
    };
  }

  if (method === "ping") {
    return { jsonrpc: "2.0", id, result: {} };
  }

  if (method === "tools/list") {
    return { jsonrpc: "2.0", id, result: { tools: MCP_TOOLS } };
  }

  if (method === "resources/list") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        resources: [
          {
            uri: INSPECTOR_URI,
            name: "Telarch Cognitive Infrastructure Inspector",
            description: "Interactive 3-tab inspector for Harpe 0/1 knapsack context packing, Kibisis epistemic memory conflict resolution, and Argus SHA-256 hash-chain verification.",
            mimeType: "text/html;profile=mcp-app",
            _meta: INSPECTOR_RESOURCE_META()
          }
        ]
      }
    };
  }

  if (method === "resources/read") {
    if (typeof params.uri !== "string") {
      return rpcError(id, -32602, "Invalid params: resources/read needs a string `uri`");
    }
    if (params.uri !== INSPECTOR_URI) {
      return rpcError(id, -32602, `Unknown resource URI: ${quoteName(params.uri).slice(1, -1)}`);
    }
    return {
      jsonrpc: "2.0",
      id,
      result: {
        contents: [
          {
            uri: INSPECTOR_URI,
            mimeType: "text/html;profile=mcp-app",
            text: INSPECTOR_HTML,
            _meta: INSPECTOR_RESOURCE_META()
          }
        ]
      }
    };
  }

  if (method === "tools/call") {
    return mcpToolsCall(id, params);
  }

  return rpcError(id, -32601, `Method not found: ${quoteName(method).slice(1, -1)}`);
}

// ---------------------------------------------------------------------------------------------------------
// MCP Streamable HTTP transport. Stateless: no session id is issued and no server-initiated message is sent.
// ---------------------------------------------------------------------------------------------------------

// A request without an Origin header is served (server-to-server MCP clients send none). A request with one
// is served only from these origins; any other origin gets 403 and no Access-Control-Allow-Origin.
const MCP_ALLOWED_ORIGINS = [
  "https://telarch.ai",
  "https://www.telarch.ai",
  "https://perseuscomputing.com",
  "https://www.perseuscomputing.com",
  "https://chatgpt.com",
  "https://chat.openai.com",
  // The frames ChatGPT renders the inspector in. INSPECTOR_RESOURCE_META names telarch.ai as the widget domain
  // and as a connect domain, so the inspector's direct call to /mcp comes from the first of these; the second
  // is the frame used when a host ignores the widget domain.
  "https://telarch-ai.web-sandbox.oaiusercontent.com",
  "https://web-sandbox.oaiusercontent.com"
];

const MCP_CORS_HEADERS = {
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, Mcp-Session-Id, MCP-Protocol-Version, OpenAI-Conversation-Id, OpenAI-Ephemeral-User-Id",
  "Access-Control-Expose-Headers": "Mcp-Session-Id, MCP-Protocol-Version"
};

function mcpBaseHeaders(origin) {
  const headers = { "Cache-Control": "no-store", "Vary": "Origin" };
  if (origin !== null) {
    Object.assign(headers, MCP_CORS_HEADERS, { "Access-Control-Allow-Origin": origin });
  }
  return headers;
}

function mcpJsonResponse(status, body, baseHeaders, extraHeaders) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...baseHeaders, ...(extraHeaders || {}), "Content-Type": "application/json; charset=utf-8" }
  });
}

function mediaTypeOf(headerValue) {
  return (headerValue || "").split(";")[0].trim().toLowerCase();
}

function acceptsJson(acceptHeader) {
  if (acceptHeader === null || acceptHeader.trim() === "") return true;
  return acceptHeader.split(",").some(part => {
    const type = mediaTypeOf(part);
    return type === "application/json" || type === "application/*" || type === "*/*";
  });
}

// Reads at most `limit` bytes of the body. Returns the text, or null when the body is larger.
async function readBodyLimited(request, limit) {
  const declared = request.headers.get("Content-Length");
  if (declared !== null && /^\d+$/.test(declared.trim()) && Number(declared.trim()) > limit) return null;
  if (!request.body) return "";
  const reader = request.body.getReader();
  const chunks = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > limit) {
      try { await reader.cancel(); } catch (_) { /* the body is dropped either way */ }
      return null;
    }
    chunks.push(value);
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
}

// Deepest nesting of arrays and objects in a JSON text, counted without recursion and before parsing.
function jsonNestingDepth(text) {
  let depth = 0;
  let deepest = 0;
  let inString = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text.charCodeAt(i);
    if (inString) {
      if (ch === 92) i++;
      else if (ch === 34) inString = false;
    } else if (ch === 34) {
      inString = true;
    } else if (ch === 123 || ch === 91) {
      depth++;
      if (depth > deepest) deepest = depth;
    } else if (ch === 125 || ch === 93) {
      depth--;
    }
  }
  return deepest;
}

async function handleMcpHttpRequest(request) {
  const origin = request.headers.get("Origin");
  if (origin !== null && !MCP_ALLOWED_ORIGINS.includes(origin)) {
    return mcpJsonResponse(403, rpcError(null, -32600, "Origin not allowed"), mcpBaseHeaders(null));
  }
  const base = mcpBaseHeaders(origin);
  const method = request.method;
  if (method === "OPTIONS") {
    return new Response(null, { status: 204, headers: base });
  }
  if (method !== "GET" && method !== "POST" && method !== "DELETE") {
    return new Response("Method Not Allowed", { status: 405, headers: { ...base, "Allow": "GET, POST, DELETE, OPTIONS" } });
  }
  const versionHeader = request.headers.get("MCP-Protocol-Version");
  if (versionHeader !== null && !MCP_PROTOCOL_VERSIONS.includes(versionHeader.trim())) {
    return mcpJsonResponse(400, rpcError(null, -32600, `Unsupported MCP-Protocol-Version; supported: ${MCP_PROTOCOL_VERSIONS.join(", ")}`), base);
  }
  if (method === "DELETE") {
    // No session exists to end; the request is acknowledged.
    return new Response(null, { status: 204, headers: base });
  }
  if (method === "GET") {
    // A GET either opens an SSE stream or gets 405. This server has no messages of its own to send, so the
    // stream carries one comment and ends.
    const accept = (request.headers.get("Accept") || "").toLowerCase();
    if (accept.includes("text/event-stream")) {
      return new Response(": telarch-mcp streamable-http ready\n\n", {
        status: 200,
        headers: { ...base, "Content-Type": "text/event-stream; charset=utf-8" }
      });
    }
    return new Response("Method Not Allowed", { status: 405, headers: { ...base, "Allow": "POST, OPTIONS" } });
  }

  // POST
  if (mediaTypeOf(request.headers.get("Content-Type")) !== "application/json") {
    return mcpJsonResponse(415, rpcError(null, -32600, "Content-Type must be application/json"), base);
  }
  if (!acceptsJson(request.headers.get("Accept"))) {
    return mcpJsonResponse(406, rpcError(null, -32600, "Accept must admit application/json"), base);
  }
  let text;
  try {
    text = await readBodyLimited(request, TELARCH_LIMITS.max_body_bytes);
  } catch (_) {
    return mcpJsonResponse(400, rpcError(null, -32700, "Parse error"), base);
  }
  if (text === null) {
    return mcpJsonResponse(413, rpcError(null, -32600, `Request body exceeds the limit max_body_bytes=${TELARCH_LIMITS.max_body_bytes}`), base);
  }
  if (jsonNestingDepth(text) > TELARCH_LIMITS.max_json_depth) {
    return mcpJsonResponse(400, rpcError(null, -32600, `Request body is nested deeper than the limit max_json_depth=${TELARCH_LIMITS.max_json_depth}`), base);
  }
  let body;
  try {
    body = JSON.parse(text);
  } catch (_) {
    return mcpJsonResponse(400, rpcError(null, -32700, "Parse error"), base);
  }
  if (Array.isArray(body)) {
    // MCP 2025-06-18 allows one message per POST; batches belong to the earlier revisions. A request without
    // the version header is treated as 2025-03-26, as the transport text says.
    if (versionHeader !== null && versionHeader.trim() === "2025-06-18") {
      return mcpJsonResponse(400, rpcError(null, -32600, "Invalid Request: MCP 2025-06-18 takes a single JSON-RPC message per POST, not a batch"), base);
    }
    if (body.length === 0) {
      return mcpJsonResponse(400, rpcError(null, -32600, "Invalid Request: empty batch"), base);
    }
    if (body.length > TELARCH_LIMITS.max_batch_messages) {
      return mcpJsonResponse(400, rpcError(null, -32600, `Invalid Request: batch of ${body.length} messages is above the limit max_batch_messages=${TELARCH_LIMITS.max_batch_messages}`), base);
    }
    const results = [];
    for (const item of body) {
      const res = await handleMcpRpcSingle(item);
      if (res !== null) results.push(res);
    }
    if (results.length === 0) {
      return new Response(null, { status: 202, headers: base });
    }
    return mcpJsonResponse(200, results, base);
  }
  const res = await handleMcpRpcSingle(body);
  if (res === null) {
    return new Response(null, { status: 202, headers: base });
  }
  const invalidRequest = res.error !== undefined && res.error.code === -32600;
  return mcpJsonResponse(invalidRequest ? 400 : 200, res, base);
}
