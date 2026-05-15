import subprocess
import sys
from pathlib import Path


RAW_INPUT_DIR = "inputs/raw"
PREPARED_INPUT_DIR = "outputs/raw_prepared_for_ocr"

PREPARE_JSON = "outputs/prepare-raw-for-ocr.json"
PREPARE_REPORT = "outputs/prepare-raw-for-ocr.report.md"

EXTRACTED_TEXT_DIR = "outputs/extracted_text_prepared"
EXTRACT_TEXT_JSON = "outputs/extract-text-prepared.json"
EXTRACT_TEXT_REPORT = "outputs/extract-text-prepared.report.md"

PREFLIGHT_JSON = "outputs/preflight-documents-prepared.json"
PREFLIGHT_REPORT = "outputs/preflight-documents-prepared.report.md"

STRUCTURED_DIR = "outputs/structured_extractions_prepared"
STRUCTURED_JSON = "outputs/structured-extractions-prepared.json"
STRUCTURED_REPORT = "outputs/structured-extractions-prepared.report.md"

PROMOTED_DIR = "outputs/promoted_extractions_prepared"
PROMOTE_JSON = "outputs/promote-structured-extractions-prepared.json"
PROMOTE_REPORT = "outputs/promote-structured-extractions-prepared.report.md"

REVIEW_JSON = "outputs/review-promoted-extractions-prepared.json"
REVIEW_REPORT = "outputs/review-promoted-extractions-prepared.report.md"

COMPARE_JSON = "outputs/compare-ocr-outputs.json"
COMPARE_REPORT = "outputs/compare-ocr-outputs.report.md"


def run_step(title: str, command: list[str], allow_failure: bool = False) -> None:
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        if allow_failure:
            print(f"Aviso: {title} retornou código {result.returncode}, mas o fluxo continuará.")
            return

        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")


def validate_structured_extractions() -> None:
    structured_path = Path(STRUCTURED_DIR)

    if not structured_path.exists():
        print("")
        print("Aviso: pasta de extrações estruturadas não existe.")
        return

    files = sorted(structured_path.glob("*.json"))

    if not files:
        print("")
        print("Aviso: nenhuma extração estruturada para validar.")
        return

    print("")
    print("==> Validar extrações estruturadas preparadas")

    for file_path in files:
        command = [
            sys.executable,
            "tools/validate_extracted.py",
            str(file_path),
        ]

        print("$ " + " ".join(command))
        result = subprocess.run(command)

        if result.returncode != 0:
            print(f"Falhou ao validar: {file_path}")
            sys.exit(result.returncode)

    print("OK: Validar extrações estruturadas preparadas")


def main() -> None:
    print("Iniciando fluxo com documentos preparados para OCR.")

    run_step(
        "Preparar documentos brutos para OCR",
        [
            sys.executable,
            "tools/prepare_raw_for_ocr.py",
            RAW_INPUT_DIR,
            PREPARED_INPUT_DIR,
            PREPARE_JSON,
            PREPARE_REPORT,
        ],
        allow_failure=True,
    )

    run_step(
        "Extrair texto dos documentos preparados",
        [
            sys.executable,
            "tools/extract_text.py",
            PREPARED_INPUT_DIR,
            EXTRACTED_TEXT_DIR,
            EXTRACT_TEXT_JSON,
            EXTRACT_TEXT_REPORT,
        ],
    )

    run_step(
        "Rodar pré-triagem dos textos preparados",
        [
            sys.executable,
            "tools/preflight_documents.py",
            EXTRACTED_TEXT_DIR,
            PREFLIGHT_JSON,
            PREFLIGHT_REPORT,
        ],
        allow_failure=True,
    )

    run_step(
        "Gerar extrações estruturadas dos textos preparados",
        [
            sys.executable,
            "tools/extract_structured_batch.py",
            EXTRACTED_TEXT_DIR,
            STRUCTURED_DIR,
            STRUCTURED_JSON,
            STRUCTURED_REPORT,
        ],
    )

    validate_structured_extractions()

    run_step(
        "Promover extrações estruturadas preparadas",
        [
            sys.executable,
            "tools/promote_structured_extractions.py",
            STRUCTURED_DIR,
            PROMOTED_DIR,
            PROMOTE_JSON,
            PROMOTE_REPORT,
        ],
    )

    run_step(
        "Gerar revisão assistida das extrações preparadas",
        [
            sys.executable,
            "tools/review_promoted_extractions.py",
            PROMOTED_DIR,
            REVIEW_JSON,
            REVIEW_REPORT,
        ],
    )

    run_step(
        "Comparar OCR normal e OCR preparado",
        [
            sys.executable,
            "tools/compare_ocr_outputs.py",
            "outputs/extracted_text",
            EXTRACTED_TEXT_DIR,
            COMPARE_JSON,
            COMPARE_REPORT,
        ],
        allow_failure=True,
    )

    print("")
    print("Fluxo com documentos preparados para OCR finalizado.")
    print("")
    print("Saídas principais:")
    print(f"- {PREPARE_REPORT}")
    print(f"- {EXTRACT_TEXT_REPORT}")
    print(f"- {PREFLIGHT_REPORT}")
    print(f"- {STRUCTURED_REPORT}")
    print(f"- {PROMOTE_REPORT}")
    print(f"- {REVIEW_REPORT}")
    print(f"- {COMPARE_REPORT}")
    print(f"- {EXTRACTED_TEXT_DIR}/")
    print(f"- {STRUCTURED_DIR}/")
    print(f"- {PROMOTED_DIR}/")


if __name__ == "__main__":
    main()
