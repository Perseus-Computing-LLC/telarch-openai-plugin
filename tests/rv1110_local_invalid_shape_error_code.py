"""severity: low
finding: valid JSON of the wrong shape is reported as -32700 Parse error with id null and a Python exception text
location: plugins/telarch-local/server/telarch_mcp_server.py:179-181 and :197 (`.get` on whatever was parsed), :323-325 (every exception becomes -32700, id None)
effect: JSON-RPC 2.0 section 5.1: -32700 means "Invalid JSON was received"; -32600 is "The JSON sent is
  not a valid Request object"; -32602 is "Invalid method parameter(s)". A request whose `params` is an
  array or a string raises AttributeError inside handle_request; main() answers
  {"id": null, "error": {"code": -32700, "message": "'list' object has no attribute 'get'"}}, so the
  caller cannot match the error to its request id (section 5: id MUST be the same as the request's
  unless the id could not be detected). A top-level array or scalar is answered the same way. The loop
  survives and nothing but JSON reaches stdout, which is correct.
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


def _answers(raw_lines):
    return [json.loads(x) for x in _run_stdio(_load_local_module(), raw_lines)]


def test_control_malformed_json_is_parse_error_and_the_loop_keeps_serving(sandbox):
    out = _answers(["{not json", json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"})])
    assert out[0]["error"]["code"] == -32700 and out[0]["id"] is None
    assert out[1] == {"jsonrpc": "2.0", "id": 2, "result": {}}


def test_array_params_keeps_the_request_id_and_is_invalid_params(sandbox):
    out = _answers([json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": ["harpe_budget_evaluate"]})])
    assert out[0]["id"] == 7, f"request id lost: {out[0]}"
    assert out[0]["error"]["code"] == -32602


def test_top_level_scalar_is_invalid_request_not_parse_error(sandbox):
    out = _answers(['"ping"'])
    assert out[0]["error"]["code"] == -32600, f"got {out[0]['error']}"


def test_error_message_does_not_carry_python_internals(sandbox):
    out = _answers([json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": "x"})])
    assert "object has no attribute" not in out[0]["error"]["message"]
