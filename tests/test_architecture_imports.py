import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "agenticlens"
FORBIDDEN_IMPORTS = {
    "exporters": ("agenticlens.cli",),
    "comparison": ("agenticlens.cli",),
    "evaluation": ("agenticlens.cli",),
}


def _imports_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_package_layers_do_not_import_cli() -> None:
    for package, forbidden_prefixes in FORBIDDEN_IMPORTS.items():
        package_root = SRC_ROOT / package
        for file in package_root.rglob("*.py"):
            imports = _imports_in(file)
            assert not any(
                imported == prefix or imported.startswith(f"{prefix}.")
                for prefix in forbidden_prefixes
                for imported in imports
            ), f"{file} imports a forbidden module from {forbidden_prefixes!r}"
