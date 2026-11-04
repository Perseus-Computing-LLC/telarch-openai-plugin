// Telarch Streamable-HTTP MCP Server + Interactive MCP App UI (Cloudflare Edge)
// MIT License (c) 2026 Perseus Computing LLC

const OPENAI_APPS_CHALLENGE_TOKEN = "tvvlXj9ABL4IHa4f6ecObVVH3P-6FniKSZQ6xTuvDYw";

const INSPECTOR_URI = "ui://telarch/inspector-v1.html";

const INSPECTOR_HTML = "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>Telarch Cognitive Infrastructure Inspector</title>\n<style>\n  :root {\n    --bg: #0b101b;\n    --panel: #121a2b;\n    --border: #23324d;\n    --text: #e6edf7;\n    --muted: #8fa3c0;\n    --accent: #4da3ff;\n    --ok: #2ecc71;\n    --warn: #f39c12;\n    --err: #ff5c5c;\n    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;\n    --sans: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;\n  }\n  * { box-sizing: border-box; }\n  body {\n    margin: 0;\n    padding: 14px;\n    font-family: var(--sans);\n    background: var(--bg);\n    color: var(--text);\n    font-size: 13px;\n    line-height: 1.45;\n  }\n  .header {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    border-bottom: 1px solid var(--border);\n    padding-bottom: 10px;\n    margin-bottom: 12px;\n  }\n  .brand {\n    display: flex;\n    align-items: center;\n    gap: 8px;\n    font-weight: 700;\n    font-size: 14px;\n    letter-spacing: 0.02em;\n  }\n  .badge {\n    font-family: var(--mono);\n    font-size: 11px;\n    padding: 2px 7px;\n    border-radius: 4px;\n    background: rgba(77,163,255,0.14);\n    color: var(--accent);\n    border: 1px solid rgba(77,163,255,0.35);\n  }\n  .badge.ok { background: rgba(46,204,113,0.14); color: var(--ok); border-color: rgba(46,204,113,0.35); }\n  .badge.warn { background: rgba(243,156,18,0.14); color: var(--warn); border-color: rgba(243,156,18,0.35); }\n  .badge.err { background: rgba(255,92,92,0.14); color: var(--err); border-color: rgba(255,92,92,0.35); }\n  .tabs {\n    display: flex;\n    gap: 6px;\n    margin-bottom: 12px;\n  }\n  .tab {\n    flex: 1;\n    padding: 7px 10px;\n    background: var(--panel);\n    color: var(--muted);\n    border: 1px solid var(--border);\n    border-radius: 6px;\n    cursor: pointer;\n    font-weight: 600;\n    font-size: 12px;\n    text-align: center;\n  }\n  .tab.active {\n    color: var(--text);\n    border-color: var(--accent);\n    background: rgba(77,163,255,0.12);\n  }\n  .card {\n    background: var(--panel);\n    border: 1px solid var(--border);\n    border-radius: 8px;\n    padding: 12px;\n    margin-bottom: 10px;\n  }\n  .row {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    gap: 8px;\n    margin-bottom: 8px;\n  }\n  .bar-wrap {\n    height: 12px;\n    background: #080c14;\n    border-radius: 6px;\n    overflow: hidden;\n    border: 1px solid var(--border);\n    margin: 8px 0;\n  }\n  .bar-fill {\n    height: 100%;\n    background: linear-gradient(90deg, #2b7de9, #2ecc71);\n    transition: width 0.2s ease;\n  }\n  .item-list {\n    display: flex;\n    flex-direction: column;\n    gap: 6px;\n    margin-top: 8px;\n  }\n  .item {\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    padding: 6px 8px;\n    border-radius: 5px;\n    background: #0d1422;\n    border: 1px solid var(--border);\n    font-size: 12px;\n  }\n  .mono { font-family: var(--mono); font-size: 11px; color: var(--muted); word-break: break-all; }\n  button.btn {\n    background: #1b6ef3;\n    color: #fff;\n    border: none;\n    border-radius: 5px;\n    padding: 6px 11px;\n    font-size: 12px;\n    font-weight: 600;\n    cursor: pointer;\n  }\n  button.btn.secondary {\n    background: transparent;\n    border: 1px solid var(--border);\n    color: var(--text);\n  }\n  button.btn.danger {\n    background: rgba(255,92,92,0.18);\n    border: 1px solid rgba(255,92,92,0.45);\n    color: var(--err);\n  }\n  input[type=\"range\"] { width: 160px; }\n  .hidden { display: none; }\n</style>\n</head>\n<body>\n  <div class=\"header\">\n    <div class=\"brand\">\n      <span>TELARCH</span>\n      <span class=\"badge\">Kibisis \u00b7 Harpe \u00b7 Argus</span>\n    </div>\n    <span id=\"status-badge\" class=\"badge ok\">MCP Ready</span>\n  </div>\n\n  <div class=\"tabs\">\n    <button class=\"tab active\" data-tab=\"harpe\">Harpe 0/1 Knapsack</button>\n    <button class=\"tab\" data-tab=\"kibisis\">Kibisis Memory</button>\n    <button class=\"tab\" data-tab=\"argus\">Argus SHA-256 Chain</button>\n  </div>\n\n  <!-- TAB 1: HARPE -->\n  <div id=\"panel-harpe\" class=\"panel\">\n    <div class=\"card\">\n      <div class=\"row\">\n        <strong>0/1 Knapsack Context Budgeter</strong>\n        <div>\n          <label for=\"budget-slider\" class=\"mono\">Total Budget: <span id=\"budget-val\">3600</span> tok</label>\n          <input id=\"budget-slider\" type=\"range\" min=\"3580\" max=\"3750\" step=\"5\" value=\"3640\">\n        </div>\n      </div>\n      <div class=\"bar-wrap\"><div id=\"harpe-bar\" class=\"bar-fill\" style=\"width: 72%\"></div></div>\n      <div class=\"row mono\">\n        <span id=\"harpe-summary\">Effective: 56 tokens | Consumed: 42 tokens (75.0%)</span>\n        <button id=\"btn-repack\" class=\"btn\">Re-Pack via MCP</button>\n      </div>\n      <div class=\"mono\" style=\"margin-top:4px\">Policy Digest: <span id=\"harpe-digest\">sha256:8f9c...</span></div>\n      <div id=\"harpe-items\" class=\"item-list\"></div>\n    </div>\n  </div>\n\n  <!-- TAB 2: KIBISIS -->\n  <div id=\"panel-kibisis\" class=\"panel hidden\">\n    <div class=\"card\">\n      <div class=\"row\">\n        <strong>Epistemic Vault &amp; Conflict Resolution</strong>\n        <button id=\"btn-recall\" class=\"btn\">Resolve Conflicts via MCP</button>\n      </div>\n      <div class=\"mono\" id=\"kibisis-meta\">Scope: default | Active Filter: verified + candidate (revoked &amp; superseded excluded)</div>\n      <div id=\"kibisis-items\" class=\"item-list\"></div>\n      <pre id=\"kibisis-envelope\" class=\"mono\" style=\"background:#080c14;padding:8px;border-radius:5px;border:1px solid var(--border);margin-top:8px;white-space:pre-wrap;\"></pre>\n    </div>\n  </div>\n\n  <!-- TAB 3: ARGUS -->\n  <div id=\"panel-argus\" class=\"panel hidden\">\n    <div class=\"card\">\n      <div class=\"row\">\n        <strong>RFC 8785 Canonical JSON SHA-256 Audit Chain</strong>\n        <div style=\"display:flex;gap:6px;\">\n          <button id=\"btn-tamper\" class=\"btn danger\">Simulate Mid-Chain Tamper</button>\n          <button id=\"btn-verify\" class=\"btn\">Verify Chain via MCP</button>\n        </div>\n      </div>\n      <div id=\"argus-banner\" class=\"badge ok\" style=\"display:inline-block;margin-bottom:8px;\">CHAIN VALID \u2014 3/3 Events Cryptographically Verified from GENESIS</div>\n      <div id=\"argus-events\" class=\"item-list\"></div>\n    </div>\n  </div>\n\n<script type=\"module\">\n  // Default authoritative state\n  let state = {\n    harpe: {\n      total_budget: 3640,\n      effective_budget: 56,\n      consumed_tokens: 34,\n      pruned_tokens: 18,\n      utilization_pct: 60.71,\n      pinned_policy_digest: \"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\",\n      items: [\n        { id: \"sys_invariants\", content: \"Enforce SQLCipher encryption and monotonic fencing tokens on every write.\", priority: 100, pinned: true, status: \"INCLUDED (PINNED)\", tokens: 16 },\n        { id: \"arch_decision\", content: \"Use Rust 0/1 knapsack DP for deterministic context packing under budget.\", priority: 90, pinned: false, status: \"INCLUDED (KNAPSACK)\", tokens: 18 },\n        { id: \"stale_scratch\", content: \"Verbose historical debug trace from deprecated prototype build.\", priority: 15, pinned: false, status: \"PRUNED\", tokens: 18 }\n      ]\n    },\n    kibisis: {\n      active_scope: \"default\",\n      query: \"deployment database\",\n      records: [\n        { key: \"db_engine_v1\", category: \"decision\", content: \"Use unencrypted SQLite for local storage.\", epistemic_state: \"verified\", status: \"SUPERSEDED by db_engine_v2\" },\n        { key: \"db_engine_v2\", category: \"decision\", content: \"Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).\", epistemic_state: \"verified\", supersedes_key: \"db_engine_v1\", status: \"ACTIVE\" },\n        { key: \"temp_override\", category: \"convention\", content: \"Allow plaintext fallback in production.\", epistemic_state: \"revoked\", status: \"TOMBSTONED (REVOKED)\" }\n      ],\n      envelope: '<kibisis-recall trust=\"untrusted-stored-text\" scope=\"default\">\\\\n- [decision/db_engine_v2] (verified): Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).\\\\n</kibisis-recall>'\n    },\n    argus: {\n      valid: true,\n      first_broken_sequence: null,\n      error_detail: null,\n      events: [\n        { sequence: 1, event_id: \"evt_01\", event_type: \"kibisis.lease.acquire\", actor: \"worker-a\", payload: { fencing_token: 1, ttl_s: 30 }, timestamp: \"2026-11-04T00:00:01Z\", prev_hash: \"GENESIS\", event_hash: \"a7c4...\" },\n        { sequence: 2, event_id: \"evt_02\", event_type: \"harpe.context.pack\", actor: \"worker-a\", payload: { consumed_tokens: 34, savings_bp: 6540 }, timestamp: \"2026-11-04T00:00:02Z\", prev_hash: \"a7c4...\", event_hash: \"d91e...\" },\n        { sequence: 3, event_id: \"evt_03\", event_type: \"kibisis.vault.write\", actor: \"worker-a\", payload: { fencing_token: 1, key: \"db_engine_v2\" }, timestamp: \"2026-11-04T00:00:03Z\", prev_hash: \"d91e...\", event_hash: \"f04b...\" }\n      ]\n    }\n  };\n\n  // Tab switching\n  document.querySelectorAll(\".tab\").forEach(btn => {\n    btn.addEventListener(\"click\", () => {\n      document.querySelectorAll(\".tab\").forEach(b => b.classList.remove(\"active\"));\n      document.querySelectorAll(\".panel\").forEach(p => p.classList.add(\"hidden\"));\n      btn.classList.add(\"active\");\n      document.getElementById(\"panel-\" + btn.dataset.tab).classList.remove(\"hidden\");\n    });\n  });\n\n  // JSON-RPC 2.0 MCP Apps postMessage bridge\n  let rpcId = 1;\n  const pending = new Map();\n\n  window.addEventListener(\"message\", (ev) => {\n    const msg = ev.data;\n    if (!msg || typeof msg !== \"object\") return;\n    if (msg.id && pending.has(msg.id)) {\n      const { resolve } = pending.get(msg.id);\n      pending.delete(msg.id);\n      resolve(msg.result || msg.error);\n      return;\n    }\n    if (msg.method === \"ui/notifications/tool-result\" && msg.params?.structuredContent) {\n      applyServerPayload(msg.params.structuredContent);\n    }\n  });\n\n  function sendRpc(method, params) {\n    return new Promise((resolve) => {\n      const id = rpcId++;\n      pending.set(id, { resolve });\n      window.parent.postMessage({ jsonrpc: \"2.0\", id, method, params }, \"*\");\n      setTimeout(() => {\n        if (pending.has(id)) {\n          pending.delete(id);\n          resolve(null);\n        }\n      }, 2500);\n    });\n  }\n\n  async function callMcpTool(name, args) {\n    const statusBadge = document.getElementById(\"status-badge\");\n    statusBadge.textContent = \"Calling \" + name + \"\u2026\";\n    statusBadge.className = \"badge warn\";\n    if (window.openai?.callTool) {\n      try {\n        const res = await window.openai.callTool(name, args);\n        if (res?.structuredContent) applyServerPayload(res.structuredContent);\n        statusBadge.textContent = \"MCP Synced\";\n        statusBadge.className = \"badge ok\";\n        return res;\n      } catch (_) {}\n    }\n    const rpcRes = await sendRpc(\"tools/call\", { name, arguments: args });\n    if (rpcRes?.structuredContent) {\n      applyServerPayload(rpcRes.structuredContent);\n      statusBadge.textContent = \"MCP Synced\";\n      statusBadge.className = \"badge ok\";\n      return rpcRes;\n    }\n    // Direct fallback to https://telarch.ai/mcp when running standalone\n    try {\n      const r = await fetch(\"https://telarch.ai/mcp\", {\n        method: \"POST\",\n        headers: { \"Content-Type\": \"application/json\" },\n        body: JSON.stringify({ jsonrpc: \"2.0\", id: rpcId++, method: \"tools/call\", params: { name, arguments: args } })\n      });\n      const j = await r.json();\n      if (j?.result?.structuredContent) applyServerPayload(j.result.structuredContent);\n      statusBadge.textContent = \"MCP Synced\";\n      statusBadge.className = \"badge ok\";\n    } catch (_) {\n      statusBadge.textContent = \"Local Preview\";\n      statusBadge.className = \"badge ok\";\n    }\n  }\n\n  function applyServerPayload(sc) {\n    if (!sc) return;\n    if (sc.harpe) state.harpe = sc.harpe;\n    if (sc.kibisis) state.kibisis = sc.kibisis;\n    if (sc.argus) state.argus = sc.argus;\n    if (sc.policy_applied && sc.included_items) {\n      state.harpe = {\n        total_budget: sc.total_budget,\n        effective_budget: sc.effective_budget,\n        consumed_tokens: sc.consumed_tokens,\n        pruned_tokens: sc.pruned_tokens,\n        utilization_pct: sc.utilization_pct,\n        pinned_policy_digest: sc.pinned_policy_digest,\n        items: [\n          ...sc.included_items.map(i => ({ ...i, status: i.pinned ? \"INCLUDED (PINNED)\" : \"INCLUDED (KNAPSACK)\" })),\n          ...sc.pruned_items.map(i => ({ ...i, status: \"PRUNED\" }))\n        ]\n      };\n    }\n    if (sc.envelope && sc.resolved_records) {\n      state.kibisis = {\n        active_scope: sc.active_scope,\n        query: sc.query,\n        records: sc.all_records_trace || sc.resolved_records,\n        envelope: sc.envelope\n      };\n    }\n    if (typeof sc.valid === \"boolean\" && sc.events) {\n      state.argus = sc;\n    }\n    render();\n  }\n\n  function render() {\n    // Render Harpe\n    const h = state.harpe;\n    document.getElementById(\"budget-val\").textContent = h.total_budget;\n    const pct = Math.min(100, Math.max(0, h.utilization_pct || 0));\n    document.getElementById(\"harpe-bar\").style.width = pct + \"%\";\n    document.getElementById(\"harpe-summary\").textContent =\n      `Effective: ${h.effective_budget} tok | Consumed: ${h.consumed_tokens} tok (${pct.toFixed(1)}%) | Pruned: ${h.pruned_tokens} tok`;\n    document.getElementById(\"harpe-digest\").textContent = \"sha256:\" + String(h.pinned_policy_digest).slice(0, 24) + \"\u2026\";\n    const hList = document.getElementById(\"harpe-items\");\n    hList.innerHTML = \"\";\n    (h.items || []).forEach(it => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const cls = it.status.startsWith(\"INCLUDED\") ? \"ok\" : \"warn\";\n      div.innerHTML = `<div><strong>${it.id}</strong> (prio ${it.priority}, ${it.tokens || \"?\"} tok)<div class=\"mono\">${it.content}</div></div><span class=\"badge ${cls}\">${it.status}</span>`;\n      hList.appendChild(div);\n    });\n\n    // Render Kibisis\n    const k = state.kibisis;\n    const kList = document.getElementById(\"kibisis-items\");\n    kList.innerHTML = \"\";\n    (k.records || []).forEach(rec => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const cls = rec.status === \"ACTIVE\" ? \"ok\" : (rec.status.includes(\"TOMBSTONE\") ? \"err\" : \"warn\");\n      div.innerHTML = `<div><strong>${rec.category}/${rec.key}</strong> [${rec.epistemic_state}]<div class=\"mono\">${rec.content}</div></div><span class=\"badge ${cls}\">${rec.status}</span>`;\n      kList.appendChild(div);\n    });\n    document.getElementById(\"kibisis-envelope\").textContent = k.envelope || \"\";\n\n    // Render Argus\n    const a = state.argus;\n    const banner = document.getElementById(\"argus-banner\");\n    if (a.valid) {\n      banner.className = \"badge ok\";\n      banner.textContent = `CHAIN VALID \u2014 ${a.events.length}/${a.events.length} Events Verified from GENESIS (Head: ${String(a.head_hash || \"\").slice(0, 16)}\u2026)`;\n    } else {\n      banner.className = \"badge err\";\n      banner.textContent = `TAMPER DETECTED AT SEQ #${a.first_broken_sequence}: ${a.error_detail}`;\n    }\n    const aList = document.getElementById(\"argus-events\");\n    aList.innerHTML = \"\";\n    (a.events || []).forEach(ev => {\n      const div = document.createElement(\"div\");\n      div.className = \"item\";\n      const broken = !a.valid && a.first_broken_sequence === ev.sequence;\n      div.innerHTML = `<div><strong>#${ev.sequence} ${ev.event_type}</strong> (${ev.actor})<div class=\"mono\">payload: ${JSON.stringify(ev.payload)}</div><div class=\"mono\">prev: ${String(ev.prev_hash).slice(0,16)}\u2026 \u2192 hash: ${String(ev.event_hash).slice(0,16)}\u2026</div></div><span class=\"badge ${broken ? 'err' : 'ok'}\">${broken ? 'HASH MISMATCH' : 'SEALED'}</span>`;\n      aList.appendChild(div);\n    });\n  }\n\n  document.getElementById(\"budget-slider\").addEventListener(\"input\", (e) => {\n    document.getElementById(\"budget-val\").textContent = e.target.value;\n  });\n\n  document.getElementById(\"btn-repack\").addEventListener(\"click\", () => {\n    const totalBudget = parseInt(document.getElementById(\"budget-slider\").value, 10);\n    callMcpTool(\"harpe_synthesize_context\", {\n      total_budget: totalBudget,\n      policy: \"knapsack_dp\",\n      items: [\n        { id: \"sys_invariants\", content: \"Enforce SQLCipher encryption and monotonic fencing tokens on every write.\", priority: 100, pinned: true },\n        { id: \"arch_decision\", content: \"Use Rust 0/1 knapsack DP for deterministic context packing under budget.\", priority: 90, pinned: false },\n        { id: \"stale_scratch\", content: \"Verbose historical debug trace from deprecated prototype build.\", priority: 15, pinned: false }\n      ]\n    });\n  });\n\n  document.getElementById(\"btn-recall\").addEventListener(\"click\", () => {\n    callMcpTool(\"kibisis_resolve_memory\", {\n      active_scope: \"default\",\n      requested_scope: \"default\",\n      query: \"SQLCipher encryption\",\n      records: state.kibisis.records\n    });\n  });\n\n  document.getElementById(\"btn-tamper\").addEventListener(\"click\", () => {\n    const tampered = JSON.parse(JSON.stringify(state.argus.events));\n    if (tampered.length >= 2) {\n      tampered[1].payload.savings_bp = 9999; // Mutate payload without re-sealing hash chain\n    }\n    callMcpTool(\"argus_audit_verify\", { events: tampered });\n  });\n\n  document.getElementById(\"btn-verify\").addEventListener(\"click\", () => {\n    callMcpTool(\"argus_audit_seal\", {\n      events: [\n        { event_type: \"kibisis.lease.acquire\", actor: \"worker-a\", payload: { fencing_token: 1, ttl_s: 30 }, timestamp: \"2026-11-04T00:00:01Z\" },\n        { event_type: \"harpe.context.pack\", actor: \"worker-a\", payload: { consumed_tokens: 34, savings_bp: 6540 }, timestamp: \"2026-11-04T00:00:02Z\" },\n        { event_type: \"kibisis.vault.write\", actor: \"worker-a\", payload: { fencing_token: 1, key: \"db_engine_v2\" }, timestamp: \"2026-11-04T00:00:03Z\" }\n      ]\n    });\n  });\n\n  // Initialize bridge & render\n  if (window.openai?.toolOutput) {\n    applyServerPayload(window.openai.toolOutput);\n  } else {\n    render();\n  }\n  sendRpc(\"ui/initialize\", {\n    protocolVersion: \"2025-06-18\",\n    appInfo: { name: \"Telarch Inspector\", version: \"0.1.0\" },\n    appCapabilities: {}\n  }).then(() => {\n    window.parent.postMessage({ jsonrpc: \"2.0\", method: \"ui/notifications/initialized\", params: {} }, \"*\");\n  });\n</script>\n</body>\n</html>";

