"""How the local server keys its vault file (review 2026-11-10, L03; paths L04, L05).

Default: a key file ``vault.key`` beside the vault, created once with mode 0600, so the vault file is encrypted
without any setup. A passphrase from the environment is used instead when given, and then no key file is
written. A plain vault with entries from an earlier plugin version is kept, served unchanged and reported as
plain. The server never switches plaintext on itself.
"""
from __future__ import annotations

import json
import os
import sqlite3
import stat
import sys

import pytest

from telarch_testlib import isolate_environment, load_local_module, local_call

SQLITE_HEADER = b"SQLite format 3\x00"


def _health(server) -> dict:
    answer = local_call(server, "kibisis_health", {})
    assert answer["result"].get("isError") is not True, answer
    return json.loads(answer["result"]["content"][0]["text"])


def _remember(server, key: str, content: str) -> dict:
    return local_call(server, "kibisis_remember", {"category": "decision", "key": key, "content": content})


def _recall_text(server, query: str) -> str:
    answer = local_call(server, "kibisis_recall", {"query": query})
    assert answer["result"].get("isError") is not True, answer
    return answer["result"]["content"][0]["text"]


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    return isolate_environment(tmp_path, monkeypatch)


def test_first_start_creates_a_private_key_file_and_an_encrypted_vault(sandbox):
    server = load_local_module().TelarchMCPServer()
    data = sandbox / "plugin_data"
    key_file, vault_file = data / "vault.key", data / "kibisis_vault.sqlite"
    assert key_file.is_file() and vault_file.is_file()
    key_text = key_file.read_text().strip()
    assert len(key_text) == 64 and int(key_text, 16) >= 0, "32 random bytes as hex"
    if os.name == "posix":
        assert stat.S_IMODE(key_file.stat().st_mode) == 0o600
    assert _remember(server, "marker", "zebra-quartz-0451")["result"].get("isError") is not True
    assert "zebra-quartz-0451" in _recall_text(server, "zebra-quartz-0451")
    raw = b"".join(p.read_bytes() for p in data.iterdir() if p.name.startswith("kibisis_vault.sqlite"))
    assert not vault_file.read_bytes().startswith(SQLITE_HEADER), "the vault file is a plain SQLite database"
    assert b"zebra-quartz-0451" not in raw, "stored text is readable in the vault file"
    assert "KIBISIS_ALLOW_PLAINTEXT" not in os.environ
    storage = _health(server)["vault_storage"]
    assert storage["mode"] == "encrypted" and storage["key_file"] == str(key_file)


def test_second_start_reuses_the_key_file_and_reads_the_same_vault(sandbox, monkeypatch):
    module = load_local_module()
    first = module.TelarchMCPServer()
    _remember(first, "marker", "heron-basalt-7719")
    key_before = (sandbox / "plugin_data" / "vault.key").read_text()
    del first
    monkeypatch.setenv("KIBISIS_PASSPHRASE_FILE", "")  # a new process starts without the variable
    second = load_local_module().TelarchMCPServer()
    assert (sandbox / "plugin_data" / "vault.key").read_text() == key_before
    assert "heron-basalt-7719" in _recall_text(second, "heron-basalt-7719")


def test_a_passphrase_from_the_environment_keeps_the_key_out_of_the_folder(sandbox, monkeypatch):
    monkeypatch.setenv("KIBISIS_PASSPHRASE", "correct horse battery staple for a test")
    server = load_local_module().TelarchMCPServer()
    data = sandbox / "plugin_data"
    assert not (data / "vault.key").exists()
    assert not (data / "kibisis_vault.sqlite").read_bytes().startswith(SQLITE_HEADER)
    storage = _health(server)["vault_storage"]
    assert storage["mode"] == "encrypted" and storage["key_source"] == "environment"


