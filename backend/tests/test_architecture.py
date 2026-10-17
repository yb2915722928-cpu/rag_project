from pathlib import Path
import ast


ROOT = Path(__file__).parents[1]


def test_all_eight_module_boundaries_exist() -> None:
    names = {
        "identity_access", "library", "indexing", "execution",
        "query", "ledger", "conversation", "platform_ops",
    }
    actual = {p.name for p in (ROOT / "src/rag_app/modules").iterdir() if p.is_dir()}
    assert names <= actual


def test_domain_modules_do_not_import_frameworks_or_orms() -> None:
    forbidden = ("fastapi", "sqlalchemy", "psycopg", "httpx")
    for path in (ROOT / "src/rag_app/modules").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert not any(f"import {name}" in source or f"from {name}" in source for name in forbidden)


def test_application_is_independent_of_framework_and_repository_never_commits() -> None:
    for path in (ROOT / "src/rag_app/application").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(n.name.split(".")[0] not in {"sqlalchemy", "fastapi"} for n in node.names)
            if isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in {"sqlalchemy", "fastapi"}
    tree = ast.parse((ROOT / "src/rag_app/adapters/postgres.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("Repository"):
            assert not any(isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                           and call.func.attr in {"commit", "rollback", "close"}
                           for call in ast.walk(node))

