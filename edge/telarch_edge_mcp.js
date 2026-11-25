// Telarch Streamable-HTTP MCP Server + Interactive MCP App UI (Cloudflare Edge)
// MIT License (c) 2026 Perseus Computing LLC

const OPENAI_APPS_CHALLENGE_TOKEN = "tvvlXj9ABL4IHa4f6ecObVVH3P-6FniKSZQ6xTuvDYw";
const TELARCH_VERSION = "0.3.1"; // serverInfo.version, and the version the inspector page reports
const INSPECTOR_URI = "ui://telarch/inspector-v1.html";

const INSPECTOR_HTML = "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>Telarch Inspector</title>\n<style>\n  :root {\n    --bg: #0b101b;\n    --panel: #121a2b;\n    --border: #23324d;\n    --text: #e6edf7;\n    --muted: #8fa3c0;\n    --accent: #4da3ff;\n    --ok: #2ecc71;\n    --warn: #f39c12;\n    --err: #ff5c5c;\n    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;\n    --sans: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;\n  }\n  * { box-sizing: border-box; }\n  body {\n    margin: 0;\n    padding: 14px;\n    font-family: var(--sans);\n    background: var(--bg);\n    color: var(--text);\n    font-size: 13px;\n    line-height: 1.45;\n  }\n  .header {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    border-bottom: 1px solid var(--border);\n    padding-bottom: 10px;\n    margin-bottom: 12px;\n  }\n  .brand {\n    display: flex;\n    align-items: center;\n    gap: 8px;\n    font-weight: 700;\n    font-size: 14px;\n    letter-spacing: 0.02em;\n  }\n  .badge {\n    font-family: var(--mono);\n    font-size: 11px;\n    padding: 2px 7px;\n    border-radius: 4px;\n    background: rgba(77,163,255,0.14);\n    color: var(--accent);\n    border: 1px solid rgba(77,163,255,0.35);\n  }\n  .badge.ok { background: rgba(46,204,113,0.14); color: var(--ok); border-color: rgba(46,204,113,0.35); }\n  .badge.warn { background: rgba(243,156,18,0.14); color: var(--warn); border-color: rgba(243,156,18,0.35); }\n  .badge.err { background: rgba(255,92,92,0.14); color: var(--err); border-color: rgba(255,92,92,0.35); }\n  .tabs {\n    display: flex;\n    gap: 6px;\n    margin-bottom: 12px;\n  }\n  .tab {\n    flex: 1;\n    padding: 7px 10px;\n    background: var(--panel);\n    color: var(--muted);\n    border: 1px solid var(--border);\n    border-radius: 6px;\n    cursor: pointer;\n    font-weight: 600;\n    font-size: 12px;\n    text-align: center;\n  }\n  .tab.active {\n    color: var(--text);\n    border-color: var(--accent);\n    background: rgba(77,163,255,0.12);\n  }\n  .card {\n    background: var(--panel);\n    border: 1px solid var(--border);\n    border-radius: 8px;\n    padding: 12px;\n    margin-bottom: 10px;\n  }\n  .row {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    gap: 8px;\n    margin-bottom: 8px;\n  }\n  .bar-wrap {\n    height: 12px;\n    background: #080c14;\n    border-radius: 6px;\n    overflow: hidden;\n    border: 1px solid var(--border);\n    margin: 8px 0;\n  }\n  .bar-fill {\n    height: 100%;\n    background: linear-gradient(90deg, #2b7de9, #2ecc71);\n    transition: width 0.2s ease;\n  }\n  .item-list {\n    display: flex;\n    flex-direction: column;\n    gap: 6px;\n    margin-top: 8px;\n  }\n  .item {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    gap: 10px;\n    padding: 6px 8px;\n    border-radius: 5px;\n    background: #0d1422;\n    border: 1px solid var(--border);\n    font-size: 12px;\n  }\n  /* Text wraps between words. A string with no space in it (a hash, a JSON payload) may wrap anywhere. */\n  .item > div:first-child { min-width: 0; }\n  .item > .badge, .header .badge { white-space: nowrap; flex-shrink: 0; }\n  .mono { font-family: var(--mono); font-size: 11px; color: var(--muted); overflow-wrap: anywhere; }\n  .hash { user-select: all; cursor: copy; }\n  .note { font-size: 12px; color: var(--muted); margin-top: 8px; }\n  .bar-fill.over { background: var(--warn); }\n  .budget-warning { margin-top: 6px; color: var(--warn); white-space: normal; }\n  .budget-warning:empty { display: none; }\n  .banner { display: block; margin-bottom: 8px; overflow-wrap: anywhere; }\n  .source { display: inline-block; margin-bottom: 8px; }\n  button.btn {\n    background: #1b6ef3;\n    color: #fff;\n    border: none;\n    border-radius: 5px;\n    padding: 6px 11px;\n    font-size: 12px;\n    font-weight: 600;\n    cursor: pointer;\n  }\n  button.btn.secondary {\n    background: transparent;\n    border: 1px solid var(--border);\n    color: var(--text);\n  }\n  button.btn.danger {\n    background: rgba(255,92,92,0.18);\n    border: 1px solid rgba(255,92,92,0.45);\n    color: var(--err);\n  }\n  input[type=\"range\"] { width: 160px; }\n  .hidden { display: none; }\n</style>\n</head>\n<body>\n  <div class=\"header\">\n    <div class=\"brand\">\n      <span>TELARCH</span>\n      <span class=\"badge\">Kibisis · Harpe · Argus</span>\n      <span class=\"badge\">v{{TELARCH_VERSION}}</span>\n    </div>\n    <span id=\"status-badge\" class=\"badge ok\">MCP Ready</span>\n  </div>\n\n  <div class=\"tabs\">\n    <button class=\"tab active\" data-tab=\"harpe\">Harpe Exact Knapsack</button>\n    <button class=\"tab\" data-tab=\"kibisis\">Kibisis Memory</button>\n    <button class=\"tab\" data-tab=\"argus\">Argus SHA-256 Chain</button>\n  </div>\n\n  <!-- TAB 1: HARPE -->\n  <div id=\"panel-harpe\" class=\"panel\">\n    <div class=\"card\">\n      <div id=\"harpe-source\" class=\"badge source\"></div>\n      <div class=\"row\">\n        <strong>Exact Knapsack Context Budgeter</strong>\n        <div>\n          <label for=\"budget-slider\" class=\"mono\">Total Budget: <span id=\"budget-val\"></span> tok</label>\n          <input id=\"budget-slider\" type=\"range\" min=\"3580\" max=\"3750\" step=\"5\" value=\"3640\">\n        </div>\n      </div>\n      <div class=\"bar-wrap\"><div id=\"harpe-bar\" class=\"bar-fill\" style=\"width: 0%\"></div></div>\n      <div class=\"row mono\">\n        <span id=\"harpe-summary\"></span>\n        <button id=\"btn-repack\" class=\"btn\">Re-Pack via MCP</button>\n      </div>\n      <div id=\"harpe-warning\" class=\"mono budget-warning\" role=\"status\"></div>\n      <div class=\"mono\" style=\"margin-top:4px\">Policy Digest: <span id=\"harpe-digest\"></span></div>\n      <div id=\"harpe-items\" class=\"item-list\"></div>\n      <div class=\"note\">Priority runs from 0 to 100, and a lower number is more important. Pinned items and priority-0 items are always kept; the other items compete for the tokens that are left.</div>\n    </div>\n  </div>\n\n  <!-- TAB 2: KIBISIS -->\n  <div id=\"panel-kibisis\" class=\"panel hidden\">\n    <div class=\"card\">\n      <div id=\"kibisis-source\" class=\"badge source\"></div>\n      <div class=\"row\">\n        <strong>Epistemic Vault &amp; Conflict Resolution</strong>\n        <button id=\"btn-recall\" class=\"btn\">Resolve Conflicts via MCP</button>\n      </div>\n      <div class=\"mono\" id=\"kibisis-meta\"></div>\n      <div id=\"kibisis-items\" class=\"item-list\"></div>\n      <pre id=\"kibisis-envelope\" class=\"mono\" style=\"background:#080c14;padding:8px;border-radius:5px;border:1px solid var(--border);margin-top:8px;white-space:pre-wrap;\"></pre>\n    </div>\n  </div>\n\n  <!-- TAB 3: ARGUS -->\n  <div id=\"panel-argus\" class=\"panel hidden\">\n    <div class=\"card\">\n      <div id=\"argus-source\" class=\"badge source\"></div>\n      <div class=\"row\">\n        <strong>RFC 8785 Canonical JSON SHA-256 Audit Chain</strong>\n        <div style=\"display:flex;gap:6px;\">\n          <button id=\"btn-tamper\" class=\"btn danger\">Simulate Mid-Chain Tamper</button>\n          <button id=\"btn-verify\" class=\"btn\">Verify Chain via MCP</button>\n        </div>\n      </div>\n      <div id=\"argus-banner\" class=\"badge banner\"></div>\n      <div class=\"mono\">Head: <span id=\"argus-head\" class=\"hash\"></span></div>\n      <div id=\"argus-events\" class=\"item-list\"></div>\n      <div class=\"note\">Click a hash to select all 64 characters. Where the host allows clipboard access, the click copies it as well.</div>\n    </div>\n  </div>\n\n<script type=\"module\">\n  // Default authoritative state\n  let state = {\n    \"harpe\": {\n      \"total_budget\": 3640,\n      \"effective_budget\": 56,\n      \"consumed_tokens\": 38,\n      \"pruned_tokens\": 46,\n      \"utilization_pct\": 67.86,\n      \"reserved_total\": 3584,\n      \"reserves_exceed_budget\": false,\n      \"shortfall_tokens\": 0,\n      \"control_overflow\": false,\n      \"over_budget\": false,\n      \"overflow_tokens\": 0,\n      \"pinned_policy_digest\": \"cafe934dfa8d52cab4344dc561586dbd21abc66489654f54d38327e5dda5cbce\",\n      \"policy\": \"knapsack_dp\",\n      \"reserves\": {\n        \"reserved_completion\": 2048,\n        \"reserved_tools\": 1024,\n        \"safety_margin\": 512\n      },\n      \"items\": [\n        {\n          \"id\": \"sys_invariants\",\n          \"content\": \"Enforce SQLCipher encryption and monotonic fencing tokens on every write.\",\n          \"role\": \"context\",\n          \"priority\": 0,\n          \"pinned\": true,\n          \"tokens\": 19,\n          \"status\": \"INCLUDED (PINNED)\"\n        },\n        {\n          \"id\": \"arch_decision\",\n          \"content\": \"Use the exact knapsack DP for deterministic context packing under budget.\",\n          \"role\": \"context\",\n          \"priority\": 10,\n          \"pinned\": false,\n          \"tokens\": 19,\n          \"status\": \"INCLUDED (KNAPSACK)\"\n        },\n        {\n          \"id\": \"stale_scratch\",\n          \"content\": \"Verbose historical debug trace from the deprecated prototype build: retry loop dumps, allocator statistics and unfiltered request logs, kept for reference only and safe to drop first.\",\n          \"role\": \"context\",\n          \"priority\": 85,\n          \"pinned\": false,\n          \"tokens\": 46,\n          \"status\": \"PRUNED\"\n        }\n      ]\n    },\n    \"kibisis\": {\n      \"active_scope\": \"default\",\n      \"query\": \"SQLCipher encryption\",\n      \"records\": [\n        {\n          \"key\": \"db_engine_v1\",\n          \"category\": \"decision\",\n          \"content\": \"Use unencrypted SQLite for local storage.\",\n          \"epistemic_state\": \"verified\",\n          \"status\": \"SUPERSEDED\"\n        },\n        {\n          \"key\": \"db_engine_v2\",\n          \"category\": \"decision\",\n          \"content\": \"Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).\",\n          \"epistemic_state\": \"verified\",\n          \"supersedes_key\": \"db_engine_v1\",\n          \"status\": \"ACTIVE\"\n        },\n        {\n          \"key\": \"temp_override\",\n          \"category\": \"convention\",\n          \"content\": \"Allow plaintext fallback in production.\",\n          \"epistemic_state\": \"revoked\",\n          \"status\": \"TOMBSTONED (REVOKED)\"\n        }\n      ],\n      \"envelope\": \"\\u003ckibisis-recall trust=\\\"untrusted-stored-text\\\" scope=\\\"default\\\">\\n- [decision/db_engine_v2] (verified): Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).\\n\\u003c/kibisis-recall>\"\n    },\n    \"argus\": {\n      \"valid\": true,\n      \"total_events\": 3,\n      \"root_hash\": \"26fed160404022047c0fe2c7f18eb8f7f49f997d9bb59f27497b6d181aa36cfb\",\n      \"head_hash\": \"751d0246915ff68c0f76082d8df81bf70d297ad06419d1ebd885c3dfd2323065\",\n      \"first_broken_sequence\": null,\n      \"first_broken_index\": null,\n      \"error_detail\": null,\n      \"anchor_prev_hash\": \"GENESIS\",\n      \"starts_at_genesis\": true,\n      \"events\": [\n        {\n          \"sequence\": 1,\n          \"event_id\": \"evt_0001\",\n          \"event_type\": \"kibisis.lease.acquire\",\n          \"actor\": \"worker-a\",\n          \"timestamp\": \"2026-11-04T00:00:01Z\",\n          \"payload\": {\n            \"fencing_token\": 1,\n            \"ttl_s\": 30\n          },\n          \"canonical_payload\": \"{\\\"fencing_token\\\":1,\\\"ttl_s\\\":30}\",\n          \"prev_hash\": \"GENESIS\",\n          \"event_hash\": \"26fed160404022047c0fe2c7f18eb8f7f49f997d9bb59f27497b6d181aa36cfb\"\n        },\n        {\n          \"sequence\": 2,\n          \"event_id\": \"evt_0002\",\n          \"event_type\": \"harpe.context.pack\",\n          \"actor\": \"worker-a\",\n          \"timestamp\": \"2026-11-04T00:00:02Z\",\n          \"payload\": {\n            \"consumed_tokens\": 38,\n            \"savings_bp\": 5476\n          },\n          \"canonical_payload\": \"{\\\"consumed_tokens\\\":38,\\\"savings_bp\\\":5476}\",\n          \"prev_hash\": \"26fed160404022047c0fe2c7f18eb8f7f49f997d9bb59f27497b6d181aa36cfb\",\n          \"event_hash\": \"4f53b01e1b830ebf8e2666f22109701f09e55ae60877b0e61813314a11fd0a3f\"\n        },\n        {\n          \"sequence\": 3,\n          \"event_id\": \"evt_0003\",\n          \"event_type\": \"kibisis.vault.write\",\n          \"actor\": \"worker-a\",\n          \"timestamp\": \"2026-11-04T00:00:03Z\",\n          \"payload\": {\n            \"fencing_token\": 1,\n            \"key\": \"db_engine_v2\"\n          },\n          \"canonical_payload\": \"{\\\"fencing_token\\\":1,\\\"key\\\":\\\"db_engine_v2\\\"}\",\n          \"prev_hash\": \"4f53b01e1b830ebf8e2666f22109701f09e55ae60877b0e61813314a11fd0a3f\",\n          \"event_hash\": \"751d0246915ff68c0f76082d8df81bf70d297ad06419d1ebd885c3dfd2323065\"\n        }\n      ]\n    }\n  };\n\n  // The chain as the server sealed it. The tamper button changes a copy of it; the verify button checks it.\n  let sealedChain = state.argus;\n  // How the chain on the Argus tab was last checked: \"sealed\" (hashes written, nothing checked yet),\n  // \"verified\" or \"broken\" (a result of argus_audit_verify).\n  let argusCheck = \"sealed\";\n  // Where the data of each tab came from: \"demonstration\" (built into the server) or \"request\" (passed in by\n  // the conversation, to telarch_open_inspector or as a tool result the host pushed to this page).\n  let dataSource = { harpe: \"demonstration\", kibisis: \"demonstration\", argus: \"demonstration\" };\n\n  // Tab switching\n  document.querySelectorAll(\".tab\").forEach(btn => {\n    btn.addEventListener(\"click\", () => {\n      document.querySelectorAll(\".tab\").forEach(b => b.classList.remove(\"active\"));\n      document.querySelectorAll(\".panel\").forEach(p => p.classList.add(\"hidden\"));\n      btn.classList.add(\"active\");\n      document.getElementById(\"panel-\" + btn.dataset.tab).classList.remove(\"hidden\");\n    });\n  });\n\n  // Tool output is data, never markup: every value placed into innerHTML goes through esc().\n  const ESC_MAP = { \"&\": \"&amp;\", \"<\": \"&lt;\", \">\": \"&gt;\", '\"': \"&quot;\", \"'\": \"&#x27;\", \"`\": \"&#x60;\" };\n  function esc(value) {\n    return String(value ?? \"\").replace(/[&<>\"'`]/g, ch => ESC_MAP[ch]);\n  }\n\n  // JSON-RPC 2.0 MCP Apps postMessage bridge\n  let rpcId = 1;\n  const pending = new Map();\n\n  window.addEventListener(\"message\", (ev) => {\n    if (ev.source !== window.parent) return; // only the host frame speaks on this bridge\n    const msg = ev.data;\n    if (!msg || typeof msg !== \"object\") return;\n    if (msg.id && pending.has(msg.id)) {\n      const { resolve } = pending.get(msg.id);\n      pending.delete(msg.id);\n      resolve(msg.result || msg.error);\n      return;\n    }\n    if (msg.method === \"ui/notifications/tool-result\" && msg.params?.structuredContent) {\n      applyServerPayload(msg.params.structuredContent);\n    }\n  });\n\n  function sendRpc(method, params) {\n    return new Promise((resolve) => {\n      const id = rpcId++;\n      pending.set(id, { resolve });\n      window.parent.postMessage({ jsonrpc: \"2.0\", id, method, params }, \"*\");\n      setTimeout(() => {\n        if (pending.has(id)) {\n          pending.delete(id);\n          resolve(null);\n        }\n      }, 2500);\n    });\n  }\n\n  // Calls a tool through the host and returns its structuredContent, or null when the call failed or was\n  // refused. Nothing is drawn here: the caller passes the result to applyServerPayload with the tool's name.\n  async function callMcpTool(name, args) {\n    const statusBadge = document.getElementById(\"status-badge\");\n    statusBadge.textContent = \"Calling \" + name + \"…\";\n    statusBadge.className = \"badge warn\";\n    const settle = (res) => {\n      const sc = res && !res.isError && res.structuredContent ? res.structuredContent : null;\n      statusBadge.textContent = sc ? \"MCP Synced\" : \"Call refused\";\n      statusBadge.className = sc ? \"badge ok\" : \"badge warn\";\n      return sc;\n    };\n    if (window.openai?.callTool) {\n      try {\n        return settle(await window.openai.callTool(name, args));\n      } catch (_) {}\n    }\n    const rpcRes = await sendRpc(\"tools/call\", { name, arguments: args });\n    if (rpcRes?.structuredContent || rpcRes?.isError) return settle(rpcRes);\n    // Direct fallback to https://telarch.ai/mcp when running standalone\n    try {\n      const r = await fetch(\"https://telarch.ai/mcp\", {\n        method: \"POST\",\n        headers: { \"Content-Type\": \"application/json\" },\n        body: JSON.stringify({ jsonrpc: \"2.0\", id: rpcId++, method: \"tools/call\", params: { name, arguments: args } })\n      });\n      const j = await r.json();\n      return settle(j?.result);\n    } catch (_) {\n      // No host bridge and no network: the page keeps what it showed and says the call did not happen.\n      statusBadge.textContent = \"MCP not reachable\";\n      statusBadge.className = \"badge warn\";\n      return null;\n    }\n  }\n\n  // `tool` names the tool that produced `sc` when the page made the call itself. A result pushed by the host\n  // carries no name and is read by its shape.\n  function applyServerPayload(sc, tool) {\n    if (!sc) return;\n    if (sc.data_source && typeof sc.data_source === \"object\") {\n      for (const tab of [\"harpe\", \"kibisis\", \"argus\"]) {\n        if (typeof sc.data_source[tab] === \"string\") dataSource[tab] = sc.data_source[tab];\n      }\n    }\n    if (sc.harpe) state.harpe = sc.harpe;\n    if (sc.kibisis) state.kibisis = sc.kibisis;\n    if (sc.argus) {\n      state.argus = sc.argus;\n      sealedChain = sc.argus;\n      // Events passed in by the conversation went through the verifier on the server before they were sent\n      // here. The demonstration chain was only sealed.\n      argusCheck = dataSource.argus === \"request\" ? (sc.argus.valid ? \"verified\" : \"broken\") : \"sealed\";\n    }\n    // A result with no tool name was pushed by the host: it is a tool result of the conversation.\n    if (sc.policy_applied && sc.included_items) {\n      if (!tool) dataSource.harpe = \"request\";\n      const rows = [\n        ...sc.included_items.map(i => ({ ...i, status: keptStatus(i, sc.policy_applied) })),\n        ...(sc.pruned_items || []).map(i => ({ ...i, status: \"PRUNED\" }))\n      ];\n      // Rows keep the order the items were sent in: in harpe the position of an item is its age.\n      const sent = (state.harpe.items || []).map(i => i.id);\n      const place = id => (sent.indexOf(id) < 0 ? sent.length : sent.indexOf(id));\n      rows.sort((x, y) => place(x.id) - place(y.id));\n      state.harpe = {\n        total_budget: sc.total_budget,\n        effective_budget: sc.effective_budget,\n        consumed_tokens: sc.consumed_tokens,\n        pruned_tokens: sc.pruned_tokens,\n        utilization_pct: sc.utilization_pct,\n        reserved_total: sc.reserved_total,\n        reserves_exceed_budget: sc.reserves_exceed_budget,\n        shortfall_tokens: sc.shortfall_tokens,\n        control_overflow: sc.control_overflow,\n        over_budget: sc.over_budget,\n        overflow_tokens: sc.overflow_tokens,\n        pinned_policy_digest: sc.pinned_policy_digest,\n        policy: sc.policy_applied,\n        // The page's own call sent these reserves. A pushed result does not name them one by one, so their sum\n        // is taken from the result (reserved_total since 0.3.1; before that, total minus effective budget);\n        // packing again with that sum gives the same effective budget.\n        reserves: tool && state.harpe.reserves\n          ? state.harpe.reserves\n          : {\n            reserved_completion: Number.isFinite(sc.reserved_total) ? sc.reserved_total : Math.max(0, sc.total_budget - sc.effective_budget),\n            reserved_tools: 0,\n            safety_margin: 0\n          },\n        items: rows\n      };\n    }\n    if (sc.envelope && sc.resolved_records) {\n      if (!tool) dataSource.kibisis = \"request\";\n      state.kibisis = {\n        active_scope: sc.active_scope,\n        query: sc.query,\n        records: sc.all_records_trace || sc.resolved_records,\n        envelope: sc.envelope\n      };\n    }\n    if (typeof sc.valid === \"boolean\" && sc.events) {\n      if (!tool) dataSource.argus = \"request\";\n      state.argus = sc;\n      if (tool === \"argus_audit_verify\" || !sc.valid) {\n        // Only the verifier reports a break, and only its answer counts as a verification.\n        argusCheck = sc.valid ? \"verified\" : \"broken\";\n      } else {\n        sealedChain = sc;\n        argusCheck = \"sealed\";\n      }\n    }\n    render();\n  }\n\n  // How a kept item is labelled. The server has the same function (harpeKeptStatus).\n  function keptStatus(item, policy) {\n    if (item.pinned === true) return \"INCLUDED (PINNED)\";\n    if (item.priority === 0) return \"INCLUDED (PRIORITY 0)\";\n    return policy === \"knapsack_dp\" ? \"INCLUDED (KNAPSACK)\" : `INCLUDED (${String(policy).toUpperCase()})`;\n  }\n\n  function sourceLabel(el, source) {\n    el.textContent = source === \"request\" ? \"Data from this conversation\" : \"Demonstration data\";\n    el.className = source === \"request\" ? \"badge source ok\" : \"badge source\";\n  }\n\n  // Why a Harpe item was kept or pruned, from the numbers of the result. `ctx` says what took the room:\n  // the reserves (nothing left for context at all) or the always-kept items.\n  function harpeReason(it, room, policy, ctx) {\n    const kept = String(it.status ?? \"\").startsWith(\"INCLUDED\");\n    if (kept && (it.pinned === true || it.priority === 0)) {\n      return ctx.overBudget ? \"always kept: pinned or priority 0, even over the budget\" : \"always kept: pinned or priority 0\";\n    }\n    const left = ctx.alwaysKeptTokens > 0 ? `the ${room} tok left after the always-kept items` : `the ${room} tok available`;\n    if (kept) return `kept: chosen for ${left}`;\n    if (ctx.reservesTakeAll) {\n      return `pruned: no tokens are left for context; the reserves (${ctx.reservedTotal} tok) take the whole ${ctx.totalBudget}-tok budget`;\n    }\n    if ((Number(it.tokens) || 0) > room) return `pruned: its ${it.tokens} tok do not fit in ${left}`;\n    if (policy === \"knapsack_dp\") return `pruned: it fits on its own, but the kept items score higher together within ${room} tok`;\n    return \"pruned: it fits on its own, but this policy took other items first\";\n  }\n\n  function render() {\n    // Render Harpe\n    sourceLabel(document.getElementById(\"harpe-source\"), dataSource.harpe);\n    sourceLabel(document.getElementById(\"kibisis-source\"), dataSource.kibisis);\n    sourceLabel(document.getElementById(\"argus-source\"), dataSource.argus);\n    const h = state.harpe;\n    document.getElementById(\"budget-val\").textContent = h.total_budget;\n    const slider = document.getElementById(\"budget-slider\");\n    if (dataSource.harpe === \"request\" && Number.isFinite(h.total_budget)) {\n      // The demonstration range suits the demonstration items. For other items the slider runs from the\n      // reserves (nothing fits) to the budget at which every item fits, and always holds the budget in use.\n      const r = h.reserves || {};\n      const reserved = (Number(r.reserved_completion) || 0) + (Number(r.reserved_tools) || 0) + (Number(r.safety_margin) || 0);\n      const candidates = (Number(h.consumed_tokens) || 0) + (Number(h.pruned_tokens) || 0);\n      slider.min = String(Math.max(1, Math.min(reserved, h.total_budget)));\n      slider.max = String(Math.max(h.total_budget, reserved + candidates));\n      slider.step = \"1\";\n    }\n    if (Number.isFinite(h.total_budget)) slider.value = String(h.total_budget);\n    const pct = Math.min(100, Math.max(0, h.utilization_pct || 0));\n    const rv = h.reserves || {};\n    const reservedTotal = Number.isFinite(h.reserved_total)\n      ? h.reserved_total\n      : (Number(rv.reserved_completion) || 0) + (Number(rv.reserved_tools) || 0) + (Number(rv.safety_margin) || 0);\n    const totalBudget = Number(h.total_budget) || 0;\n    const effective = Number(h.effective_budget) || 0;\n    const shortfall = Number.isFinite(h.shortfall_tokens) ? h.shortfall_tokens : Math.max(0, reservedTotal - totalBudget);\n    const reservesExceed = typeof h.reserves_exceed_budget === \"boolean\" ? h.reserves_exceed_budget : reservedTotal > totalBudget;\n    const reservesTakeAll = effective === 0 && reservedTotal >= totalBudget;\n    // over_budget comes from the server; a result from before 0.3.1 lacks it, so it is worked out from the numbers.\n    const consumed = Number(h.consumed_tokens) || 0;\n    const overBudget = typeof h.over_budget === \"boolean\" ? h.over_budget : consumed > effective;\n    const overflow = Number.isFinite(h.overflow_tokens) ? h.overflow_tokens : Math.max(0, consumed - effective);\n    const bar = document.getElementById(\"harpe-bar\");\n    bar.style.width = (overBudget ? 100 : pct) + \"%\";\n    bar.className = overBudget ? \"bar-fill over\" : \"bar-fill\";\n    const used = overBudget ? `${overflow} tok over the budget` : `${pct.toFixed(1)}%`;\n    document.getElementById(\"harpe-summary\").textContent =\n      `Effective: ${h.effective_budget} tok | Consumed: ${h.consumed_tokens} tok (${used}) | Pruned: ${h.pruned_tokens} tok`;\n    const reserveParts = Number.isFinite(rv.reserved_completion) && Number.isFinite(rv.reserved_tools) && Number.isFinite(rv.safety_margin) && (rv.reserved_tools || rv.safety_margin)\n      ? ` (completion ${rv.reserved_completion} + tools ${rv.reserved_tools} + margin ${rv.safety_margin})`\n      : \"\";\n    let warning = \"\";\n    if (reservesExceed) {\n      warning = `No room for context: the reserves${reserveParts} need ${reservedTotal} tok, ${shortfall} tok more than the ${totalBudget}-tok total budget. Raise total_budget or lower the reserves; set them to 0 to pack against the total budget alone.`;\n    } else if (reservesTakeAll) {\n      warning = `No room for context: the reserves${reserveParts} take the whole ${totalBudget}-tok total budget. Raise total_budget or lower the reserves.`;\n    }\n    if (overBudget) {\n      warning += (warning ? \" \" : \"\") + `The always-kept items (pinned or priority 0) need ${consumed} tok and are kept anyway, ${overflow} tok over the ${effective} tok available.`;\n    }\n    document.getElementById(\"harpe-warning\").textContent = warning;\n    document.getElementById(\"harpe-digest\").textContent = \"sha256:\" + String(h.pinned_policy_digest);\n    const hItems = Array.isArray(h.items) ? h.items : [];\n    const alwaysKeptTokens = hItems\n      .filter(it => String(it.status ?? \"\").startsWith(\"INCLUDED\") && (it.pinned === true || it.priority === 0))\n      .reduce((sum, it) => sum + (Number(it.tokens) || 0), 0);\n    const room = Math.max(0, (Number(h.effective_budget) || 0) - alwaysKeptTokens);\n    const reasonCtx = { alwaysKeptTokens, overBudget, reservesTakeAll, reservedTotal, totalBudget };\n    const hList = document.getElementById(\"harpe-items\");\n    hList.innerHTML = \"\";\n    hItems.forEach(it => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const status = String(it.status ?? \"\");\n      const cls = status.startsWith(\"INCLUDED\") ? \"ok\" : \"warn\";\n      div.innerHTML = `<div><strong>${esc(it.id)}</strong> (priority ${esc(it.priority)}, ${esc(it.tokens ?? \"?\")} tok)<div class=\"mono\">${esc(it.content)}</div><div class=\"mono\">${esc(harpeReason(it, room, h.policy ?? \"knapsack_dp\", reasonCtx))}</div></div><span class=\"badge ${cls}\">${esc(status)}</span>`;\n      hList.appendChild(div);\n    });\n\n    // Render Kibisis\n    const k = state.kibisis;\n    const kRecords = Array.isArray(k.records) ? k.records : [];\n    const withStatus = test => kRecords.filter(rec => test(String(rec.status ?? \"\"))).length;\n    document.getElementById(\"kibisis-meta\").textContent =\n      `Scope: ${k.active_scope ?? \"default\"} | Query: ${JSON.stringify(k.query ?? \"\")} | ` +\n      `${withStatus(s => s === \"ACTIVE\")} active, ${withStatus(s => s === \"SUPERSEDED\")} superseded, ${withStatus(s => s.includes(\"TOMBSTONE\"))} revoked. ` +\n      \"The envelope holds the active records that match the query.\";\n    const kList = document.getElementById(\"kibisis-items\");\n    kList.innerHTML = \"\";\n    kRecords.forEach(rec => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const status = String(rec.status ?? \"\");\n      const cls = status === \"ACTIVE\" ? \"ok\" : (status.includes(\"TOMBSTONE\") ? \"err\" : \"warn\");\n      div.innerHTML = `<div><strong>${esc(rec.category)}/${esc(rec.key)}</strong> [${esc(rec.epistemic_state)}]<div class=\"mono\">${esc(rec.content)}</div></div><span class=\"badge ${cls}\">${esc(status)}</span>`;\n      kList.appendChild(div);\n    });\n    document.getElementById(\"kibisis-envelope\").textContent = k.envelope || \"\";\n\n    // Render Argus. \"Verified\" is said only after argus_audit_verify answered; a sealed chain is shown as sealed.\n    const a = state.argus;\n    const aEvents = Array.isArray(a.events) ? a.events : [];\n    const anchor = a.starts_at_genesis === false ? \"the supplied anchor\" : \"GENESIS\";\n    const banner = document.getElementById(\"argus-banner\");\n    if (!a.valid) {\n      banner.className = \"badge err banner\";\n      banner.textContent = `CHAIN BROKEN AT ${a.first_broken_sequence == null ? \"EVENT INDEX \" + a.first_broken_index : \"SEQ #\" + a.first_broken_sequence}: ${a.error_detail}`;\n    } else if (argusCheck === \"verified\") {\n      banner.className = \"badge ok banner\";\n      banner.textContent = `CHAIN VALID: ${aEvents.length}/${aEvents.length} events verified from ${anchor} by argus_audit_verify`;\n    } else {\n      banner.className = \"badge banner\";\n      banner.textContent = `SEALED, NOT YET VERIFIED: ${aEvents.length} events chained from ${anchor}. \"Verify Chain via MCP\" checks them.`;\n    }\n    document.getElementById(\"argus-head\").textContent = String(a.head_hash ?? \"\");\n    const aList = document.getElementById(\"argus-events\");\n    aList.innerHTML = \"\";\n    aEvents.forEach((ev, evIndex) => {\n      if (!ev || typeof ev !== \"object\") return;\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const broken = !a.valid && (a.first_broken_index === undefined ? a.first_broken_sequence === ev.sequence : a.first_broken_index === evIndex);\n      // The verifier stops at the first break: events before it passed, events after it were not looked at.\n      let mark = [\"\", \"SEALED\"];\n      if (broken) mark = [\"err\", \"BROKEN HERE\"];\n      else if (a.valid && argusCheck === \"verified\") mark = [\"ok\", \"VERIFIED\"];\n      else if (!a.valid && Number.isInteger(a.first_broken_index)) mark = evIndex < a.first_broken_index ? [\"ok\", \"VERIFIED\"] : [\"warn\", \"NOT CHECKED\"];\n      div.innerHTML = `<div><strong>#${esc(ev.sequence)} ${esc(ev.event_type)}</strong> (${esc(ev.actor)}) <span class=\"mono\">${esc(ev.timestamp == null ? \"no timestamp\" : ev.timestamp)}</span><div class=\"mono\">payload: ${esc(JSON.stringify(ev.payload))}</div><div class=\"mono\">prev: <span class=\"hash\">${esc(ev.prev_hash)}</span></div><div class=\"mono\">hash: <span class=\"hash\">${esc(ev.event_hash)}</span></div></div><span class=\"badge ${mark[0]}\">${mark[1]}</span>`;\n      aList.appendChild(div);\n    });\n  }\n\n  document.getElementById(\"budget-slider\").addEventListener(\"input\", (e) => {\n    document.getElementById(\"budget-val\").textContent = e.target.value;\n  });\n\n  document.getElementById(\"btn-repack\").addEventListener(\"click\", async () => {\n    const totalBudget = parseInt(document.getElementById(\"budget-slider\").value, 10);\n    const packed = await callMcpTool(\"harpe_synthesize_context\", {\n      total_budget: totalBudget,\n      ...(state.harpe.reserves || {}),\n      policy: state.harpe.policy ?? \"knapsack_dp\",\n      items: (state.harpe.items || []).map(it => {\n        const item = { id: it.id, content: it.content, priority: it.priority, pinned: it.pinned === true };\n        if (typeof it.role === \"string\") item.role = it.role;\n        return item;\n      })\n    });\n    if (!packed) return;\n    applyServerPayload(packed, \"harpe_synthesize_context\");\n    // The demonstration chain records the packing result, so it is sealed again with the new numbers. A chain\n    // from the conversation is left as it is.\n    if (dataSource.argus !== \"demonstration\") return;\n    const chain = Array.isArray(sealedChain.events) ? sealedChain.events.filter(ev => ev && typeof ev === \"object\") : [];\n    if (!chain.some(ev => ev.event_type === \"harpe.context.pack\")) return;\n    const resealed = await callMcpTool(\"argus_audit_seal\", {\n      events: chain.map(ev => {\n        const event = {\n          event_type: ev.event_type,\n          actor: ev.actor,\n          payload: ev.event_type === \"harpe.context.pack\"\n            ? { consumed_tokens: packed.consumed_tokens, savings_bp: packed.tokens_saved_bp }\n            : ev.payload\n        };\n        if (typeof ev.timestamp === \"string\") event.timestamp = ev.timestamp;\n        return event;\n      })\n    });\n    applyServerPayload(resealed, \"argus_audit_seal\");\n  });\n\n  document.getElementById(\"btn-recall\").addEventListener(\"click\", async () => {\n    applyServerPayload(await callMcpTool(\"kibisis_resolve_memory\", {\n      active_scope: state.kibisis.active_scope ?? \"default\",\n      requested_scope: state.kibisis.active_scope ?? \"default\",\n      query: typeof state.kibisis.query === \"string\" ? state.kibisis.query : \"\",\n      records: (state.kibisis.records || []).map(r => {\n        const rec = { key: r.key, category: r.category, content: r.content, epistemic_state: r.epistemic_state };\n        if (typeof r.supersedes_key === \"string\") rec.supersedes_key = r.supersedes_key;\n        return rec;\n      })\n    }), \"kibisis_resolve_memory\");\n  });\n\n  // Changes one payload in a copy of the sealed chain, leaves the hashes as they were, and asks the verifier.\n  document.getElementById(\"btn-tamper\").addEventListener(\"click\", async () => {\n    const tampered = JSON.parse(JSON.stringify(Array.isArray(sealedChain.events) ? sealedChain.events : []));\n    const target = tampered[Math.min(1, tampered.length - 1)];\n    if (target && typeof target === \"object\") {\n      const before = target.payload && typeof target.payload === \"object\" ? target.payload : {};\n      target.payload = { ...before, savings_bp: before.savings_bp === 9999 ? 9998 : 9999 };\n    }\n    applyServerPayload(await callMcpTool(\"argus_audit_verify\", { events: tampered }), \"argus_audit_verify\");\n  });\n\n  // Verifies the chain as it was sealed, unchanged. After a tamper this shows the untampered chain again.\n  document.getElementById(\"btn-verify\").addEventListener(\"click\", async () => {\n    applyServerPayload(await callMcpTool(\"argus_audit_verify\", { events: sealedChain.events }), \"argus_audit_verify\");\n  });\n\n  document.getElementById(\"panel-argus\").addEventListener(\"click\", (e) => {\n    const el = e.target && e.target.closest ? e.target.closest(\".hash\") : null;\n    if (!el || typeof navigator === \"undefined\" || !navigator.clipboard?.writeText) return;\n    navigator.clipboard.writeText(el.textContent).then(() => {\n      const statusBadge = document.getElementById(\"status-badge\");\n      statusBadge.textContent = \"Hash copied\";\n      statusBadge.className = \"badge ok\";\n    }, () => {});\n  });\n\n  // Initialize bridge & render\n  if (window.openai?.toolOutput) {\n    applyServerPayload(window.openai.toolOutput);\n  } else {\n    render();\n  }\n  sendRpc(\"ui/initialize\", {\n    protocolVersion: \"2025-06-18\",\n    appInfo: { name: \"Telarch Inspector\", version: \"{{TELARCH_VERSION}}\" },\n    appCapabilities: {}\n  }).then(() => {\n    window.parent.postMessage({ jsonrpc: \"2.0\", method: \"ui/notifications/initialized\", params: {} }, \"*\");\n  });\n</script>\n</body>\n</html>".split("{{TELARCH_VERSION}}").join(TELARCH_VERSION);

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
// `code` is one of REFUSAL_CODES. `path` names the argument the refusal is about, written from the tool's
// arguments as in "items[1].id", or is null when no single argument is at fault.
class TelarchRefusal extends Error {
  constructor(code, path, message) {
    super(message);
    this.name = "TelarchRefusal";
    this.code = code;
    this.path = path;
  }
}

