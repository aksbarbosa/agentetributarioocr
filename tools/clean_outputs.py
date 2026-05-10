from pathlib import Path


OUTPUTS_DIR = Path("outputs")


FILES_TO_REMOVE = [
    "irpf-consolidado.json",
    "irpf-consolidado.report.md",
]


def clean_outputs() -> list[Path]:
    """
    Remove arquivos gerados conhecidos dentro da pasta outputs/.

    Não remove a pasta outputs/.
    Não remove arquivos fora de outputs/.
    """
    removed_files = []

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename in FILES_TO_REMOVE:
        file_path = OUTPUTS_DIR / filename

        if file_path.exists():
            file_path.unlink()
            removed_files.append(file_path)

    return removed_files


def main() -> None:
    removed_files = clean_outputs()

    if not removed_files:
        print("Nenhum arquivo de output para remover.")
        return

    print("Arquivos removidos:")

    for file_path in removed_files:
        print(f"- {file_path}")


if __name__ == "__main__":
    main()