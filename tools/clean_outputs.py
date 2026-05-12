from pathlib import Path


OUTPUT_FILES = [
    "outputs/irpf-consolidado.json",
    "outputs/irpf-consolidado.report.md",
    "outputs/agent-decision.json",
    "outputs/agent-decisions.json",
    "outputs/agent-decisions.report.md",
    "outputs/preflight-documents.json",
    "outputs/preflight-documents.report.md",
]


def remove_file(path_str: str) -> bool:
    """
    Remove um arquivo, se existir.

    Retorna True se removeu.
    Retorna False se o arquivo não existia.
    """
    path = Path(path_str)

    if not path.exists():
        return False

    if path.is_file():
        path.unlink()
        return True

    return False


def clean_outputs() -> list[str]:
    """
    Remove os outputs conhecidos gerados pelo projeto.
    """
    removed_files = []

    for output_file in OUTPUT_FILES:
        if remove_file(output_file):
            removed_files.append(output_file)

    return removed_files


def main() -> None:
    removed_files = clean_outputs()

    if removed_files:
        print("Arquivos removidos:")
        for file_path in removed_files:
            print(f"- {file_path}")
    else:
        print("Nenhum output conhecido para remover.")


if __name__ == "__main__":
    main()