// Every code a refused call can carry. A code is the error name its message starts with, without a trailing
// "Error". The list only grows: a code is never renamed and never used for another refusal.
const REFUSAL_CODES = [
  "InvalidArguments",        // the arguments do not match the tool's inputSchema (JSON-RPC error -32602)
  "PayloadTooDeep", "FloatPayload", "UnsafeInteger", "UnsupportedPayload",
  "KnapsackTooLarge", "UnknownPolicy", "DuplicateItemId",
  "ScopeIsolation", "EpistemicTrustViolation", "DuplicateRecordKey", "SupersessionLoop",
  "StaleFencingToken", "LeaseClockMissing", "LeaseExpired",
  "PrevHashFormat", "SequenceRequired", "SequenceOrder"
];

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
    throw new TelarchRefusal("PayloadTooDeep", path, `PayloadTooDeepError at ${path}: nested deeper than the limit max_json_depth=${TELARCH_LIMITS.max_json_depth}.`);
  }
  if (val === null) return "null";
  const t = typeof val;
  if (t === "boolean") return val ? "true" : "false";
  if (t === "number") {
    if (!Number.isFinite(val) || !Number.isInteger(val)) {
      throw new TelarchRefusal("FloatPayload", path, `FloatPayloadError at ${path}: a non-integer number is rejected for canonical SHA-256 hashing; express fractions as integer basis points (*_bp).`);
    }
    if (!Number.isSafeInteger(val)) {
      throw new TelarchRefusal("UnsafeInteger", path, `UnsafeIntegerError at ${path}: integers beyond +/-9007199254740991 (2**53 - 1) cannot be hashed exactly; send them as strings.`);
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
  throw new TelarchRefusal("UnsupportedPayload", path, `UnsupportedPayloadError at ${path}: only JSON values can be hashed.`);
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

function harpeReserves(args) {
  return {
    reserved_completion: args.reserved_completion ?? 2048,
    reserved_tools: args.reserved_tools ?? 1024,
    safety_margin: args.safety_margin ?? 512
  };
}

function harpeReservedTotal(args) {
  const reserves = harpeReserves(args);
  return reserves.reserved_completion + reserves.reserved_tools + reserves.safety_margin;
}

function harpeAvailable(args) {
  return Math.max(0, args.total_budget - harpeReservedTotal(args));
}

// available_context, utilization_pct and is_exceeded are what harpe's TokenBudget gives: the available amount
// is never below 0, and with nothing available the utilization is 100 and is_exceeded is false while nothing
// is used. reserves_exceed_budget and shortfall_tokens say that the reserves alone are larger than the window.
function runHarpeBudget(args) {
  const reserved = harpeReservedTotal(args);
  const avail = harpeAvailable(args);
  const used = args.current_usage ?? 0;
  return {
    total_budget: args.total_budget,
    reserved_total: reserved,
    available_context: avail,
    current_usage: used,
    utilization_pct: avail > 0 ? roundHalfEven2((used / avail) * 100) : 100,
    is_exceeded: used > avail,
    reserves_exceed_budget: reserved > args.total_budget,
    shortfall_tokens: Math.max(0, reserved - args.total_budget)
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
      "KnapsackTooLarge", null,
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
  throw new TelarchRefusal("UnknownPolicy", "policy", `UnknownPolicyError: policy must be one of ${HARPE_POLICIES.join(", ")}.`);
}

const HARPE_POLICIES = ["knapsack_dp", "lowest_priority", "fifo", "warm_prefix"];

// Context synthesizer with the semantics of harpe 0.1.0a13 ContextBudgetEngine.synthesize (Harpe)
async function runHarpeSynthesize(args) {
  const totalBudget = args.total_budget;
  const policy = args.policy ?? "knapsack_dp";
  const effectiveBudget = harpeAvailable(args);
  const reservedTotal = harpeReservedTotal(args);

  const seen = new Set();
  const items = args.items.map((it, index) => {
    if (seen.has(it.id)) {
      throw new TelarchRefusal("DuplicateItemId", `items[${index}].id`, `DuplicateItemIdError: item id ${JSON.stringify(it.id)} occurs more than once; ids must be unique.`);
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
    reserved_total: reservedTotal,
    reserves_exceed_budget: reservedTotal > totalBudget,
    shortfall_tokens: Math.max(0, reservedTotal - totalBudget),
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
    throw new TelarchRefusal("ScopeIsolation", "requested_scope", `ScopeIsolationError: cross-scope memory access denied (requested_scope=${JSON.stringify(requestedScope)} != active_scope=${JSON.stringify(activeScope)}).`);
  }
  // Write gate, fail closed: only a write that names origin "user" may carry epistemic_state "verified".
  if (args.write_attempt !== undefined) {
    const attempt = args.write_attempt;
    if (attempt.epistemic_state === "verified" && attempt.origin !== "user") {
      throw new TelarchRefusal("EpistemicTrustViolation", "write_attempt.epistemic_state", "EpistemicTrustViolation: model-originated writes cannot self-promote to epistemic_state='verified'; store as 'candidate' for human review.");
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

  // A key occurs once per category: with two records under one key nothing says which of them holds.
  const firstIndex = new Map();
  const byKey = new Map();
  records.forEach((r, index) => {
    const id = JSON.stringify([r.category, r.key]);
    if (firstIndex.has(id)) {
      throw new TelarchRefusal("DuplicateRecordKey", `records[${index}].key`, `DuplicateRecordKeyError: records[${firstIndex.get(id)}] and records[${index}] both have category ${quoteName(r.category)} and key ${quoteName(r.key)}; a key occurs once per category.`);
    }
    firstIndex.set(id, index);
    if (!byKey.has(r.key)) byKey.set(r.key, []);
    byKey.get(r.key).push(r);
  });

  // A record supersedes another only if it is not revoked, does not name itself, and is verified whenever the
  // record it replaces is verified: a candidate, disputed or withdrawn record never displaces a verified one.
  // A supersedes_key that names no record of this call is valid (the older record may not have been sent) and
  // is reported in unresolved_supersedes.
  const superseded = new Set();
  const replaces = new Map();
  const unresolvedSupersedes = [];
  for (const r of records) {
    if (r.supersedes_key === undefined || r.supersedes_key === r.key) continue;
    const named = byKey.get(r.supersedes_key) ?? [];
    if (named.length === 0 && !unresolvedSupersedes.includes(r.supersedes_key)) unresolvedSupersedes.push(r.supersedes_key);
    if (r.epistemic_state === "revoked") continue;
    for (const target of named) {
      if (target.epistemic_state === "revoked") continue;
      if (target.epistemic_state === "verified" && r.epistemic_state !== "verified") continue;
      superseded.add(target);
      if (!replaces.has(r)) replaces.set(r, []);
      replaces.get(r).push(target);
    }
  }

  // Records that supersede each other in a loop would all be dropped, with nothing left active and no notice.
  // The call is refused instead. Walked without recursion: a chain may be as long as the record limit.
  const visit = new Map(); // 1: on the path being walked, 2: finished
  for (const start of replaces.keys()) {
    if (visit.has(start)) continue;
    const path = [start];
    const cursor = [0];
    visit.set(start, 1);
    while (path.length > 0) {
      const targets = replaces.get(path[path.length - 1]) ?? [];
      const at = cursor[cursor.length - 1]++;
      if (at >= targets.length) {
        visit.set(path.pop(), 2);
        cursor.pop();
        continue;
      }
      const target = targets[at];
      if (visit.get(target) === 1) {
        const loop = path.slice(path.indexOf(target)).map(r => quoteName(r.key));
        const chain = loop.length > 8
          ? `${loop.slice(0, 8).join(" supersedes ")} supersedes … (${loop.length} records in the loop)`
          : `${loop.join(" supersedes ")} supersedes ${loop[0]}`;
        throw new TelarchRefusal("SupersessionLoop", `records[${records.indexOf(target)}].supersedes_key`, `SupersessionLoopError: supersedes_key forms a loop: ${chain}. None of these records could be active; remove one of their supersedes_key values.`);
      }
      if (visit.get(target) === 2) continue;
      visit.set(target, 1);
      path.push(target);
      cursor.push(0);
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
    unresolved_supersedes: unresolvedSupersedes,
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
    throw new TelarchRefusal("StaleFencingToken", "fencing_token", `StaleFencingTokenError: holder ${holder} presented fencing_token=${token} < highest_token_seen=${highest}. Split-brain write rejected.`);
  }
  if (args.lease_expires_epoch !== undefined) {
    if (args.now_epoch === undefined) {
      throw new TelarchRefusal("LeaseClockMissing", "now_epoch", "LeaseClockMissingError: lease_expires_epoch was given without now_epoch; expiry cannot be evaluated, so the write is not permitted.");
    }
    if (args.now_epoch >= args.lease_expires_epoch) {
      throw new TelarchRefusal("LeaseExpired", "lease_expires_epoch", `LeaseExpiredError: holder ${holder} lease expired at ${args.lease_expires_epoch} (now=${args.now_epoch}). Write rejected.`);
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
    throw new TelarchRefusal("PrevHashFormat", "prev_hash", "PrevHashFormatError: prev_hash must be \"GENESIS\" or the 64 lowercase hex characters of the previous head_hash.");
  }
  if (startHash !== ARGUS_GENESIS && args.events[0].sequence === undefined) {
    throw new TelarchRefusal("SequenceRequired", "events[0].sequence", "SequenceRequiredError: a segment that continues an earlier chain (prev_hash is not GENESIS) must give `sequence` on its first event.");
  }
  let prevHash = startHash;
  let prevSeq = null;
  const sealed = [];
  for (let i = 0; i < args.events.length; i++) {
    const ev = args.events[i];
    const expectedSeq = prevSeq === null ? (ev.sequence ?? 1) : prevSeq + 1;
    if (ev.sequence !== undefined && ev.sequence !== expectedSeq) {
      throw new TelarchRefusal("SequenceOrder", `events[${i}].sequence`, `SequenceOrderError: events[${i}].sequence is ${ev.sequence} but the chain is linear and needs ${expectedSeq}; sequences rise by exactly one.`);
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

// Shared by the tool that works on the data and by telarch_open_inspector, which shows the same data.
const HARPE_ITEMS_SCHEMA = {
  type: "array",
  maxItems: TELARCH_LIMITS.max_items,
  description: "Candidate context items to pack, oldest first. Ids must be unique. An item's size is counted from its `content` (the larger of its count of words and punctuation marks and a quarter of its characters); there is no field for giving a token count, so send the text itself.",
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
};

const KIBISIS_RECORDS_SCHEMA = {
  type: "array",
  maxItems: TELARCH_LIMITS.max_items,
  description: "Memory records to resolve across supersession and revocation chains. A key occurs once per category. Left out: three built-in demonstration records. An empty list resolves nothing.",
  items: {
    type: "object",
    properties: {
      key: { type: "string", minLength: 1 },
      category: { type: "string", default: "decision" },
      content: { type: "string" },
      epistemic_state: { type: "string", enum: EPISTEMIC_STATES, default: "candidate" },
      supersedes_key: { type: "string", description: "Key of the record this one replaces. It may name a record that is not in this call." }
    },
    required: ["key", "content"],
    additionalProperties: false
  }
};

const ARGUS_SEALED_EVENTS_SCHEMA = {
  type: "array",
  minItems: 1,
  maxItems: TELARCH_LIMITS.max_items,
  description: "Sealed events in order. Each needs sequence (positive integer), event_id, event_type, actor, prev_hash, event_hash (strings), timestamp (string or null) and payload (object); canonical_payload is checked when present. Defects inside an event are reported as valid:false, not as a call error.",
  items: { type: "object" }
};

const MCP_TOOLS = [
  {
    name: "harpe_synthesize_context",
    title: "Synthesize & Prune Context (Exact Knapsack)",
    description: "Use this when you need to pack candidate context items deterministically into a strict token budget. Same selection as the harpe 0.1.0a13 library: the budget optimised against is total_budget minus the three reserves (returned as effective_budget, with their sum as reserved_total); when the reserves alone are larger than total_budget, reserves_exceed_budget is true, shortfall_tokens says by how much and only always-kept items are kept; pinned items and priority-0 items are always kept; the rest are chosen by `policy`. Priority runs 0-100 and a LOWER number is MORE important. The position of an item in `items` is its age: first = oldest. Limits: at most 4096 items, and knapsack_dp is refused (nothing packed, error names max_knapsack_cells) when candidates x (capacity / common divisor of token counts + 1) exceeds 4,000,000. Token counts are a deterministic estimate, not a model tokenizer.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { ...TOTAL_BUDGET, description: "Total model context budget in tokens. The three reserves (2048 + 1024 + 512 = 3584 by default) come off it first; to pack into total_budget alone, set reserved_completion, reserved_tools and safety_margin to 0." },
        reserved_completion: { ...TOKEN_QUANTITY, description: "Tokens reserved for completion output.", default: 2048 },
        reserved_tools: { ...TOKEN_QUANTITY, description: "Tokens reserved for tool schemas.", default: 1024 },
        safety_margin: { ...TOKEN_QUANTITY, description: "Safety margin buffer in tokens.", default: 512 },
        policy: {
          type: "string",
          enum: HARPE_POLICIES,
          default: "knapsack_dp",
          description: "How unpinned items are chosen. knapsack_dp: exact knapsack on utility (falls with the priority number). lowest_priority: lowest priority number first, newer first among equals, each taken if it still fits. fifo: newest first, each taken if it still fits. warm_prefix: oldest items up to half the capacity, then newest items into the rest."
        },
        items: HARPE_ITEMS_SCHEMA
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
      "openai/toolInvocation/invoking": "Solving the exact context knapsack…",
      "openai/toolInvocation/invoked": "Context packed within token budget."
    }
  },
  {
    name: "harpe_budget_evaluate",
    title: "Evaluate Token Budget & Margins",
    description: "Use this when you need to compute available context tokens, safety margin deductions, and utilization percentage for a model token window. The result is arithmetic on the numbers of this call and knows nothing about any model's real window: available_context is total_budget minus reserved_completion (default 2048), reserved_tools (default 1024) and safety_margin (default 512), never below 0, and reserved_total is the sum of the three. When the reserves are larger than total_budget, reserves_exceed_budget is true and shortfall_tokens says by how much. available_context 0 means no context fits; utilization_pct is then 100 whatever current_usage is, and is_exceeded stays false while current_usage is 0.",
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
    description: "Use this to work out which of the memory records you pass in `records` are active: revoked records are tombstoned, superseded records are dropped (a record that is not verified never displaces a verified one; `supersedes_key` applies to every record with that key), a requested scope other than the active scope is refused, and a write_attempt that claims epistemic_state 'verified' without origin 'user' is refused. Active records matching `query` are returned in a <kibisis-recall trust=\"untrusted-stored-text\"> envelope with markup characters escaped. Refused: two records with the same category and key, and records that supersede each other in a loop. A `supersedes_key` that names no record of the call is allowed and is listed in `unresolved_supersedes`. Stateless: this server stores no memory. It resolves the records of this call; when `records` is left out it resolves three built-in demonstration records and the result says records_source \"demonstration\".",
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
        records: KIBISIS_RECORDS_SCHEMA
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
    description: "Use this to compute canonical RFC 8785 (JCS) JSON and linear SHA-256 hash-chain digests for a sequence of agent audit events, from GENESIS or from the head_hash of an earlier segment (prev_hash; then the first event must give its sequence). Sequences rise by exactly one. Rejects fractions (use integer basis points *_bp) and integers beyond +/-(2**53 - 1) (send them as strings). An event without a timestamp is sealed with timestamp null; no time is invented. To check the chain, pass the returned events to argus_audit_verify unchanged, a null timestamp included. Stateless: the sealed events are returned, not stored.",
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
    description: "Use this to cryptographically verify a linear SHA-256 Argus audit chain and isolate the first event that is altered, malformed, out of sequence or unlinked. Pass the sealed events exactly as argus_audit_seal returned them, with timestamp null where it is null; a missing or retyped field makes the chain invalid, nothing is defaulted. The result proves the listed events are unaltered and linked from anchor_prev_hash (starts_at_genesis says whether that is GENESIS). It cannot detect events removed from the end of the list: compare head_hash and total_events with values you already trust.",
    inputSchema: {
      type: "object",
      properties: {
        prev_hash: { type: "string", description: "Optional trusted anchor: the hash the first event must link to (\"GENESIS\" or a 64-character head_hash). When omitted the first event's own prev_hash is the anchor and is reported as anchor_prev_hash." },
        events: ARGUS_SEALED_EVENTS_SCHEMA
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
    title: "Telarch Inspector",
    description: "Render the interactive Telarch Inspector UI: three tabs for Harpe exact knapsack token packing, Kibisis epistemic memory conflict resolution, and Argus SHA-256 audit chain verification. Pass `items`, `records` or `events` to show data from this conversation: the Harpe tab packs the items exactly as harpe_synthesize_context does for the same arguments, the Kibisis tab resolves the records as kibisis_resolve_memory does, and the Argus tab shows the sealed events with the result of the argus_audit_verify check. A tab that is given no data shows built-in demonstration data, and every tab says which of the two it shows (also returned as data_source). The same limits and refusals apply as in those three tools. Nothing is stored.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { ...TOTAL_BUDGET, default: 3640, description: "Token budget for the Harpe tab. The default suits the demonstration items; with your own items pass the budget you pack against. As in harpe_synthesize_context, the reserves (3584 by default) come off it first; set them to 0 to pack into total_budget alone." },
        reserved_completion: { ...TOKEN_QUANTITY, default: 2048, description: "As in harpe_synthesize_context." },
        reserved_tools: { ...TOKEN_QUANTITY, default: 1024, description: "As in harpe_synthesize_context." },
        safety_margin: { ...TOKEN_QUANTITY, default: 512, description: "As in harpe_synthesize_context." },
        policy: { type: "string", enum: HARPE_POLICIES, default: "knapsack_dp", description: "As in harpe_synthesize_context." },
        items: { ...HARPE_ITEMS_SCHEMA, description: "Context items to show on the Harpe tab, oldest first, as in harpe_synthesize_context. An item's size is counted from its `content`; there is no field for giving a token count, so send the text itself. Left out: built-in demonstration items." },
        active_scope: { type: "string", default: "default", description: "Scope the records on the Kibisis tab are resolved in." },
        query: { type: "string", description: "Memory query for the Kibisis tab. Left out: \"SQLCipher encryption\" with the demonstration records, and an empty query (it matches every active record) with your own records." },
        records: { ...KIBISIS_RECORDS_SCHEMA, description: "Memory records to show on the Kibisis tab, as in kibisis_resolve_memory. Left out: three built-in demonstration records." },
        events: { ...ARGUS_SEALED_EVENTS_SCHEMA, description: "Sealed events to show on the Argus tab, in order and exactly as argus_audit_seal returned them. They go through the argus_audit_verify check before they are shown. Left out: a built-in demonstration chain." }
      },
      additionalProperties: false
    },
    annotations: {
      title: "Telarch Inspector",
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
  { id: "arch_decision", content: "Use the exact knapsack DP for deterministic context packing under budget.", priority: 10, pinned: false },
  { id: "stale_scratch", content: "Verbose historical debug trace from the deprecated prototype build: retry loop dumps, allocator statistics and unfiltered request logs, kept for reference only and safe to drop first.", priority: 85, pinned: false }
];

// How a kept item is labelled on the Harpe tab. The page has the same function (keptStatus).
function harpeKeptStatus(item, policy) {
  if (item.pinned) return "INCLUDED (PINNED)";
  if (item.priority === 0) return "INCLUDED (PRIORITY 0)";
  return policy === "knapsack_dp" ? "INCLUDED (KNAPSACK)" : `INCLUDED (${policy.toUpperCase()})`;
}

// Each tab shows what the call passed for it, run through the handler of the tool that owns that data, or
// the demonstration data when the call passed nothing for it. data_source says which, per tab.
async function runInspector(args) {
  const ownItems = args.items !== undefined;
  const ownRecords = args.records !== undefined;
  const ownEvents = args.events !== undefined;
  const sourceItems = ownItems ? args.items : INSPECTOR_DEMO_ITEMS;
  const reserves = harpeReserves(args);
  const harpeRes = await runHarpeSynthesize({
    total_budget: args.total_budget ?? 3640,
    ...reserves,
    policy: args.policy ?? "knapsack_dp",
    items: sourceItems
  });
  const scope = args.active_scope ?? "default";
  const kibisisRes = runKibisisResolve({
    active_scope: scope,
    requested_scope: scope,
    query: args.query ?? (ownRecords ? "" : "SQLCipher encryption"),
    records: ownRecords ? args.records : KIBISIS_DEMO_RECORDS
  });
  // Events from the call are checked, not sealed again: the panel must show a broken chain as broken.
  const argusRes = ownEvents
    ? await runArgusVerify({ events: args.events })
    : await runArgusSeal({
      events: [
        { event_type: "kibisis.lease.acquire", actor: "worker-a", payload: { fencing_token: 1, ttl_s: 30 }, timestamp: "2026-11-04T00:00:01Z" },
        { event_type: "harpe.context.pack", actor: "worker-a", payload: { consumed_tokens: harpeRes.consumed_tokens, savings_bp: harpeRes.tokens_saved_bp }, timestamp: "2026-11-04T00:00:02Z" },
        { event_type: "kibisis.vault.write", actor: "worker-a", payload: { fencing_token: 1, key: "db_engine_v2" }, timestamp: "2026-11-04T00:00:03Z" }
      ]
    });
  const keptById = new Map(harpeRes.included_items.map(i => [i.id, i]));
  const prunedById = new Map(harpeRes.pruned_items.map(i => [i.id, i]));
  return {
    status: "inspector_ready",
    data_source: {
      harpe: ownItems ? "request" : "demonstration",
      kibisis: ownRecords ? "request" : "demonstration",
      argus: ownEvents ? "request" : "demonstration"
    },
    harpe: {
      total_budget: harpeRes.total_budget,
      effective_budget: harpeRes.effective_budget,
      consumed_tokens: harpeRes.consumed_tokens,
      pruned_tokens: harpeRes.pruned_tokens,
      utilization_pct: harpeRes.utilization_pct,
      reserved_total: harpeRes.reserved_total,
      reserves_exceed_budget: harpeRes.reserves_exceed_budget,
      shortfall_tokens: harpeRes.shortfall_tokens,
      control_overflow: harpeRes.control_overflow,
      over_budget: harpeRes.over_budget,
      overflow_tokens: harpeRes.overflow_tokens,
      pinned_policy_digest: harpeRes.pinned_policy_digest,
      policy: harpeRes.policy_applied,
      reserves,
      // In the order the items were given: in harpe the position of an item is its age.
      items: sourceItems.map(src => (keptById.has(src.id)
        ? { ...keptById.get(src.id), status: harpeKeptStatus(keptById.get(src.id), harpeRes.policy_applied) }
        : { ...prunedById.get(src.id), status: "PRUNED" }))
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
// required, additionalProperties:false. Returns { path, problem } for the first violation (`problem` is a
// sentence that starts with the path), or null.
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
  const at = (where, problem) => ({ path: where, problem: `${where} ${problem}` });
  if (schema.type !== undefined) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some(t => schemaTypeMatches(t, value))) {
      const wanted = types.map(t => (t === "integer" ? "an integer (whole number within +/-(2**53 - 1))" : (t === "null" ? "null" : `of type ${t}`))).join(" or ");
      return at(path, `must be ${wanted}`);
    }
  }
  if (schema.enum !== undefined && !schema.enum.includes(value)) {
    return at(path, `must be one of: ${schema.enum.join(", ")}`);
  }
  if (typeof value === "number") {
    if (schema.minimum !== undefined && value < schema.minimum) return at(path, `must be >= ${schema.minimum}`);
    if (schema.maximum !== undefined && value > schema.maximum) return at(path, `must be <= ${schema.maximum}`);
  } else if (typeof value === "string") {
    if (schema.minLength !== undefined && value.length < schema.minLength) return at(path, `must have at least ${schema.minLength} character(s)`);
  } else if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) return at(path, `must have at least ${schema.minItems} item(s)`);
    if (schema.maxItems !== undefined && value.length > schema.maxItems) return at(path, `has ${value.length} items, above the limit of ${schema.maxItems}`);
    if (schema.items !== undefined) {
      for (let i = 0; i < value.length; i++) {
        const inner = schemaViolation(schema.items, value[i], `${path}[${i}]`);
        if (inner) return inner;
      }
    }
  } else if (isPlainObject(value)) {
    const properties = schema.properties || {};
    for (const name of schema.required || []) {
      if (!Object.hasOwn(value, name)) return at(`${path}.${name}`, "is required");
    }
    for (const name of Object.keys(value)) {
      if (Object.hasOwn(properties, name)) {
        const inner = schemaViolation(properties[name], value[name], `${path}.${name}`);
        if (inner) return inner;
      } else if (schema.additionalProperties === false) {
        return at(path, `has no property ${quoteName(name)}`);
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

function rpcError(id, code, message, data) {
  return { jsonrpc: "2.0", id, error: data === undefined ? { code, message } : { code, message, data } };
}

// "arguments.items[0].role" -> "items[0].role": the path as refusals of the tool handlers give it. The
// arguments object itself is "".
function argumentPath(path) {
  return path === "arguments" ? "" : path.replace(/^arguments\./, "");
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
    return rpcError(id, -32602, `Invalid arguments for tool ${name}: ${violation.problem}`, { code: "InvalidArguments", path: argumentPath(violation.path) });
  }
  let payload;
  try {
    payload = await MCP_TOOL_HANDLERS[name](args);
  } catch (err) {
    if (err instanceof TelarchRefusal) {
      return {
        jsonrpc: "2.0",
        id,
        result: {
          structuredContent: { error: { code: err.code, path: err.path, message: err.message } },
          content: [{ type: "text", text: err.message }],
          isError: true
        }
      };
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
          version: TELARCH_VERSION
        },
        instructions: "Stateless tools; nothing is stored between calls. Use harpe_synthesize_context for exact knapsack token packing (priority 0-100, lower = more important), kibisis_resolve_memory to resolve the memory records you pass in and frame them in an escaped <kibisis-recall> envelope, argus_audit_seal / argus_audit_verify for RFC 8785 SHA-256 audit chains (safe integers and strings only; no fractions), and telarch_open_inspector to show items, records or sealed events of the conversation (built-in demonstration data for a tab that is given none) in an interactive panel. A refused call carries a stable code and the path of the argument at fault: in structuredContent.error for a refusal by a tool, in error.data for arguments that do not match the schema. Arguments are checked against each tool's inputSchema; a call that does not match is refused."
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
            name: "Telarch Inspector",
            description: "Interactive 3-tab inspector for Harpe exact knapsack context packing, Kibisis epistemic memory conflict resolution, and Argus SHA-256 hash-chain verification.",
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
