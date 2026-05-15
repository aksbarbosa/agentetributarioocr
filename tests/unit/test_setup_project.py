import os
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import setup_project as module


def test_required_paths_are_declared():
    expected = {
        Path("tools"),
        Path("tests"),
        Path("config/project_config.json"),
        Path("config/ocr_config.json"),
        Path("requirements.txt"),
    }

    assert set(module.REQUIRED_PATHS) == expected


def test_ensure_project_root_accepts_valid_structure():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        original_cwd = Path.cwd()

        try:
            os.chdir(tmp_dir)

            Path("tools").mkdir()
            Path("tests").mkdir()
            Path("config").mkdir()
            Path("config/project_config.json").write_text("{}", encoding="utf-8")
            Path("config/ocr_config.json").write_text("{}", encoding="utf-8")
            Path("requirements.txt").write_text("", encoding="utf-8")

            module.ensure_project_root()

        finally:
            os.chdir(original_cwd)


def test_ensure_project_root_fails_with_missing_structure():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        original_cwd = Path.cwd()

        try:
            os.chdir(tmp_dir)

            try:
                module.ensure_project_root()
            except SystemExit as exc:
                assert exc.code == 1
                return

            raise AssertionError("Estrutura inválida foi aceita.")

        finally:
            os.chdir(original_cwd)


def run_tests():
    test_required_paths_are_declared()
    test_ensure_project_root_accepts_valid_structure()
    test_ensure_project_root_fails_with_missing_structure()

    print("test_setup_project.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()