// Deterministic token estimator matching Harpe HeuristicTokenCounter (~4 chars/token + framing)
function countTokens(text) {
  const s = String(text || "");
  if (!s) return 0;
  const words = s.trim().split(/\s+/).filter(Boolean).length;
  const charEst = Math.ceil(s.length / 4);
  return Math.max(1, Math.ceil((words * 1.3 + charEst) / 2));
}

// WebCrypto SHA-256 hex digest
async function sha256Hex(input) {
  const bytes = new TextEncoder().encode(String(input));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, "0")).join("");
}

// RFC 8785 (JCS) canonical JSON serializer with strict float rejection (Argus invariant)
function canonicalizeJson(val, path = "payload") {
  if (val === null) return "null";
  const t = typeof val;
  if (t === "boolean") return val ? "true" : "false";
  if (t === "number") {
    if (!Number.isFinite(val) || !Number.isInteger(val)) {
      throw new Error(`FloatPayloadError at ${path}: non-integer number ${val} is rejected for canonical SHA-256 hashing; express fractions as integer basis points (*_bp).`);
    }
    return String(val);
  }
  if (t === "string") return JSON.stringify(val);
  if (Array.isArray(val)) {
    return "[" + val.map((item, idx) => canonicalizeJson(item, `${path}[${idx}]`)).join(",") + "]";
  }
  if (t === "object") {
    const keys = Object.keys(val).sort();
    return "{" + keys.map(k => JSON.stringify(k) + ":" + canonicalizeJson(val[k], `${path}.${k}`)).join(",") + "}";
  }
  throw new Error(`Unsupported JSON type at ${path}: ${t}`);
}

