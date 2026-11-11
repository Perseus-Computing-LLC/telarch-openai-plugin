"""severity: low
finding: the recall skill documents a kibisis_recall call that the hosted server does not expose and the local server refuses
location: plugins/telarch/skills/telarch-recall/SKILL.md:12 and plugins/telarch/skills/telarch-recall/references/cli.md:7,10-16 (hosted plugin; files byte-identical to the telarch-local copies)
effect: the hosted plugin's only server is edge/telarch_edge_mcp.js, whose tools/list has seven tools and
  no kibisis_recall (the nearest is kibisis_resolve_memory), so rule 1 of the hosted skill tells the
  model to call a tool that does not exist there. On the local server the documented call
  `kibisis_recall(query=..., category=..., epistemic_state="verified", limit=10, match="any")` is
  refused: the tool has no epistemic_state parameter (it has include_candidates) and the upstream
  handler answers "Refused: 'epistemic_state' cannot be set through MCP".
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EDGE_JS = ROOT / "edge" / "telarch_edge_mcp.js"
LOCAL_PY = ROOT / "plugins" / "telarch-local" / "server" / "telarch_mcp_server.py"
_ENV_PREFIXES = ("KIBISIS_", "ARGUS_", "TELARCH_", "PLUGIN_", "HARPE_")


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """Clean environment: no Telarch variables, HOME/XDG/cwd/PLUGIN_DATA inside pytest's tmp_path."""
    for key in list(os.environ):
        if key.startswith(_ENV_PREFIXES):
            monkeypatch.delenv(key)
    data = tmp_path / "plugin_data"
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "home" / "xdg"))
    monkeypatch.setenv("PLUGIN_DATA", str(data))
    (tmp_path / "home").mkdir()
    (tmp_path / "cwd").mkdir()
    monkeypatch.chdir(tmp_path / "cwd")
    return tmp_path


def _load_local_module():
    spec = importlib.util.spec_from_file_location("telarch_mcp_server", LOCAL_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _local_call(server, name: str, args) -> dict:
    return server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})


def _run_stdio(mod, lines) -> list:
    """Drive the real main() loop with the given stdin lines; return the stdout lines it wrote."""
    out, err = io.StringIO(), io.StringIO()
    saved = sys.stdin, sys.stdout, sys.stderr
    sys.stdin, sys.stdout, sys.stderr = io.StringIO("".join(line + "\n" for line in lines)), out, err
    try:
        rc = mod.main()
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved
    assert rc == 0
    return [ln for ln in out.getvalue().split("\n") if ln != ""]


def _edge_rpc(req: dict) -> dict:
    harness = (
        "const fs = require('fs');\n"
        f"const code = fs.readFileSync({json.dumps(str(EDGE_JS))}, 'utf8');\n"
        "const fn = new Function(code + '\\nreturn handleMcpRpcSingle;')();\n"
        f"(async () => {{ process.stdout.write(JSON.stringify(await fn({json.dumps(req)}))); }})();\n"
    )
    proc = subprocess.run(["node", "-e", harness], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def _edge_call(name: str, args) -> dict:
    return _edge_rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})


def _rejected(resp: dict) -> bool:
    return "error" in resp or bool(resp.get("result", {}).get("isError"))


import ast
import re

HOSTED_SKILLS = ROOT / "plugins" / "telarch" / "skills"
LOCAL_SKILLS = ROOT / "plugins" / "telarch-local" / "skills"
TOOL_RE = re.compile(r"`((?:kibisis|harpe|argus|telarch)_[a-z_]+)`|\b((?:kibisis|harpe|argus)_[a-z_]+)\(")
NOT_TOOLS = {"telarch_balance", "argus_receipt_seq"}  # field names in the card examples


def _mentioned_tools(skill_dir: Path) -> dict:
    found = {}
    for path in sorted(skill_dir.rglob("*.md")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for a, b in TOOL_RE.findall(line):
                name = a or b
                if name not in NOT_TOOLS:
                    found.setdefault(name, f"{path.relative_to(ROOT)}:{lineno}")
    return found


def _documented_recall_call() -> dict:
    text = (LOCAL_SKILLS / "telarch-recall" / "references" / "cli.md").read_text(encoding="utf-8")
    block = re.search(r"```python\n(kibisis_recall\(.*?\))\n```", text, re.S).group(1)
    call = ast.parse(block).body[0].value
    return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}


def test_control_local_skill_docs_name_only_tools_the_local_server_lists(sandbox):
    server = _load_local_module().TelarchMCPServer()
    listed = {t["name"] for t in server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}
    mentioned = _mentioned_tools(LOCAL_SKILLS)
    assert "kibisis_recall" in mentioned and len(listed) == 10
    assert set(mentioned) <= listed


def test_hosted_skill_docs_name_only_tools_the_hosted_server_lists():
    listed = {t["name"] for t in _edge_rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}
    missing = {name: where for name, where in _mentioned_tools(HOSTED_SKILLS).items() if name not in listed}
    assert missing == {}, f"hosted skills name tools the hosted server does not have: {missing}"


def test_documented_recall_call_is_accepted_by_the_local_server(sandbox):
    args = _documented_recall_call()
    assert args["query"] and "limit" in args  # parsed from the document, not typed here
    server = _load_local_module().TelarchMCPServer()
    resp = _local_call(server, "kibisis_recall", args)
    assert not _rejected(resp), f"documented call refused: {resp['result']['content'][0]['text'][:160]}"
