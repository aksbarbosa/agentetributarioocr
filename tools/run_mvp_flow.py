import json
import shutil
import subprocess
import sys
from pathlib import Path


APPROVED_DIR = Path("outputs/approved_test")

REVIEW_JSON = "outputs/review-promoted-extractions.json"
MANUAL_REVIEW_PACK_JSON = "outputs/manual-review-pack.json"
MANUAL_REVIEW_PACK_REPORT = "outputs/manual-review-pack.report.md"

APPROVAL_JSON = "outputs/approve-promoted-extractions.json"
APPROVAL_REPORT = "outputs/approve-promoted-extractions.report.md"

CONSOLIDATED_JSON = "outputs/irpf-consolidado.json"
CONSOLIDATED_REPORT = "outputs/irpf-consolidado.report.md"

DEC_EXPERIMENTAL_TXT = "outputs/irpf-export-dec-experimental.txt"
DEC_EXPERIMENTAL_REPORT = "outputs/irpf-export-dec-experimental.report.md"


def run_step(title: str, command: list[str]) -> None:
    """
    Executa uma etapa obrigatória do MVP.

    Se a etapa falhar, interrompe o fluxo.
    """
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")


def run_optional_review_step(title: str, command: list[str]) -> int:
    """
    Executa a etapa de revisão manual.

    Retorna o código de saída para que o fluxo decida se deve parar.
    """
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode == 0:
        print(f"OK: {title}")
    else:
        print(f"Atenção: {title} encontrou pendências.")

    return result.returncode


def load_json(path: str) -> dict:
    """
    Carrega JSON se existir.
    """
    file_path = Path(path)

    if not file_path.exists():
        return {}

    return json.loads(file_path.read_text(encoding="utf-8"))


def get_pending_review_count(pack_path: str) -> int:
    """
    Lê a quantidade de campos pendentes no pacote de revisão manual.
    """
    data = load_json(pack_path)
    summary = data.get("summary", {})

    return int(summary.get("pending_field_count", 0) or 0)


def clean_approved_dir() -> None:
    """
    Limpa a pasta de aprovação segura antes de aprovar novos arquivos.

    Isso evita que arquivos antigos continuem em outputs/approved_test
    depois de uma nova revisão.
    """
    if APPROVED_DIR.exists():
        shutil.rmtree(APPROVED_DIR)

    APPROVED_DIR.mkdir(parents=True, exist_ok=True)


def print_final_outputs(include_dec: bool) -> None:
    """
    Imprime as principais saídas do fluxo.
    """
    print("")
    print("Saídas principais:")
    print("- outputs/extract-text.report.md")
    print("- outputs/structured-extractions-batch.report.md")
    print("- outputs/promote-structured-extractions.report.md")
    print("- outputs/review-promoted-extractions.report.md")
    print("- outputs/manual-review-pack.json")
    print("- outputs/manual-review-pack.report.md")
    print("- outputs/approve-promoted-extractions.report.md")
    print("- outputs/irpf-consolidado.json")
    print("- outputs/irpf-consolidado.report.md")

    if include_dec:
        print("- outputs/irpf-export-dec-experimental.txt")
        print("- outputs/irpf-export-dec-experimental.report.md")


def main() -> None:
    """
    Executa o fluxo MVP completo de forma segura.

    Fluxo:
    1. inputs/raw -> OCR/texto -> extração estruturada -> promoção -> revisão
    2. gera pacote de revisão manual
    3. se houver pendências, para antes da aprovação/canônico
    4. se não houver pendências, aprova para outputs/approved_test
    5. roda pipeline canônico usando outputs/approved_test
    6. gera exportação DEC experimental somente se o canônico for válido
    """
    print("Iniciando fluxo MVP completo.")

    Path("outputs").mkdir(exist_ok=True)

    run_step(
        "Rodar fluxo bruto com OCR, extração estruturada, promoção e revisão",
        [sys.executable, "tools/run_raw_flow.py"],
    )

    review_return_code = run_optional_review_step(
        "Gerar pacote de revisão manual",
        [
            sys.executable,
            "tools/generate_manual_review_pack.py",
            REVIEW_JSON,
            MANUAL_REVIEW_PACK_JSON,
            MANUAL_REVIEW_PACK_REPORT,
        ],
    )

    pending_count = get_pending_review_count(MANUAL_REVIEW_PACK_JSON)

    if review_return_code != 0 or pending_count > 0:
        print("")
        print("Fluxo interrompido para revisão humana.")
        print(f"Campos pendentes: {pending_count}")
        print("")
        print("Revise os arquivos:")
        print(f"- {MANUAL_REVIEW_PACK_JSON}")
        print(f"- {MANUAL_REVIEW_PACK_REPORT}")
        print("")
        print("Depois de corrigir os campos pendentes, rode novamente o fluxo.")
        print_final_outputs(include_dec=False)
        sys.exit(1)

    clean_approved_dir()

    run_step(
        "Aprovar extrações promovidas para pasta segura",
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
        "Rodar pipeline canônico com extrações aprovadas",
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
    print("Fluxo MVP completo finalizado com sucesso.")
    print_final_outputs(include_dec=True)


if __name__ == "__main__":
    main()