// Exact 0/1 Knapsack DP + priority context synthesizer (Harpe)
async function runHarpeSynthesize(args) {
  const totalBudget = Number(args.total_budget ?? 4096);
  const reservedCompletion = Number(args.reserved_completion ?? 2048);
  const reservedTools = Number(args.reserved_tools ?? 1024);
  const safetyMargin = Number(args.safety_margin ?? 512);
  const policy = String(args.policy || "knapsack_dp");
  const effectiveBudget = Math.max(0, totalBudget - reservedCompletion - reservedTools - safetyMargin);

  const rawItems = Array.isArray(args.items) ? args.items : [];
  const items = rawItems.map((it, idx) => ({
    id: String(it.id ?? `item_${idx}`),
    content: String(it.content ?? ""),
    role: String(it.role ?? "context"),
    priority: Number.isInteger(it.priority) ? it.priority : Number(it.priority ?? 50),
    pinned: Boolean(it.pinned),
    tokens: countTokens(it.content ?? "")
  }));

  const pinnedItems = items.filter(i => i.pinned);
  const unpinnedItems = items.filter(i => !i.pinned);

  let consumedTokens = 0;
  const includedItems = [];
  const prunedItems = [];
  let controlOverflow = false;

  for (const p of pinnedItems) {
    if (consumedTokens + p.tokens <= effectiveBudget) {
      includedItems.push(p);
      consumedTokens += p.tokens;
    } else {
      controlOverflow = true;
      prunedItems.push(p);
    }
  }

  const remainingBudget = Math.max(0, effectiveBudget - consumedTokens);

  if (policy === "knapsack_dp" && unpinnedItems.length > 0 && remainingBudget > 0) {
    const n = unpinnedItems.length;
    const cap = Math.min(remainingBudget, 8192);
    // Exact 0/1 DP table over token weights and priority values
    const dp = Array.from({ length: n + 1 }, () => new Int32Array(cap + 1));
    for (let i = 1; i <= n; i++) {
      const w = unpinnedItems[i - 1].tokens;
      const v = Math.max(1, unpinnedItems[i - 1].priority);
      for (let c = 0; c <= cap; c++) {
        dp[i][c] = dp[i - 1][c];
        if (w <= c && dp[i - 1][c - w] + v > dp[i][c]) {
          dp[i][c] = dp[i - 1][c - w] + v;
        }
      }
    }
    let c = cap;
    const chosen = new Set();
    for (let i = n; i >= 1; i--) {
      if (dp[i][c] !== dp[i - 1][c]) {
        chosen.add(i - 1);
        c -= unpinnedItems[i - 1].tokens;
      }
    }
    unpinnedItems.forEach((it, idx) => {
      if (chosen.has(idx)) {
        includedItems.push(it);
        consumedTokens += it.tokens;
      } else {
        prunedItems.push(it);
      }
    });
  } else {
    const sorted = [...unpinnedItems].sort((a, b) => b.priority - a.priority);
    for (const it of sorted) {
      if (consumedTokens + it.tokens <= effectiveBudget) {
        includedItems.push(it);
        consumedTokens += it.tokens;
      } else {
        prunedItems.push(it);
      }
    }
  }

  const prunedTokens = prunedItems.reduce((acc, i) => acc + i.tokens, 0);
  const totalCandidateTokens = consumedTokens + prunedTokens;
  const tokensSavedBp = totalCandidateTokens > 0 ? Math.round((prunedTokens / totalCandidateTokens) * 10000) : 0;
  const utilizationPct = effectiveBudget > 0 ? Number(((consumedTokens / effectiveBudget) * 100).toFixed(2)) : 0;
  const digestInput = JSON.stringify({
    policy,
    effectiveBudget,
    included: includedItems.map(i => i.id),
    pruned: prunedItems.map(i => i.id)
  });
  const pinnedPolicyDigest = await sha256Hex(digestInput);

  return {
    policy_applied: policy,
    total_budget: totalBudget,
    effective_budget: effectiveBudget,
    consumed_tokens: consumedTokens,
    pruned_tokens: prunedTokens,
    utilization_pct: utilizationPct,
    tokens_saved_bp: tokensSavedBp,
    control_overflow: controlOverflow,
    pinned_policy_digest: pinnedPolicyDigest,
    included_ids: includedItems.map(i => i.id),
    pruned_ids: prunedItems.map(i => i.id),
    included_items: includedItems,
    pruned_items: prunedItems
  };
}

