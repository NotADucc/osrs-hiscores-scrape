import builtins
import sys
import pytest
import psutil
import types

from src.util.guard_clause_handler import script_running_in_cmd_guard


@pytest.fixture(autouse=True)
def patch_exit(monkeypatch):
    """ Prevent real sys.exit in tests """
    called = {}

    def fake_exit(code=1):
        called["code"] = code
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", fake_exit)
    return called


@pytest.fixture(autouse=True)
def patch_input(monkeypatch):
    """ Prevent blocking input() during tests """
    monkeypatch.setattr(builtins, "input", lambda *a, **kw: "")


@pytest.fixture
def mock_process(monkeypatch):
    def _make_process(name):
        parent = types.SimpleNamespace()
        parent.name = lambda: name
        proc = types.SimpleNamespace()
        proc.parent = lambda: parent
        monkeypatch.setattr(psutil, "Process", lambda pid: proc)
    return _make_process


def test_exits_if_stdin_not_tty(monkeypatch, patch_exit):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    with pytest.raises(SystemExit):
        script_running_in_cmd_guard()

    assert patch_exit["code"] == 1


def test_exits_if_stdout_not_tty(monkeypatch, patch_exit):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    with pytest.raises(SystemExit):
        script_running_in_cmd_guard()

    assert patch_exit["code"] == 1


@pytest.mark.parametrize(
    "file_manager",
    [
        "dolphin", "explorer", "explorer.exe", "finder", "nautilus"
    ]
)
def test_exits_if_parent_is_file_manager(file_manager, monkeypatch, mock_process, patch_exit):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    mock_process(file_manager)

    with pytest.raises(SystemExit):
        script_running_in_cmd_guard()

    assert patch_exit["code"] == 1


@pytest.mark.parametrize(
    "terminal",
    [
        "alacritty", 
        "bash", 
        "bash.exe", 
        "cmd.exe", 
        "conhost.exe", 
        "dash", 
        "fish", 
        "gnome-terminal", 
        "Hyper", 
        "iTerm2", 
        "kitty", 
        "konsole", 
        "lxterminal", 
        "mate-terminal", 
        "powershell.exe", 
        "pwsh.exe", 
        "rxvt", 
        "screen", 
        "sh", 
        "Terminal", 
        "terminator", 
        "tilix", 
        "tmux", 
        "Warp", 
        "wt.exe", 
        "xterm", 
        "zsh"
    ]
)
def test_passes_in_real_terminal(terminal, monkeypatch, mock_process):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    mock_process(terminal)

    script_running_in_cmd_guard()
