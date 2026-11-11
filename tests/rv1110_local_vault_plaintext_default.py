"""severity: medium
finding: with no configuration the local plugin stores memory in an unencrypted SQLite file, while the README and manifest describe an encrypted vault
location: plugins/telarch-local/server/telarch_mcp_server.py:169-170 (sets KIBISIS_ALLOW_PLAINTEXT=1 whenever KIBISIS_PASSPHRASE is unset)
effect: README.md:7 ("keeps agent memory in an encrypted SQLite file"), README.md:33 ("Runs 100% offline
  against a local SQLCipher AES-256 vault"), plugins/telarch-local/plugin.json:5 and :34 ("Encrypted
  local memory"). plugins/telarch-local/mcp.json passes no environment, so the installed plugin always
  takes this branch: the vault file starts with the plain "SQLite format 3" header, stored text is
  readable in the file, and kibisis_health reports entry_key:false / whole_file:false. Upstream
  refuses to open a vault without a passphrase unless KIBISIS_ALLOW_PLAINTEXT is set; the plugin sets
  it on the user's behalf without saying so. references/config.md:9 calls that switch "only for local
  unencrypted development/testing".
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


SECRET_TEXT = "rv1110 canary sentence stored through kibisis_remember"


def _server_with_one_memory(sandbox):
    mod = _load_local_module()
    server = mod.TelarchMCPServer()
    resp = _local_call(server, "kibisis_remember", {"category": "convention", "key": "canary", "content": SECRET_TEXT})
    assert not _rejected(resp), resp
    return server, sandbox / "plugin_data" / "kibisis_vault.sqlite"


def _vault_bytes(vault: Path) -> bytes:
    return b"".join(p.read_bytes() for p in sorted(vault.parent.glob(vault.name + "*")))


def test_control_memory_is_stored_in_plugin_data_and_can_be_recalled(sandbox):
    server, vault = _server_with_one_memory(sandbox)
    assert vault.is_file()
    recall = _local_call(server, "kibisis_recall", {"query": "canary", "include_candidates": True})
    assert SECRET_TEXT in recall["result"]["content"][0]["text"]


def test_default_vault_file_is_not_plain_sqlite(sandbox):
    _, vault = _server_with_one_memory(sandbox)
    assert vault.read_bytes()[:16] != b"SQLite format 3\x00", "vault file is an unencrypted SQLite database"


def test_stored_text_is_not_readable_in_the_vault_file(sandbox):
    _, vault = _server_with_one_memory(sandbox)
    assert SECRET_TEXT.encode() not in _vault_bytes(vault), "stored memory text is readable in the vault file"


def test_health_reports_some_encryption_by_default(sandbox):
    server, _ = _server_with_one_memory(sandbox)
    enc = json.loads(_local_call(server, "kibisis_health", {})["result"]["content"][0]["text"])["encryption"]
    assert enc["entry_key"] or enc["whole_file"], f"kibisis_health: {enc}"