// Epistemic memory resolver & conflict filter (Kibisis)
function runKibisisResolve(args) {
  const activeScope = String(args.active_scope || "default");
  const requestedScope = String(args.requested_scope || activeScope);
  if (requestedScope !== activeScope) {
    throw new Error(`ScopeIsolationError: cross-scope memory access denied (requested_scope='${requestedScope}' != active_scope='${activeScope}').`);
  }
  if (args.write_attempt && args.write_attempt.origin === "model" && args.write_attempt.epistemic_state === "verified") {
    throw new Error("EpistemicTrustViolation: model-originated writes cannot self-promote to epistemic_state='verified'; store as 'candidate' for human review.");
  }

  const query = String(args.query || "").toLowerCase().trim();
  const queryTerms = query.split(/\s+/).filter(Boolean);
  const rawRecords = Array.isArray(args.records) && args.records.length > 0 ? args.records : [
    { key: "db_engine_v1", category: "decision", content: "Use unencrypted SQLite for local storage.", epistemic_state: "verified" },
    { key: "db_engine_v2", category: "decision", content: "Use SQLCipher AES-256 with PBKDF2-HMAC-SHA512 (256,000 iterations).", epistemic_state: "verified", supersedes_key: "db_engine_v1" },
    { key: "temp_override", category: "convention", content: "Allow plaintext fallback in production.", epistemic_state: "revoked" }
  ];

  const supersededKeys = new Set(rawRecords.map(r => r.supersedes_key).filter(Boolean));
  const trace = [];
  const activeRecords = [];

  for (const r of rawRecords) {
    const key = String(r.key || "unnamed");
    const category = String(r.category || "general");
    const content = String(r.content || "");
    const state = String(r.epistemic_state || "candidate");
    if (state === "revoked") {
      trace.push({ key, category, content, epistemic_state: state, status: "TOMBSTONED (REVOKED)" });
      continue;
    }
    if (supersededKeys.has(key)) {
      trace.push({ key, category, content, epistemic_state: state, status: "SUPERSEDED" });
      continue;
    }
    const textLower = `${key} ${category} ${content}`.toLowerCase();
    const hits = queryTerms.length === 0 ? 1 : queryTerms.filter(t => textLower.includes(t)).length;
    if (hits > 0 || queryTerms.length === 0) {
      activeRecords.push({ key, category, content, epistemic_state: state, match_score: hits, status: "ACTIVE" });
    }
    trace.push({ key, category, content, epistemic_state: state, status: "ACTIVE" });
  }

  const lines = activeRecords.map(r => `- [${r.category}/${r.key}] (${r.epistemic_state}): ${r.content}`);
  const envelope = `<kibisis-recall trust="untrusted-stored-text" scope="${activeScope}">\n` +
    (lines.length ? lines.join("\n") : "(no matching active records)") +
    `\n</kibisis-recall>`;

  return {
    active_scope: activeScope,
    query: args.query || "",
    resolved_count: activeRecords.length,
    resolved_records: activeRecords,
    all_records_trace: trace,
    envelope
  };
}

