"""severity: medium
finding: the documented KIBISIS_VAULT_PATH variable moves the vault out of the plugin data folder to the per-user default path, and the file is not created where the variable points
location: plugins/telarch-local/server/telarch_mcp_server.py:167-168 (KIBISIS_DB_PATH is only set when neither variable is present)
effect: plugins/telarch-local/skills/telarch-setup/references/config.md:7 documents `KIBISIS_VAULT_PATH`
  as the vault path. The installed kibisis package reads only KIBISIS_DB_PATH (kibisis/config.py:24,
  :76; no source file under kibisis, harpe or argus mentions KIBISIS_VAULT_PATH). The server sees the
  variable, skips its own PLUGIN_DATA default, and kibisis falls back to its per-user data directory
  ($XDG_DATA_HOME or ~/.local/share). The vault is then neither at the documented path nor in
  PLUGIN_DATA. The same line of config.md gives the default file name as vault.sqlite; the code
  uses kibisis_vault.sqlite.
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


def _files_under(root: Path) -> list:
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


def test_control_without_the_variable_the_vault_is_created_in_plugin_data(sandbox):
    _load_local_module().TelarchMCPServer()
    assert (sandbox / "plugin_data" / "kibisis_vault.sqlite").is_file()
    assert _files_under(sandbox / "home") == []


def test_vault_is_created_where_kibisis_vault_path_points(sandbox, monkeypatch):
    target = sandbox / "custom" / "my_vault.sqlite"
    target.parent.mkdir()
    monkeypatch.setenv("KIBISIS_VAULT_PATH", str(target))
    _load_local_module().TelarchMCPServer()
    assert target.is_file(), f"no vault at KIBISIS_VAULT_PATH; files written under HOME: {_files_under(sandbox / 'home')}"


def test_setting_the_variable_does_not_write_outside_the_chosen_and_plugin_dirs(sandbox, monkeypatch):
    monkeypatch.setenv("KIBISIS_VAULT_PATH", str(sandbox / "custom.sqlite"))
    _load_local_module().TelarchMCPServer()
    assert _files_under(sandbox / "home") == [], "vault created in the per-user data directory"
