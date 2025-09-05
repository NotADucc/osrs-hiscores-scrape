import dis
from typing import Any, Callable, cast


def get_comparison(f: Callable[[Any], bool]) -> str:
    """ Tries to retrieve the comparison symbol from a predicate function. """
    visited: set[int] = set()
    stack: list[Callable] = [f]

    while stack:
        func = stack.pop()
        if id(func) in visited:
            continue
        visited.add(id(func))

        try:
            for instr in dis.get_instructions(func):
                if instr.opname == "COMPARE_OP" and instr.argval in {"==", "!=", "<", "<=", ">", ">="}:
                    return instr.argval
        except TypeError:
            pass

        closure = getattr(func, "__closure__", None)
        if closure:
            for cell in closure:
                try:
                    cell_val = cell.cell_contents
                except ValueError:
                    continue

                if callable(cell_val):
                    stack.append(cast(Callable[[Any], bool], cell_val))
                else:
                    for name in dir(cell_val):
                        try:
                            attr = getattr(cell_val, name)
                        except Exception:
                            continue
                        if callable(attr):
                            stack.append(cast(Callable[[Any], bool], attr))


        co = getattr(func, "__code__", None)
        names = set(co.co_names) if co else set()
        globs = getattr(func, "__globals__", {}) or {}
        for name in names:
            g = globs.get(name)
            if callable(g):
                stack.append(cast(Callable[[Any], bool], g))

    raise ValueError("Could not extract a comparison operator")