// Argus RFC 8785 canonical JSON SHA-256 chain sealer & verifier
async function runArgusSeal(args) {
  const rawEvents = Array.isArray(args.events) ? args.events : [];
  let prevHash = String(args.prev_hash || "GENESIS");
  const sealed = [];
  for (let i = 0; i < rawEvents.length; i++) {
    const ev = rawEvents[i];
    const seq = Number.isInteger(ev.sequence) ? ev.sequence : i + 1;
    const eventId = String(ev.event_id || `evt_${String(seq).padStart(4, "0")}`);
    const eventType = String(ev.event_type || "agent.action");
    const actor = String(ev.actor || "agent");
    const timestamp = String(ev.timestamp || "2026-11-04T00:00:00Z");
    const payload = ev.payload ?? {};
    const canonicalPayload = canonicalizeJson(payload);
    const canonicalEnvelope = canonicalizeJson({
      actor,
      event_id: eventId,
      event_type: eventType,
      payload,
      prev_hash: prevHash,
      sequence: seq,
      timestamp
    });
    const eventHash = await sha256Hex(canonicalEnvelope);
    sealed.push({
      sequence: seq,
      event_id: eventId,
      event_type: eventType,
      actor,
      timestamp,
      payload,
      canonical_payload: canonicalPayload,
      prev_hash: prevHash,
      event_hash: eventHash
    });
    prevHash = eventHash;
  }
  return {
    valid: true,
    total_events: sealed.length,
    root_hash: sealed.length > 0 ? sealed[0].event_hash : null,
    head_hash: sealed.length > 0 ? sealed[sealed.length - 1].event_hash : null,
    first_broken_sequence: null,
    error_detail: null,
    events: sealed
  };
}