def test_an_existing_plain_vault_with_entries_is_kept_served_and_reported_as_plain(sandbox, monkeypatch):
    # an earlier plugin version: the server switched plaintext on and wrote a plain SQLite vault
    monkeypatch.setenv("KIBISIS_ALLOW_PLAINTEXT", "1")
    old = load_local_module().TelarchMCPServer()
    _remember(old, "legacy", "osprey-granite-3302")
    del old
    monkeypatch.delenv("KIBISIS_ALLOW_PLAINTEXT")
    vault_file = sandbox / "plugin_data" / "kibisis_vault.sqlite"
    assert vault_file.read_bytes().startswith(SQLITE_HEADER)
    rows_before = sqlite3.connect(f"file:{vault_file}?mode=ro", uri=True).execute("select count(*) from sqlite_master").fetchone()[0]

    server = load_local_module().TelarchMCPServer()
    assert "osprey-granite-3302" in _recall_text(server, "osprey-granite-3302"), "the old entries are gone"
    assert vault_file.read_bytes().startswith(SQLITE_HEADER), "the old vault was converted or replaced"
    assert sqlite3.connect(f"file:{vault_file}?mode=ro", uri=True).execute("select count(*) from sqlite_master").fetchone()[0] == rows_before
    storage = _health(server)["vault_storage"]
    assert storage["mode"] == "plain" and "earlier plugin version" in storage["reason"]
    assert not (sandbox / "plugin_data" / "vault.key").exists(), "a key file that opens nothing was left behind"
    assert "KIBISIS_ALLOW_PLAINTEXT" not in os.environ and not os.environ.get("KIBISIS_PASSPHRASE_FILE")
    # and it stays writable
    assert _remember(server, "after", "magpie-flint-8840")["result"].get("isError") is not True
    assert "magpie-flint-8840" in _recall_text(server, "magpie-flint-8840")


def test_plaintext_is_only_used_when_the_operator_asks_for_it(sandbox, monkeypatch):
    monkeypatch.setenv("KIBISIS_ALLOW_PLAINTEXT", "1")
    server = load_local_module().TelarchMCPServer()
    assert not (sandbox / "plugin_data" / "vault.key").exists()
    storage = _health(server)["vault_storage"]
    assert storage["mode"] == "plain" and "KIBISIS_ALLOW_PLAINTEXT" in storage["reason"]


def test_the_key_file_sits_beside_a_vault_named_by_either_variable(sandbox, monkeypatch):
    elsewhere = sandbox / "elsewhere"
    monkeypatch.setenv("KIBISIS_VAULT_PATH", str(elsewhere / "v.sqlite"))
    load_local_module().TelarchMCPServer()
    assert (elsewhere / "v.sqlite").is_file() and (elsewhere / "vault.key").is_file()
    assert not (sandbox / "plugin_data" / "kibisis_vault.sqlite").exists()
    # KIBISIS_DB_PATH wins when both are set
    monkeypatch.setenv("KIBISIS_PASSPHRASE_FILE", "")
    monkeypatch.setenv("KIBISIS_DB_PATH", str(sandbox / "winner" / "w.sqlite"))
    load_local_module().TelarchMCPServer()
    assert (sandbox / "winner" / "w.sqlite").is_file() and (sandbox / "winner" / "vault.key").is_file()


@pytest.mark.parametrize(
    "platform, env, expected",
    [
        ("linux", {"HOME": "/home/u", "XDG_DATA_HOME": "/x/data"}, "/x/data/telarch"),
        ("linux", {"HOME": "/home/u"}, "/home/u/.local/share/telarch"),
        ("linux", {"HOME": "/home/u", "XDG_DATA_HOME": "relative/dir"}, "/home/u/.local/share/telarch"),
        ("darwin", {"HOME": "/Users/u", "XDG_DATA_HOME": "/x/data"}, "/Users/u/Library/Application Support/telarch"),
    ],
)
def test_default_data_directory_is_per_user(platform, env, expected):
    assert str(_module().default_data_dir(env, platform)) == expected


@pytest.mark.skipif(sys.platform.startswith("win"), reason="builds a Windows path with the POSIX path module")
def test_default_data_directory_on_windows_uses_localappdata():
    got = _module().default_data_dir({"LOCALAPPDATA": "/c/Users/u/AppData/Local", "HOME": "/c/Users/u"}, "win32")
    assert str(got) == "/c/Users/u/AppData/Local/telarch"


def test_without_plugin_data_nothing_is_written_to_the_start_directory(sandbox, monkeypatch):
    monkeypatch.delenv("PLUGIN_DATA")
    load_local_module().TelarchMCPServer()
    assert list((sandbox / "cwd").iterdir()) == []
    if sys.platform.startswith("linux"):
        assert (sandbox / "home" / "xdg" / "telarch" / "kibisis_vault.sqlite").is_file()
        assert (sandbox / "home" / "xdg" / "telarch" / "argus_ledger.jsonl").parent.is_dir()


_MODULE = None


def _module():
    """The server module, imported once without starting a server (importing reads no environment)."""
    global _MODULE
    if _MODULE is None:
        _MODULE = load_local_module()
    return _MODULE
