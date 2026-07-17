from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import sys

CANONICAL_ROOT = Path("trading_os")
LEGACY_ROOTS = {
    "agents",
    "api",
    "backend",
    "core",
    "dashboard",
    "enterprise",
    "mobile",
    "modules",
    "nexus",
    "paper",
    "realworld",
}


@dataclass(frozen=True)
class ImportViolation:
    file: Path
    line: int
    imported_module: str


def imported_modules(tree: ast.AST) -> list[tuple[int, str]]:
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.lineno, node.module))
    return imports


def find_violations() -> list[ImportViolation]:
    violations: list[ImportViolation] = []
    for path in CANONICAL_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for line, module_name in imported_modules(tree):
            root = module_name.split(".", 1)[0]
            if root in LEGACY_ROOTS:
                violations.append(ImportViolation(path, line, module_name))
    return violations


def main() -> int:
    violations = find_violations()
    if not violations:
        print("Import boundary check passed: trading_os does not import legacy roots.")
        return 0

    print("Import boundary check failed. Canonical trading_os imported legacy modules:")
    for item in violations:
        print(f"{item.file}:{item.line}: imports {item.imported_module}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
