import json
import shutil
import subprocess
import sys
from pathlib import Path


MANUAL_REVIEW_PACK_JSON = "outputs/manual-review-pack.json"
MANUAL_REVIEW_PACK_REPORT = "outputs/manual-review-pack.report.md"

APPLY_JSON = "outputs/apply-manual-review-pack.json"
APPLY_REPORT = "outputs/apply-manual-review-pack.report.md"

REVIEW_JSON = "outputs/review-promoted-extractions.json"
REVIEW_REPORT = "outputs/review-promoted-extractions.report.md"

APPROVED_DIR = Path("outputs/approved_test")
APPROVAL_JSON = "outputs/approve-promoted-extractions.json"
APPROVAL_REPORT = "outputs/approve-promoted-extractions.report.md"

CONSOLIDATED_JSON = "outputs/irpf-consolidado.json"
CONSOLIDATED_REPORT = "outputs/irpf-consolidado.report.md"

DEC_EXPERIMENTAL_TXT = "outputs/irpf-export-dec-experimental.txt"
DEC_EXPERIMENTAL_REPORT = "outputs/irpf-export-dec-experimental.report.md"


def run_step(title: str, command: list[str]) -> None:
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")


def run_review_pack_step() -> int:
    print("")
    print("==> Gerar novo pacote de revisão manual")
    command = [
        sys.executable,
        "tools/generate_manual_review_pack.py",
        REVIEW_JSON,
        MANUAL_REVIEW_PACK_JSON,
        MANUAL_REVIEW_PACK_REPORT,
    ]
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode == 0:
        print("OK: Gerar novo pacote de revisão manual")
    else:
        print("Atenção: ainda há pendências de revisão manual.")

    return result.returncode


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        return {}

    return json.loads(file_path.read_text(encoding="utf-8"))


def get_pending_review_count() -> int:
    data = load_json(MANUAL_REVIEW_PACK_JSON)
    summary = data.get("summary", {})

    return int(summary.get("pending_field_count", 0) or 0)


def clean_approved_dir() -> None:
    if APPROVED_DIR.exists():
        shutil.rmtree(APPROVED_DIR)

    APPROVED_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("Continuando fluxo após revisão manual.")

    run_step(
        "Aplicar pacote de revisão manual",
        [
            sys.executable,
            "tools/apply_manual_review_pack.py",
            MANUAL_REVIEW_PACK_JSON,
            APPLY_JSON,
            APPLY_REPORT,
        ],
    )

    run_step(
        "Revisar novamente extrações promovidas",
        [
            sys.executable,
            "tools/review_promoted_extractions.py",
            "outputs/promoted_extractions",
            REVIEW_JSON,
            REVIEW_REPORT,
        ],
    )

    review_code = run_review_pack_step()
    pending_count = get_pending_review_count()

    if review_code != 0 or pending_count > 0:
        print("")
        print("Fluxo interrompido: ainda há pendências de revisão.")
        print(f"Campos pendentes: {pending_count}")
        print("")
        print("Revise novamente:")
        print(f"- {MANUAL_REVIEW_PACK_JSON}")
        print(f"- {MANUAL_REVIEW_PACK_REPORT}")
        sys.exit(1)

    clean_approved_dir()

    run_step(
        "Aprovar extrações corrigidas",
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
        "Gerar JSON canônico",
        [
            sys.executable,
            "tools/run_project.py",
            str(APPROVED_DIR),
            CONSOLIDATED_JSON,
            CONSOLIDATED_REPORT,
        ],
    )

    run_step(
        "Gerar exportação DEC experimental",
        [
            sys.executable,
            "tools/export_dec_experimental.py",
            CONSOLIDATED_JSON,
            DEC_EXPERIMENTAL_TXT,
            DEC_EXPERIMENTAL_REPORT,
        ],
    )

    print("")
    print("Fluxo pós-revisão manual finalizado com sucesso.")
    print("")
    print("Saídas principais:")
    print(f"- {CONSOLIDATED_JSON}")
    print(f"- {CONSOLIDATED_REPORT}")
    print(f"- {DEC_EXPERIMENTAL_TXT}")
    print(f"- {DEC_EXPERIMENTAL_REPORT}")


if __name__ == "__main__":
    main()