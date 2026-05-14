import subprocess
import sys
from pathlib import Path


EXECUTED_STEPS = []


def run_step(title: str, command: list[str], allow_failure: bool = False) -> int:
    """
    Executa uma etapa do fluxo real a partir de inputs/raw.
    """
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0 and not allow_failure:
        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    if result.returncode != 0 and allow_failure:
        print(f"Aviso: {title} retornou código {result.returncode}, mas o fluxo continuará.")

    EXECUTED_STEPS.append(title)
    print(f"OK: {title}")

    return result.returncode


def collect_structured_json_files(output_dir: str) -> list[Path]:
    """
    Coleta os JSONs estruturados gerados pelo fluxo real.
    """
    path = Path(output_dir)

    if not path.exists():
        return []

    return sorted(path.glob("*.json"))


def validate_structured_extractions(output_dir: str) -> None:
    """
    Valida todos os JSONs estruturados gerados em lote.
    """
    files = collect_structured_json_files(output_dir)

    print("")
    print("==> Validar extrações estruturadas geradas")

    if not files:
        print("Nenhuma extração estruturada gerada para validar.")
        EXECUTED_STEPS.append("Validar extrações estruturadas geradas")
        print("OK: Validar extrações estruturadas geradas")
        return

    for file_path in files:
        command = [sys.executable, "tools/validate_extracted.py", str(file_path)]
        print("$ " + " ".join(command))

        result = subprocess.run(command)

        if result.returncode != 0:
            print(f"Falhou ao validar: {file_path}")
            sys.exit(result.returncode)

    EXECUTED_STEPS.append("Validar extrações estruturadas geradas")
    print("OK: Validar extrações estruturadas geradas")


def print_final_summary() -> None:
    """
    Imprime resumo final do fluxo.
    """
    print("")
    print("Fluxo real a partir de inputs/raw finalizado.")
    print("")
    print("Etapas executadas:")

    for step in EXECUTED_STEPS:
        print(f"- {step}")

    print("")
    print("Saídas principais:")
    print("- outputs/raw-inputs-manifest.json")
    print("- outputs/raw-inputs-manifest.report.md")
    print("- outputs/extract-text.json")
    print("- outputs/extract-text.report.md")
    print("- outputs/extracted_text/")
    print("- outputs/preflight-documents.json")
    print("- outputs/preflight-documents.report.md")
    print("- outputs/structured_extractions/")
    print("- outputs/structured-extractions-batch.json")
    print("- outputs/structured-extractions-batch.report.md")
    print("- outputs/promoted_extractions/")
    print("- outputs/promote-structured-extractions.json")
    print("- outputs/promote-structured-extractions.report.md")


def main() -> None:
    print("Iniciando fluxo real a partir de inputs/raw.")

    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/extracted_text").mkdir(parents=True, exist_ok=True)
    Path("outputs/structured_extractions").mkdir(parents=True, exist_ok=True)
    Path("outputs/promoted_extractions").mkdir(parents=True, exist_ok=True)

    run_step(
        "Escanear documentos brutos",
        [sys.executable, "tools/scan_raw_inputs.py", "inputs/raw"],
    )

    run_step(
        "Extrair texto dos documentos brutos",
        [sys.executable, "tools/extract_text.py", "inputs/raw"],
    )

    run_step(
        "Rodar pré-triagem dos textos extraídos",
        [sys.executable, "tools/preflight_documents.py", "outputs/extracted_text"],
        allow_failure=True,
    )

    run_step(
        "Gerar extrações estruturadas em lote",
        [sys.executable, "tools/extract_structured_batch.py", "outputs/extracted_text"],
    )

    validate_structured_extractions("outputs/structured_extractions")

    run_step(
        "Promover extrações estruturadas válidas para pasta segura",
        [
            sys.executable,
            "tools/promote_structured_extractions.py",
            "outputs/structured_extractions",
            "outputs/promoted_extractions",
            "outputs/promote-structured-extractions.json",
            "outputs/promote-structured-extractions.report.md",
        ],
    )

    print_final_summary()


if __name__ == "__main__":
    main()