import json
import sys
from pathlib import Path

from validate import validate_canonical_irpf
from report import generate_report, save_report


def load_json(path: str) -> dict:
    """
    Carrega um arquivo JSON.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_output_report_path(input_path: str) -> str:
    """
    Cria o nome do relatório a partir do JSON de entrada.

    Exemplo:
    tests/fixtures/assalariado_simples.json
    vira:
    assalariado_simples.report.md
    """
    file_path = Path(input_path)
    return f"{file_path.stem}.report.md"


def run_pipeline(input_path: str, output_report_path: str | None = None) -> dict:
    """
    Executa o pipeline atual:

    JSON canônico -> validação -> relatório Markdown
    """
    data = load_json(input_path)

    validation_result = validate_canonical_irpf(data)

    report = generate_report(data)

    if output_report_path is None:
        output_report_path = build_output_report_path(input_path)

    save_report(report, output_report_path)

    return {
        "input_path": input_path,
        "output_report_path": output_report_path,
        "validation": validation_result
    }


def print_pipeline_result(result: dict) -> None:
    """
    Mostra o resultado do pipeline no terminal.
    """
    print("Pipeline finalizado.")
    print(f"Entrada: {result['input_path']}")
    print(f"Relatório: {result['output_report_path']}")

    validation = result["validation"]

    if validation["valid"]:
        print("Status: JSON válido.")
    else:
        print("Status: JSON inválido.")

    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])

    if errors:
        print("\nErros:")
        for error in errors:
            print(f"- {error['field']}: {error['message']}")

    if warnings:
        print("\nAvisos:")
        for warning in warnings:
            print(f"- {warning['field']}: {warning['message']}")


def main() -> None:
    """
    Uso:
        python3 tools/pipeline.py tests/fixtures/assalariado_simples.json

    Ou escolhendo o nome do relatório:
        python3 tools/pipeline.py tests/fixtures/assalariado_simples.json irpf-2026.report.md
    """
    if len(sys.argv) not in [2, 3]:
        print("Uso:")
        print("python3 tools/pipeline.py tests/fixtures/assalariado_simples.json")
        print("ou")
        print("python3 tools/pipeline.py tests/fixtures/assalariado_simples.json irpf-2026.report.md")
        sys.exit(1)

    input_path = sys.argv[1]

    output_report_path = None
    if len(sys.argv) == 3:
        output_report_path = sys.argv[2]

    result = run_pipeline(input_path, output_report_path)
    print_pipeline_result(result)

    if not result["validation"]["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()