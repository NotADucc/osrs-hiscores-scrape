import argparse
import builtins
import sys
import types

import psutil
import pytest

from src.util.script_utils import argparse_wrapper, script_running_in_cmd_guard


def test_argparse_wrapper():
    def sample(x: str):
        return x

    VAL = "test"

    wrapped = argparse_wrapper(sample)
    value = wrapped(VAL)
    assert value == VAL


def test_argparse_wrapper_key_error(caplog):
    def sample(x: str):
        raise KeyError("key does not match")

    VAL = "test"

    wrapped = argparse_wrapper(sample)
    with pytest.raises(argparse.ArgumentTypeError, match="key does not match"):
        _ = wrapped(VAL)


def test_argparse_wrapper_error(caplog):
    def sample(x: str):
        raise Exception("random error")

    VAL = "test"

    wrapped = argparse_wrapper(sample)
    with pytest.raises(Exception, match="random error"):
        _ = wrapped(VAL)


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
