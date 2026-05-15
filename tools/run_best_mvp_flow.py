import json
import shutil
import subprocess
import sys
from pathlib import Path


REVIEW_JSON = "outputs/review-promoted-extractions-best.json"
REVIEW_REPORT = "outputs/review-promoted-extractions-best.report.md"

MANUAL_REVIEW_PACK_JSON = "outputs/manual-review-pack-best.json"
MANUAL_REVIEW_PACK_REPORT = "outputs/manual-review-pack-best.report.md"

APPROVED_DIR = Path("outputs/approved_best")
APPROVAL_JSON = "outputs/approve-promoted-extractions-best.json"
APPROVAL_REPORT = "outputs/approve-promoted-extractions-best.report.md"

CONSOLIDATED_JSON = "outputs/irpf-consolidado-best.json"
CONSOLIDATED_REPORT = "outputs/irpf-consolidado-best.report.md"

DEC_EXPERIMENTAL_TXT = "outputs/irpf-export-dec-experimental-best.txt"
DEC_EXPERIMENTAL_REPORT = "outputs/irpf-export-dec-experimental-best.report.md"


def run_step(title: str, command: list[str], allow_failure: bool = False) -> int:
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        if allow_failure:
            print(f"Aviso: {title} retornou código {result.returncode}, mas o fluxo continuará.")
            return result.returncode

        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")
    return result.returncode


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        return {}

    return json.loads(file_path.read_text(encoding="utf-8"))


def get_pending_review_count(pack_path: str) -> int:
    data = load_json(pack_path)
    summary = data.get("summary", {})

    return int(summary.get("pending_field_count", 0) or 0)


def clean_approved_dir() -> None:
    if APPROVED_DIR.exists():
        shutil.rmtree(APPROVED_DIR)

    APPROVED_DIR.mkdir(parents=True, exist_ok=True)


def print_outputs(include_dec: bool) -> None:
    print("")
    print("Saídas principais:")
    print("- outputs/select-best-ocr-outputs.report.md")
    print("- outputs/structured-extractions-best.report.md")
    print(f"- {REVIEW_REPORT}")
    print(f"- {MANUAL_REVIEW_PACK_REPORT}")
    print(f"- {APPROVAL_REPORT}")
    print(f"- {CONSOLIDATED_JSON}")
    print(f"- {CONSOLIDATED_REPORT}")

    if include_dec:
        print(f"- {DEC_EXPERIMENTAL_TXT}")
        print(f"- {DEC_EXPERIMENTAL_REPORT}")


def main() -> None:
    print("Iniciando MVP com seleção do melhor OCR.")

    run_step(
        "Rodar fluxo best OCR até revisão assistida",
        [
            sys.executable,
            "tools/run_best_ocr_flow.py",
        ],
    )

    review_pack_code = run_step(
        "Gerar pacote de revisão manual best",
        [
            sys.executable,
            "tools/generate_manual_review_pack.py",
            REVIEW_JSON,
            MANUAL_REVIEW_PACK_JSON,
            MANUAL_REVIEW_PACK_REPORT,
        ],
        allow_failure=True,
    )

    pending_count = get_pending_review_count(MANUAL_REVIEW_PACK_JSON)

    if review_pack_code != 0 or pending_count > 0:
        print("")
        print("Fluxo best MVP interrompido para revisão humana.")
        print(f"Campos pendentes: {pending_count}")
        print("")
        print("Revise:")
        print(f"- {MANUAL_REVIEW_PACK_JSON}")
        print(f"- {MANUAL_REVIEW_PACK_REPORT}")
        print("")
        print("Depois, aplique as correções ou crie continuação específica para best OCR.")
        print_outputs(include_dec=False)
        sys.exit(1)

    clean_approved_dir()

    run_step(
        "Aprovar extrações best",
        [
            sys.executable,
            "tools/approve_promoted_extractions.py",
            REVIEW_JSON,
            str(APPROVED_DIR),
            APPROVAL_JSON,
            APPROVAL_REPORT,
        ],
    )

    run_step(
        "Gerar JSON canônico best",
        [
            sys.executable,
            "tools/run_project.py",
            str(APPROVED_DIR),
            CONSOLIDATED_JSON,
            CONSOLIDATED_REPORT,
        ],
    )

    run_step(
        "Gerar exportação DEC experimental best",
        [
            sys.executable,
            "tools/export_dec_experimental.py",
            CONSOLIDATED_JSON,
            DEC_EXPERIMENTAL_TXT,
            DEC_EXPERIMENTAL_REPORT,
        ],
    )

    print("")
    print("MVP com seleção do melhor OCR finalizado com sucesso.")
    print_outputs(include_dec=True)


if __name__ == "__main__":
    main()