async function runArgusVerify(args) {
  const events = Array.isArray(args.events) ? args.events : [];
  let expectedPrev = "GENESIS";
  for (let i = 0; i < events.length; i++) {
    const ev = events[i];
    const seq = Number.isInteger(ev.sequence) ? ev.sequence : i + 1;
    if (ev.prev_hash !== expectedPrev) {
      return {
        valid: false,
        total_events: events.length,
        root_hash: events[0]?.event_hash || null,
        head_hash: events[events.length - 1]?.event_hash || null,
        first_broken_sequence: seq,
        error_detail: `prev_hash mismatch at sequence ${seq}: expected ${expectedPrev}, found ${ev.prev_hash}`,
        events
      };
    }
    const canonicalEnvelope = canonicalizeJson({
      actor: String(ev.actor || "agent"),
      event_id: String(ev.event_id || `evt_${String(seq).padStart(4, "0")}`),
      event_type: String(ev.event_type || "agent.action"),
      payload: ev.payload ?? {},
      prev_hash: expectedPrev,
      sequence: seq,
      timestamp: String(ev.timestamp || "2026-11-04T00:00:00Z")
    });
    const computedHash = await sha256Hex(canonicalEnvelope);
    if (ev.event_hash !== computedHash) {
      return {
        valid: false,
        total_events: events.length,
        root_hash: events[0]?.event_hash || null,
        head_hash: events[events.length - 1]?.event_hash || null,
        first_broken_sequence: seq,
        error_detail: `SHA-256 digest mismatch at sequence ${seq}: recorded ${ev.event_hash}, computed ${computedHash}`,
        events
      };
    }
    expectedPrev = computedHash;
  }
  return {
    valid: true,
    total_events: events.length,
    root_hash: events.length > 0 ? events[0].event_hash : null,
    head_hash: events.length > 0 ? events[events.length - 1].event_hash : null,
    first_broken_sequence: null,
    error_detail: null,
    events
  };
}

