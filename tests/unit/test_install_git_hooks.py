import os
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import install_git_hooks as module


def write_hook(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/bin/sh\n"
        "echo hook ok\n",
        encoding="utf-8",
    )


def test_install_pre_commit_hook_copies_file_and_sets_executable():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        original_cwd = Path.cwd()

        original_source = module.SOURCE_HOOK
        original_target = module.TARGET_HOOK

        try:
            os.chdir(tmp_dir)

            Path(".git/hooks").mkdir(parents=True, exist_ok=True)
            source_hook = tmp_dir / "scripts/git-hooks/pre-commit"
            target_hook = tmp_dir / ".git/hooks/pre-commit"

            write_hook(source_hook)

            module.SOURCE_HOOK = Path("scripts/git-hooks/pre-commit")
            module.TARGET_HOOK = Path(".git/hooks/pre-commit")

            module.install_pre_commit_hook()

            assert target_hook.exists()
            assert target_hook.read_text(encoding="utf-8") == source_hook.read_text(
                encoding="utf-8"
            )
            assert os.access(target_hook, os.X_OK)

        finally:
            os.chdir(original_cwd)
            module.SOURCE_HOOK = original_source
            module.TARGET_HOOK = original_target


def test_install_pre_commit_hook_fails_outside_git_repo():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        original_cwd = Path.cwd()

        original_source = module.SOURCE_HOOK
        original_target = module.TARGET_HOOK

        try:
            os.chdir(tmp_dir)

            module.SOURCE_HOOK = Path("scripts/git-hooks/pre-commit")
            module.TARGET_HOOK = Path(".git/hooks/pre-commit")

            try:
                module.install_pre_commit_hook()
            except RuntimeError as exc:
                assert "raiz de um repositório Git" in str(exc)
                return

            raise AssertionError("Instalação fora de repositório Git foi aceita.")

        finally:
            os.chdir(original_cwd)
            module.SOURCE_HOOK = original_source
            module.TARGET_HOOK = original_target


def test_install_pre_commit_hook_fails_without_source_hook():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        original_cwd = Path.cwd()

        original_source = module.SOURCE_HOOK
        original_target = module.TARGET_HOOK

        try:
            os.chdir(tmp_dir)

            Path(".git/hooks").mkdir(parents=True, exist_ok=True)

            module.SOURCE_HOOK = Path("scripts/git-hooks/pre-commit")
            module.TARGET_HOOK = Path(".git/hooks/pre-commit")

            try:
                module.install_pre_commit_hook()
            except FileNotFoundError as exc:
                assert "Hook fonte não encontrado" in str(exc)
                return

            raise AssertionError("Instalação sem hook fonte foi aceita.")

        finally:
            os.chdir(original_cwd)
            module.SOURCE_HOOK = original_source
            module.TARGET_HOOK = original_target


def run_tests():
    test_install_pre_commit_hook_copies_file_and_sets_executable()
    test_install_pre_commit_hook_fails_outside_git_repo()
    test_install_pre_commit_hook_fails_without_source_hook()

    print("test_install_git_hooks.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()