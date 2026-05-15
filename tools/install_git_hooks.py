import shutil
import stat
import sys
from pathlib import Path


SOURCE_HOOK = Path("scripts/git-hooks/pre-commit")
TARGET_HOOK = Path(".git/hooks/pre-commit")


def ensure_git_repo() -> None:
    if not Path(".git").exists():
        raise RuntimeError("Este comando deve ser executado na raiz de um repositório Git.")


def install_pre_commit_hook() -> None:
    ensure_git_repo()

    if not SOURCE_HOOK.exists():
        raise FileNotFoundError(f"Hook fonte não encontrado: {SOURCE_HOOK}")

    TARGET_HOOK.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_HOOK, TARGET_HOOK)

    current_mode = TARGET_HOOK.stat().st_mode
    TARGET_HOOK.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> None:
    try:
        install_pre_commit_hook()
    except Exception as exc:
        print(f"Erro ao instalar hooks: {exc}")
        sys.exit(1)

    print("Hook pre-commit instalado com sucesso.")
    print(f"Origem: {SOURCE_HOOK}")
    print(f"Destino: {TARGET_HOOK}")
    print("")
    print("Teste com:")
    print(".git/hooks/pre-commit")


if __name__ == "__main__":
    main()
