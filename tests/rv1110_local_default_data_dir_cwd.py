"""severity: low
finding: without PLUGIN_DATA the local server creates its vault and ledger in ./.telarch of whatever directory it is started from; running the repository's own test does this in the checkout
location: plugins/telarch-local/server/telarch_mcp_server.py:165-166 (`Path(PLUGIN_DATA or TELARCH_DATA_DIR or ".telarch")`, created at construction); tests/test_mcp_contract.py loads the module and builds the server with no data directory set
effect: plugins/telarch-local/mcp.json sets cwd to ${PLUGIN_ROOT}, so on a host that does not export
  PLUGIN_DATA the unencrypted vault is written inside the plugin's install directory. In this
  repository the existing contract test leaves .telarch/kibisis_vault.sqlite and
  .telarch/argus_ledger.jsonl in the working tree; there is no .gitignore, so `git add -A` would stage
  a vault. (The baseline run of tests/test_mcp_contract.py for this review created exactly that
  directory in the clone.) TELARCH_DATA_DIR, the second fallback, is not documented anywhere.
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


def test_control_plugin_data_is_used_when_set(sandbox):
    _load_local_module().TelarchMCPServer()
    assert (sandbox / "plugin_data" / "kibisis_vault.sqlite").is_file()
    assert not (sandbox / "cwd" / ".telarch").exists()


def test_server_does_not_create_a_vault_in_the_working_directory(sandbox, monkeypatch):
    monkeypatch.delenv("PLUGIN_DATA")
    _load_local_module().TelarchMCPServer()
    created = sorted(p.name for p in (sandbox / "cwd").rglob("*") if p.is_file())
    assert created == [], f"files created under the current directory: {created}"


def test_repository_ignores_the_directory_its_own_test_creates():
    ignore = ROOT / ".gitignore"
    patterns = ignore.read_text(encoding="utf-8").split() if ignore.is_file() else []
    assert any(p.strip("/") == ".telarch" for p in patterns), ".telarch/ (vault + ledger written by tests/test_mcp_contract.py) is not git-ignored"
