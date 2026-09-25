import ast
import os
import sys

from app.infrastructure.isolation_guard import PROHIBITED_DB_MODULES, verify_zero_database_isolation


def test_runtime_database_isolation():
    """Verify that zero database drivers are loaded in the Python runtime."""
    assert verify_zero_database_isolation() is True
    for mod in PROHIBITED_DB_MODULES:
        assert mod not in sys.modules, f"Prohibited module {mod} found in sys.modules"


def test_static_ast_codebase_isolation():
    """
    Static AST Codebase Scan:
    Inspects all Python source files in app/ to verify that no database/ORM libraries
    are imported or referenced.
    """
    app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
    python_files = []

    for root, _, files in os.walk(app_dir):
        for f in files:
            if f.endswith(".py"):
                python_files.append(os.path.join(root, f))

    assert len(python_files) > 0, "No python files found in app directory"

    for file_path in python_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        base_mod = alias.name.split(".")[0]
                        assert base_mod not in PROHIBITED_DB_MODULES, (
                            f"Prohibited import '{alias.name}' detected in {file_path}"
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        base_mod = node.module.split(".")[0]
                        assert base_mod not in PROHIBITED_DB_MODULES, (
                            f"Prohibited from-import '{node.module}' detected in {file_path}"
                        )
