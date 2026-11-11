"""The README and the skill documents of each plugin describe the server that plugin talks to
(review 2026-11-10, C03 and the "claims the code does not implement" table).

Every example call in a skill is parsed from the document and sent to the server; every tool name, link, limit
and terminal command the documents give is checked against the code or the installed libraries.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from telarch_testlib import ROOT, edge_call, isolate_environment, load_local_module, local_call, node, rejected

HOSTED_SKILLS = ROOT / "plugins" / "telarch" / "skills"
LOCAL_SKILLS = ROOT / "plugins" / "telarch-local" / "skills"
README = ROOT / "README.md"
TOOL_RE = re.compile(r"`((?:kibisis|harpe|argus|telarch)_[a-z_]+)`")
PINNED = "kibisis==0.1.0a17 harpe==0.1.0a13 argus-ledger==0.1.0a9"


def _example_calls(skill_dir: Path) -> list:
    """(file, tool, arguments) for every call written in a ```python block of the skill documents."""
    calls = []
    for path in sorted(skill_dir.rglob("*.md")):
        for block in re.findall(r"```python\n(.*?)```", path.read_text(encoding="utf-8"), re.S):
            for statement in ast.parse(block).body:
                call = statement.value
                assert isinstance(call, ast.Call) and isinstance(call.func, ast.Name), f"{path}: not a tool call"
                calls.append((path.name, call.func.id, {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}))
    return calls


def _hosted_tools() -> set:
    return set(node("done(edge.tools.map(t => t.name));"))


@pytest.fixture
def local(tmp_path, monkeypatch):
    isolate_environment(tmp_path, monkeypatch)
    return load_local_module().TelarchMCPServer()


def _local_tools(server) -> set:
    return {t["name"] for t in server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]}


def test_every_example_call_in_the_hosted_skills_is_accepted_by_the_hosted_server():
    calls = _example_calls(HOSTED_SKILLS)
    assert {tool for _, tool, _ in calls} >= {"kibisis_resolve_memory", "kibisis_lease_evaluate", "harpe_synthesize_context", "harpe_budget_evaluate"}
    for where, tool, args in calls:
        assert not rejected(edge_call(tool, args)), f"{where}: documented call to {tool} is refused"


def test_every_example_call_in_the_local_skills_is_accepted_by_the_local_server(local):
    calls = _example_calls(LOCAL_SKILLS)
    assert {tool for _, tool, _ in calls} >= {"kibisis_recall", "kibisis_remember", "kibisis_forget", "harpe_synthesize_context", "harpe_budget_evaluate"}
    for where, tool, args in calls:
        assert not rejected(local_call(local, tool, args)), f"{where}: documented call to {tool} is refused"


def test_each_skill_set_names_only_tools_of_its_own_server(local):
    for skill_dir, listed in ((HOSTED_SKILLS, _hosted_tools()), (LOCAL_SKILLS, _local_tools(local))):
        named = {name for path in skill_dir.rglob("*.md") for name in TOOL_RE.findall(path.read_text(encoding="utf-8"))}
        assert named and named <= listed, f"{skill_dir.parent.name}: {sorted(named - listed)}"


def test_readme_lists_exactly_the_tools_of_the_two_servers(local):
    named = set(TOOL_RE.findall(README.read_text(encoding="utf-8")))
    assert named == _hosted_tools() | _local_tools(local)


def test_links_between_documents_resolve():
    documents = [README, *HOSTED_SKILLS.rglob("*.md"), *LOCAL_SKILLS.rglob("*.md")]
    checked = 0
    for path in documents:
        for target in re.findall(r"\]\(([^)#]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target:
                continue
            assert (path.parent / target).exists(), f"{path.relative_to(ROOT)} links to missing {target}"
            checked += 1
    assert checked >= 10


def test_hosted_reference_states_the_limits_the_worker_enforces():
    text = (HOSTED_SKILLS / "telarch-setup" / "references" / "config.md").read_text(encoding="utf-8")
    limits = node("done(edge.limits);")
    assert len(limits) == 6
    for name, value in limits.items():
        assert f"| {value:,} " in text or f"| {value:,} bytes" in text, f"{name}={value} is not in the limits table"


def test_documents_do_not_describe_another_installation():
    stale = ("ops/tci", "Hermes", "Greg", "kibisis query", "harpe budget", "harpe synthesize", ".telarch/vault.sqlite", "zero overruns", "monotonic fencing leases")
    for path in [*HOSTED_SKILLS.rglob("*.md"), *LOCAL_SKILLS.rglob("*.md"), ROOT / "plugins" / "telarch" / "plugin.json", ROOT / "plugins" / "telarch-local" / "plugin.json"]:
        text = path.read_text(encoding="utf-8")
        for phrase in stale:
            assert phrase not in text, f"{path.relative_to(ROOT)}: {phrase!r}"
    hosted = "\n".join(p.read_text(encoding="utf-8") for p in HOSTED_SKILLS.rglob("*.md"))
    assert "KIBISIS_" not in hosted and "PLUGIN_DATA" not in hosted, "hosted skills describe local environment variables"


def test_local_reference_names_the_files_and_variables_the_server_uses(local, tmp_path):
    text = (LOCAL_SKILLS / "telarch-setup" / "references" / "config.md").read_text(encoding="utf-8")
    data = tmp_path / "plugin_data"
    for name in ("kibisis_vault.sqlite", "vault.key"):
        assert (data / name).is_file() and f"`{name}`" in text
    assert "`argus_ledger.jsonl`" in text
    source = (ROOT / "plugins" / "telarch-local" / "server" / "telarch_mcp_server.py").read_text(encoding="utf-8")
    for variable in re.findall(r"`((?:KIBISIS|ARGUS|TELARCH|PLUGIN)_[A-Z_]+)`", text):
        assert variable in source or variable == "KIBISIS_SCOPE", f"{variable} is documented but the server never reads it"


def test_the_review_commands_in_the_local_skill_run_against_the_plugin_vault(local, tmp_path):
    text = (LOCAL_SKILLS / "telarch-recall" / "references" / "cli.md").read_text(encoding="utf-8")
    commands = re.findall(r"^python3 (-m kibisis\.review list.*)$", text, re.M)
    assert len(commands) == 2 and 'KIBISIS_DB_PATH="$PLUGIN_DATA/kibisis_vault.sqlite"' in text and 'KIBISIS_PASSPHRASE_FILE="$PLUGIN_DATA/vault.key"' in text
    assert not rejected(local_call(local, "kibisis_remember", {"category": "convention", "key": "python_runtime", "content": "We use Python 3.12 with uv."}))
    import kibisis

    data = tmp_path / "plugin_data"
    env = {k: v for k, v in os.environ.items() if not k.startswith(("KIBISIS_", "PLUGIN_"))}
    env.update(KIBISIS_DB_PATH=str(data / "kibisis_vault.sqlite"), KIBISIS_PASSPHRASE_FILE=str(data / "vault.key"),
               PYTHONPATH=os.pathsep.join(p for p in sys.path if p), PYTHONDONTWRITEBYTECODE="1")
    for command in commands:
        done = subprocess.run([sys.executable, *command.split()], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)
        assert done.returncode == 0, done.stderr[-300:]
        assert "convention:python_runtime" in done.stdout
    assert kibisis.__name__ == "kibisis"


def test_readme_install_line_and_ci_use_the_same_pinned_libraries():
    assert f"pip install {PINNED}" in README.read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert f"pip install pytest {PINNED}" in workflow and "python -m pytest -q tests" in workflow