const MCP_TOOLS = [
  {
    name: "harpe_synthesize_context",
    title: "Synthesize & Prune Context (0/1 Knapsack)",
    description: "Use this when you need to pack candidate context items deterministically into a strict token budget using Harpe's 0/1 knapsack dynamic programming or priority pruning.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { type: "integer", description: "Total model context budget in tokens.", default: 4096 },
        reserved_completion: { type: "integer", description: "Tokens reserved for completion output.", default: 2048 },
        reserved_tools: { type: "integer", description: "Tokens reserved for tool schemas.", default: 1024 },
        safety_margin: { type: "integer", description: "Safety margin buffer in tokens.", default: 512 },
        policy: {
          type: "string",
          enum: ["knapsack_dp", "lowest_priority", "fifo", "warm_prefix"],
          default: "knapsack_dp",
          description: "Pruning policy to apply after locking pinned items."
        },
        items: {
          type: "array",
          description: "Candidate context items to pack.",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              content: { type: "string" },
              role: { type: "string", default: "context" },
              priority: { type: "integer", default: 50 },
              pinned: { type: "boolean", default: false }
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
        total_budget: { type: "integer", description: "Total context window size in tokens." },
        reserved_completion: { type: "integer", default: 2048 },
        reserved_tools: { type: "integer", default: 1024 },
        safety_margin: { type: "integer", default: 512 },
        current_usage: { type: "integer", default: 0 }
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
    description: "Use this to resolve active memories across superseded and revoked (tombstoned) records, enforce strict tenant scope isolation and candidate-vs-verified epistemic trust gates, and format the prompt-injection-safe <kibisis-recall> envelope.",
    inputSchema: {
      type: "object",
      properties: {
        active_scope: { type: "string", default: "default", description: "Active workspace/tenant scope." },
        requested_scope: { type: "string", default: "default", description: "Requested scope (must match active_scope)." },
        query: { type: "string", description: "Search keywords to match against active memory records." },
        write_attempt: {
          type: "object",
          description: "Optional write gate evaluation (checks epistemic_state escalation rules).",
          properties: {
            origin: { type: "string", enum: ["model", "user"] },
            epistemic_state: { type: "string", enum: ["candidate", "verified", "disputed", "revoked"] }
          },
          additionalProperties: false
        },
        records: {
          type: "array",
          description: "Memory records to resolve across supersession and revocation chains.",
          items: {
            type: "object",
            properties: {
              key: { type: "string" },
              category: { type: "string", default: "decision" },
              content: { type: "string" },
              epistemic_state: { type: "string", enum: ["candidate", "verified", "disputed", "revoked"], default: "candidate" },
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
    description: "Use this to evaluate whether a concurrent agent holder's fencing token and lease TTL permit a vault mutation or must be rejected to prevent split-brain writes.",
    inputSchema: {
      type: "object",
      properties: {
        resource: { type: "string", default: "vault:default" },
        holder_id: { type: "string", description: "Agent worker identifier." },
        fencing_token: { type: "integer", description: "Holder's fencing token." },
        highest_token_seen: { type: "integer", description: "Highest monotonic fencing token recorded by the vault." },
        lease_expires_epoch: { type: "integer", description: "Lease expiration Unix timestamp (whole seconds)." },
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
    description: "Use this to compute canonical RFC 8785 (JCS) JSON and linear SHA-256 hash-chain digests from GENESIS for a sequence of agent audit events. Rejects floating-point numbers (use integer basis points *_bp).",
    inputSchema: {
      type: "object",
      properties: {
        prev_hash: { type: "string", default: "GENESIS" },
        events: {
          type: "array",
          items: {
            type: "object",
            properties: {
              sequence: { type: "integer" },
              event_id: { type: "string" },
              event_type: { type: "string" },
              actor: { type: "string" },
              timestamp: { type: "string" },
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
    description: "Use this to cryptographically verify a linear SHA-256 Argus audit chain from GENESIS and isolate the exact sequence number of any mid-chain tampering.",
    inputSchema: {
      type: "object",
      properties: {
        events: {
          type: "array",
          items: {
            type: "object",
            properties: {
              sequence: { type: "integer" },
              event_id: { type: "string" },
              event_type: { type: "string" },
              actor: { type: "string" },
              timestamp: { type: "string" },
              payload: { type: "object" },
              prev_hash: { type: "string" },
              event_hash: { type: "string" }
            },
            required: ["event_type", "actor", "payload", "prev_hash", "event_hash"],
            additionalProperties: true
          }
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
    description: "Render the interactive Telarch Inspector UI for exploring Harpe 0/1 knapsack token packing, Kibisis epistemic memory conflict resolution, and Argus SHA-256 audit chain verification.",
    inputSchema: {
      type: "object",
      properties: {
        total_budget: { type: "integer", default: 3640, description: "Initial token budget for the Harpe inspector tab." },
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

async function handleMcpRpcSingle(req) {
  if (!req || typeof req !== "object") {
    return { jsonrpc: "2.0", id: null, error: { code: -32600, message: "Invalid Request" } };
  }
  const id = req.id;
  const method = req.method;
  const params = req.params || {};

  // JSON-RPC notifications have no id
  if (id === undefined) {
    return null;
  }

  if (method === "initialize") {
    const requestedVersion = String(params.protocolVersion || "2025-06-18");
    const supported = ["2024-11-05", "2025-03-26", "2025-06-18"];
    const protocolVersion = supported.includes(requestedVersion) ? requestedVersion : "2025-06-18";
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
        instructions: "Use harpe_synthesize_context for 0/1 knapsack token packing, kibisis_resolve_memory for epistemic memory conflict resolution and <kibisis-recall> framing, argus_audit_seal / argus_audit_verify for RFC 8785 SHA-256 audit chains (integers/strings only; no floats), and telarch_open_inspector for interactive visualization."
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
            _meta: {
              ui: {
                prefersBorder: true,
                domain: "https://telarch.ai",
                csp: {
                  connectDomains: ["https://telarch.ai"],
                  resourceDomains: []
                }
              }
            }
          }
        ]
      }
    };
  }

  if (method === "resources/read") {
    const uri = String(params.uri || "");
    if (uri !== INSPECTOR_URI) {
      return { jsonrpc: "2.0", id, error: { code: -32602, message: `Unknown resource URI: ${uri}` } };
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
            _meta: {
              ui: {
                prefersBorder: true,
                domain: "https://telarch.ai",
                csp: {
                  connectDomains: ["https://telarch.ai"],
                  resourceDomains: []
                }
              }
            }
          }
        ]
      }
    };
  }

  if (method === "tools/call") {
    const name = String(params.name || "");
    const args = params.arguments || {};
    try {
      let payload;
      if (name === "harpe_synthesize_context") {
        payload = await runHarpeSynthesize(args);
      } else if (name === "harpe_budget_evaluate") {
        const total = Number(args.total_budget ?? 4096);
        const rc = Number(args.reserved_completion ?? 2048);
        const rt = Number(args.reserved_tools ?? 1024);
        const sm = Number(args.safety_margin ?? 512);
        const used = Number(args.current_usage ?? 0);
        const avail = Math.max(0, total - rc - rt - sm);
        payload = {
          total_budget: total,
          available_context: avail,
          current_usage: used,
          utilization_pct: avail > 0 ? Number(((used / avail) * 100).toFixed(2)) : 100,
          is_exceeded: used > avail
        };
      } else if (name === "kibisis_resolve_memory") {
        payload = runKibisisResolve(args);
      } else if (name === "kibisis_lease_evaluate") {
        const token = Number(args.fencing_token);
        const highest = Number(args.highest_token_seen);
        const expires = args.lease_expires_epoch !== undefined ? Number(args.lease_expires_epoch) : null;
        const now = args.now_epoch !== undefined ? Number(args.now_epoch) : null;
        if (token < highest) {
          throw new Error(`StaleFencingTokenError: holder '${args.holder_id}' presented fencing_token=${token} < highest_token_seen=${highest}. Split-brain write rejected.`);
        }
        if (expires !== null && now !== null && now >= expires) {
          throw new Error(`LeaseExpiredError: holder '${args.holder_id}' lease expired at ${expires} (now=${now}). Write rejected.`);
        }
        payload = {
          permitted: true,
          resource: String(args.resource || "vault:default"),
          holder_id: String(args.holder_id),
          accepted_fencing_token: token,
          next_monotonic_token: token + 1
        };
      } else if (name === "argus_audit_seal") {
        payload = await runArgusSeal(args);
      } else if (name === "argus_audit_verify") {
        payload = await runArgusVerify(args);
      } else if (name === "telarch_open_inspector") {
        const harpeRes = await runHarpeSynthesize({
          total_budget: Number(args.total_budget ?? 3640),
          policy: "knapsack_dp",
          items: [
            { id: "sys_invariants", content: "Enforce SQLCipher encryption and monotonic fencing tokens on every write.", priority: 100, pinned: true },
            { id: "arch_decision", content: "Use Rust 0/1 knapsack DP for deterministic context packing under budget.", priority: 90, pinned: false },
            { id: "stale_scratch", content: "Verbose historical debug trace from deprecated prototype build.", priority: 15, pinned: false }
          ]
        });
        const kibisisRes = runKibisisResolve({
          active_scope: "default",
          requested_scope: "default",
          query: String(args.query || "SQLCipher encryption")
        });
        const argusRes = await runArgusSeal({
          events: [
            { event_type: "kibisis.lease.acquire", actor: "worker-a", payload: { fencing_token: 1, ttl_s: 30 }, timestamp: "2026-11-04T00:00:01Z" },
            { event_type: "harpe.context.pack", actor: "worker-a", payload: { consumed_tokens: harpeRes.consumed_tokens, savings_bp: harpeRes.tokens_saved_bp }, timestamp: "2026-11-04T00:00:02Z" },
            { event_type: "kibisis.vault.write", actor: "worker-a", payload: { fencing_token: 1, key: "db_engine_v2" }, timestamp: "2026-11-04T00:00:03Z" }
          ]
        });
        payload = {
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
      } else {
        return {
          jsonrpc: "2.0",
          id,
          result: {
            content: [{ type: "text", text: `Unknown tool: ${name}` }],
            isError: true
          }
        };
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
    } catch (err) {
      return {
        jsonrpc: "2.0",
        id,
        result: {
          content: [{ type: "text", text: String(err && err.message ? err.message : err) }],
          isError: true
        }
      };
    }
  }

  return {
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: `Method not found: ${method}` }
  };
}

const MCP_CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, Mcp-Session-Id, MCP-Protocol-Version, OpenAI-Conversation-Id, OpenAI-Ephemeral-User-Id",
  "Access-Control-Expose-Headers": "Mcp-Session-Id, MCP-Protocol-Version",
  "Cache-Control": "no-store"
};

async function handleMcpHttpRequest(request) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: MCP_CORS_HEADERS });
  }
  if (request.method === "DELETE") {
    return new Response(null, { status: 204, headers: MCP_CORS_HEADERS });
  }
  if (request.method === "GET") {
    const accept = request.headers.get("Accept") || "";
    if (accept.includes("text/event-stream")) {
      return new Response(": telarch-mcp streamable-http ready\n\n", {
        status: 200,
        headers: {
          ...MCP_CORS_HEADERS,
          "Content-Type": "text/event-stream; charset=utf-8"
        }
      });
    }
    return new Response(
      JSON.stringify({
        name: "telarch-mcp",
        version: "0.1.0",
        transport: "streamable-http",
        protocolVersion: "2025-06-18",
        publisher: "Perseus Computing LLC",
        homepage: "https://telarch.ai",
        evidence: "https://telarch.ai/evidence",
        tools: MCP_TOOLS.map(t => t.name),
        resources: [INSPECTOR_URI]
      }, null, 2),
      {
        status: 200,
        headers: { ...MCP_CORS_HEADERS, "Content-Type": "application/json; charset=utf-8" }
      }
    );
  }
  if (request.method === "POST") {
    let body;
    try {
      body = await request.json();
    } catch (_) {
      return new Response(
        JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }),
        { status: 400, headers: { ...MCP_CORS_HEADERS, "Content-Type": "application/json; charset=utf-8" } }
      );
    }
    if (Array.isArray(body)) {
      const results = (await Promise.all(body.map(item => handleMcpRpcSingle(item)))).filter(Boolean);
      if (results.length === 0) {
        return new Response(null, { status: 202, headers: MCP_CORS_HEADERS });
      }
      return new Response(JSON.stringify(results), {
        status: 200,
        headers: { ...MCP_CORS_HEADERS, "Content-Type": "application/json; charset=utf-8" }
      });
    } else {
      const res = await handleMcpRpcSingle(body);
      if (res === null) {
        return new Response(null, { status: 202, headers: MCP_CORS_HEADERS });
      }
      return new Response(JSON.stringify(res), {
        status: 200,
        headers: { ...MCP_CORS_HEADERS, "Content-Type": "application/json; charset=utf-8" }
      });
    }
  }
  return new Response("Method Not Allowed", { status: 405, headers: MCP_CORS_HEADERS });
}
