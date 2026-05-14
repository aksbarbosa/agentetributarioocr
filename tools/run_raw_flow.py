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


def main() -> None:
    print("Iniciando fluxo real a partir de inputs/raw.")

    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/extracted_text").mkdir(parents=True, exist_ok=True)
    Path("outputs/structured_extractions").mkdir(parents=True, exist_ok=True)

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

    print_final_summary()


if __name__ == "__main__":
    main()