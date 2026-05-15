import subprocess
import sys
from pathlib import Path


BLOCKED_PREFIXES = [
    "inputs/raw/",
    "inputs/raw_test_",
    "inputs/raw_ignored/",
    "inputs/private/",
    "inputs/real/",
    "outputs/",
]

ALLOWED_OUTPUT_FILES = {
    "outputs/.gitkeep",
}

BLOCKED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
    ".dec",
}


def get_tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Falha ao executar git ls-files.")

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_blocked_path(path: str) -> bool:
    if path in ALLOWED_OUTPUT_FILES:
        return False

    for prefix in BLOCKED_PREFIXES:
        if path.startswith(prefix):
            return True

    suffix = Path(path).suffix.lower()

    if suffix in BLOCKED_EXTENSIONS:
        return True

    return False


def find_blocked_files(files: list[str]) -> list[str]:
    return [path for path in files if is_blocked_path(path)]


def main() -> None:
    tracked_files = get_tracked_files()
    blocked_files = find_blocked_files(tracked_files)

    print("Checagem de segurança do repositório.")
    print(f"Arquivos rastreados: {len(tracked_files)}")

    if not blocked_files:
        print("Nenhum arquivo sensível rastreado encontrado.")
        return

    print("")
    print("Arquivos potencialmente sensíveis rastreados pelo Git:")

    for path in blocked_files:
        print(f"- {path}")

    print("")
    print("Remova esses arquivos do índice sem apagar localmente, por exemplo:")
    print("")
    print("git rm --cached <arquivo>")
    print("")
    print("Ou, para pastas:")
    print("")
    print("git rm --cached -r outputs inputs/raw")
    print("")
    print("Depois confirme com:")
    print("")
    print("git status --short")

    sys.exit(1)


if __name__ == "__main__":
    main()
