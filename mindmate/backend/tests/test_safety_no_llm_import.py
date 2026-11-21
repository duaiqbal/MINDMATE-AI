"""Architectural invariant: app.safety must NEVER import from app.llm.

The safety layer is independent of the LLM. This test parses every module
under app/safety with the AST and fails if any import targets app.llm
(directly, via from-import, or a relative import resolving to llm).

It must pass on the current (empty) safety package and will fail the moment a
forbidden import is introduced.
"""

import ast
from pathlib import Path

SAFETY_DIR = Path(__file__).resolve().parents[1] / "app" / "safety"


def _safety_files() -> list[Path]:
    return sorted(SAFETY_DIR.rglob("*.py"))


def _forbidden_import(node: ast.AST, module_file: Path) -> str | None:
    """Return a description if the node imports from app.llm, else None."""
    if isinstance(node, ast.Import):
        for alias in node.names:
            name = alias.name
            if name == "app.llm" or name.startswith("app.llm."):
                return f"import {name}"
    elif isinstance(node, ast.ImportFrom):
        # Absolute: from app.llm[.x] import ...
        if node.level == 0 and node.module:
            if node.module == "app.llm" or node.module.startswith("app.llm."):
                return f"from {node.module} import ..."
        # Relative: resolve against the file's package path.
        if node.level > 0:
            # app/safety/<...>  ->  package parts after 'app'
            rel = module_file.relative_to(SAFETY_DIR.parents[1])  # from app/
            pkg_parts = ["app", *rel.parts[:-1]]  # drop filename
            base = pkg_parts[: len(pkg_parts) - (node.level - 1)]
            target = ".".join([*base, node.module]) if node.module else ".".join(base)
            if target == "app.llm" or target.startswith("app.llm."):
                return f"relative import -> {target}"
    return None


def test_safety_does_not_import_llm() -> None:
    violations: list[str] = []
    for f in _safety_files():
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            desc = _forbidden_import(node, f)
            if desc:
                violations.append(f"{f}: {desc}")
    assert not violations, (
        "app.safety must not import from app.llm:\n  " + "\n  ".join(violations)
    )


def test_safety_package_exists() -> None:
    assert SAFETY_DIR.is_dir(), f"missing safety package at {SAFETY_DIR}"