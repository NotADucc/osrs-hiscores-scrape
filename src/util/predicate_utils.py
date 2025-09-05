import dis
from typing import Any, Callable, cast


def get_comparison(f: Callable[[Any], bool]) -> str:
    """ Tries to retrieve the comparison symbol from a predicate """
    visited = set()
    stack = [f]

    while stack:
        func = stack.pop()
        if id(func) in visited:
            continue
        visited.add(id(func))

        for instr in dis.get_instructions(func):
            if instr.opname == "COMPARE_OP" and instr.argval in {"==", "!=", "<", "<=", ">", ">="}:
                return instr.argval

        co = getattr(func, "__code__", None)
        names = set(co.co_names) if co else set()

        if func.__closure__:
            for cell in func.__closure__:
                try:
                    cell_val = cell.cell_contents
                except ValueError:
                    continue
                if callable(cell.cell_contents):
                    stack.append(
                        cast(Callable[[Any], bool], cell.cell_contents))
                else:
                    for name in names | {"p", "pred", "predicate"}:
                        attr = getattr(cell_val, name, None)
                        if callable(attr):
                            stack.append(cast(Callable[[Any], bool], attr))

        globs = getattr(func, "__globals__", {}) or {}
        for name in names:
            g = globs.get(name)
            if callable(g):
                stack.append(cast(Callable[[Any], bool], g))

    raise ValueError("Input given is not a simple comparison predicate")