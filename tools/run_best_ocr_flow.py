import subprocess
import sys
from pathlib import Path


RAW_INPUT_DIR = "inputs/raw"

PREPARED_INPUT_DIR = "outputs/raw_prepared_for_ocr"

EXTRACTED_TEXT_DIR = "outputs/extracted_text"
EXTRACT_TEXT_JSON = "outputs/extract-text.json"
EXTRACT_TEXT_REPORT = "outputs/extract-text.report.md"

EXTRACTED_TEXT_PREPARED_DIR = "outputs/extracted_text_prepared"
EXTRACT_TEXT_PREPARED_JSON = "outputs/extract-text-prepared.json"
EXTRACT_TEXT_PREPARED_REPORT = "outputs/extract-text-prepared.report.md"

BEST_TEXT_DIR = "outputs/extracted_text_best"
BEST_TEXT_JSON = "outputs/select-best-ocr-outputs.json"
BEST_TEXT_REPORT = "outputs/select-best-ocr-outputs.report.md"

COMPARE_JSON = "outputs/compare-ocr-outputs.json"
COMPARE_REPORT = "outputs/compare-ocr-outputs.report.md"

STRUCTURED_DIR = "outputs/structured_extractions_best"
STRUCTURED_JSON = "outputs/structured-extractions-best.json"
STRUCTURED_REPORT = "outputs/structured-extractions-best.report.md"

PROMOTED_DIR = "outputs/promoted_extractions_best"
PROMOTE_JSON = "outputs/promote-structured-extractions-best.json"
PROMOTE_REPORT = "outputs/promote-structured-extractions-best.report.md"

REVIEW_JSON = "outputs/review-promoted-extractions-best.json"
REVIEW_REPORT = "outputs/review-promoted-extractions-best.report.md"


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
        print("Aviso: pasta de extrações estruturadas best não existe.")
        return

    files = sorted(structured_path.glob("*.json"))

    if not files:
        print("")
        print("Aviso: nenhuma extração estruturada best para validar.")
        return

    print("")
    print("==> Validar extrações estruturadas best")

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

    print("OK: Validar extrações estruturadas best")


def main() -> None:
    print("Iniciando fluxo com seleção do melhor OCR.")

    run_step(
        "Rodar OCR normal a partir de inputs/raw",
        [
            sys.executable,
            "tools/extract_text.py",
            RAW_INPUT_DIR,
            EXTRACTED_TEXT_DIR,
            EXTRACT_TEXT_JSON,
            EXTRACT_TEXT_REPORT,
        ],
        allow_failure=True,
    )

    run_step(
        "Preparar documentos brutos para OCR",
        [
            sys.executable,
            "tools/prepare_raw_for_ocr.py",
            RAW_INPUT_DIR,
            PREPARED_INPUT_DIR,
            "outputs/prepare-raw-for-ocr.json",
            "outputs/prepare-raw-for-ocr.report.md",
        ],
        allow_failure=True,
    )

    run_step(
        "Rodar OCR nos documentos preparados",
        [
            sys.executable,
            "tools/extract_text.py",
            PREPARED_INPUT_DIR,
            EXTRACTED_TEXT_PREPARED_DIR,
            EXTRACT_TEXT_PREPARED_JSON,
            EXTRACT_TEXT_PREPARED_REPORT,
        ],
        allow_failure=True,
    )

    run_step(
        "Comparar OCR normal e OCR preparado",
        [
            sys.executable,
            "tools/compare_ocr_outputs.py",
            EXTRACTED_TEXT_DIR,
            EXTRACTED_TEXT_PREPARED_DIR,
            COMPARE_JSON,
            COMPARE_REPORT,
        ],
        allow_failure=True,
    )

    run_step(
        "Selecionar melhor OCR por documento",
        [
            sys.executable,
            "tools/select_best_ocr_outputs.py",
            EXTRACTED_TEXT_DIR,
            EXTRACTED_TEXT_PREPARED_DIR,
            BEST_TEXT_DIR,
            BEST_TEXT_JSON,
            BEST_TEXT_REPORT,
        ],
    )

    run_step(
        "Rodar pré-triagem nos melhores textos",
        [
            sys.executable,
            "tools/preflight_documents.py",
            BEST_TEXT_DIR,
            "outputs/preflight-documents-best.json",
            "outputs/preflight-documents-best.report.md",
        ],
        allow_failure=True,
    )

    run_step(
        "Gerar extrações estruturadas com melhor OCR",
        [
            sys.executable,
            "tools/extract_structured_batch.py",
            BEST_TEXT_DIR,
            STRUCTURED_DIR,
            STRUCTURED_JSON,
            STRUCTURED_REPORT,
        ],
    )

    validate_structured_extractions()

    run_step(
        "Promover extrações estruturadas best",
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
        "Gerar revisão assistida best",
        [
            sys.executable,
            "tools/review_promoted_extractions.py",
            PROMOTED_DIR,
            REVIEW_JSON,
            REVIEW_REPORT,
        ],
    )

    print("")
    print("Fluxo com seleção do melhor OCR finalizado.")
    print("")
    print("Saídas principais:")
    print(f"- {EXTRACT_TEXT_REPORT}")
    print(f"- {EXTRACT_TEXT_PREPARED_REPORT}")
    print(f"- {COMPARE_REPORT}")
    print(f"- {BEST_TEXT_REPORT}")
    print(f"- {STRUCTURED_REPORT}")
    print(f"- {PROMOTE_REPORT}")
    print(f"- {REVIEW_REPORT}")
    print(f"- {BEST_TEXT_DIR}/")
    print(f"- {STRUCTURED_DIR}/")
    print(f"- {PROMOTED_DIR}/")


if __name__ == "__main__":
    main()
