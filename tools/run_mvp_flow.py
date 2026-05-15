import subprocess
import sys
from pathlib import Path


def run_step(title: str, command: list[str]) -> None:
    """
    Executa uma etapa do MVP.
    """
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")


def main() -> None:
    """
    Executa o fluxo MVP completo:
    inputs/raw -> extrações -> aprovação segura -> JSON canônico.
    """
    print("Iniciando fluxo MVP completo.")

    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/approved_test").mkdir(parents=True, exist_ok=True)

    run_step(
        "Rodar fluxo bruto com OCR, extração estruturada, promoção e revisão",
        [sys.executable, "tools/run_raw_flow.py"],
    )

    run_step(
        "Aprovar extrações promovidas para pasta segura",
        [
            sys.executable,
            "tools/approve_promoted_extractions.py",
            "outputs/review-promoted-extractions.json",
            "outputs/approved_test",
            "outputs/approve-promoted-extractions.json",
            "outputs/approve-promoted-extractions.report.md",
        ],
    )

    run_step(
        "Rodar pipeline canônico com extrações aprovadas",
        [
            sys.executable,
            "tools/run_project.py",
            "outputs/approved_test",
        ],
    )
    run_step(
    "Gerar exportação DEC experimental",
    [
        sys.executable,
        "tools/export_dec_experimental.py",
        "outputs/irpf-consolidado.json",
        "outputs/irpf-export-dec-experimental.txt",
        "outputs/irpf-export-dec-experimental.report.md",
    ],
)

    print("")
    print("Fluxo MVP completo finalizado.")
    print("")
    print("Saídas principais:")
    print("- outputs/extract-text.report.md")
    print("- outputs/structured-extractions-batch.report.md")
    print("- outputs/promote-structured-extractions.report.md")
    print("- outputs/review-promoted-extractions.report.md")
    print("- outputs/approve-promoted-extractions.report.md")
    print("- outputs/irpf-consolidado.json")
    print("- outputs/irpf-consolidado.report.md")
    print("- outputs/irpf-export-dec-experimental.txt")
    print("- outputs/irpf-export-dec-experimental.report.md")


if __name__ == "__main__":
    main()