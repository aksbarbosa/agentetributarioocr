import json
from pathlib import Path


PATHS = {
    "review_json": Path("outputs/review-promoted-extractions.json"),
    "manual_pack": Path("outputs/manual-review-pack.json"),
    "approved_dir": Path("outputs/approved_test"),
    "canonical_json": Path("outputs/irpf-consolidado.json"),
    "canonical_report": Path("outputs/irpf-consolidado.report.md"),
    "dec_export": Path("outputs/irpf-export-dec-experimental.txt"),
    "dec_report": Path("outputs/irpf-export-dec-experimental.report.md"),
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def count_json_files(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0

    return len(list(path.glob("*.json")))


def get_manual_pending_count() -> int:
    data = load_json(PATHS["manual_pack"])
    summary = data.get("summary", {})

    return int(summary.get("pending_field_count", 0) or 0)


def get_review_summary() -> dict:
    data = load_json(PATHS["review_json"])
    summary = data.get("summary", {})

    return summary if isinstance(summary, dict) else {}


def detect_status() -> tuple[str, str]:
    pending_count = get_manual_pending_count()
    approved_count = count_json_files(PATHS["approved_dir"])

    if PATHS["manual_pack"].exists() and pending_count > 0:
        return (
            "aguardando revisão manual",
            "Preencha outputs/manual-review-pack.json e depois rode: python3 tools/continue_after_manual_review.py",
        )

    if PATHS["manual_pack"].exists() and pending_count == 0 and approved_count == 0:
        return (
            "revisão manual sem pendências, aguardando continuação",
            "Rode: python3 tools/continue_after_manual_review.py",
        )

    if approved_count > 0 and not PATHS["canonical_json"].exists():
        return (
            "extrações aprovadas, aguardando JSON canônico",
            "Rode: python3 tools/run_project.py outputs/approved_test",
        )

    if PATHS["canonical_json"].exists() and not PATHS["dec_export"].exists():
        return (
            "JSON canônico gerado, aguardando exportação experimental",
            "Rode: python3 tools/export_dec_experimental.py",
        )

    if PATHS["canonical_json"].exists() and PATHS["dec_export"].exists():
        return (
            "fluxo completo finalizado",
            "Revise outputs/irpf-consolidado.report.md e outputs/irpf-export-dec-experimental.report.md",
        )

    if PATHS["review_json"].exists():
        return (
            "revisão assistida gerada",
            "Rode: python3 tools/generate_manual_review_pack.py",
        )

    return (
        "fluxo ainda não iniciado ou outputs limpos",
        "Rode: python3 tools/run_mvp_flow.py",
    )


def main() -> None:
    status, next_step = detect_status()

    pending_count = get_manual_pending_count()
    approved_count = count_json_files(PATHS["approved_dir"])
    review_summary = get_review_summary()

    print("Status do projeto IRPF OCR DEC")
    print("")
    print(f"Status atual: {status}")
    print(f"Próximo passo: {next_step}")
    print("")
    print("Resumo:")
    print(f"- Pendências no pacote manual: {pending_count}")
    print(f"- Arquivos aprovados em outputs/approved_test: {approved_count}")

    if review_summary:
        print(f"- Resumo da revisão assistida: {review_summary}")

    print("")
    print("Arquivos principais:")

    for label, path in PATHS.items():
        exists = "sim" if path.exists() else "não"
        print(f"- {label}: {path} — existe: {exists}")


if __name__ == "__main__":
    main()