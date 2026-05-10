import sys
from pathlib import Path

from build_canonical_json import (
    load_json,
    save_json,
    build_canonical_json,
)

from validate_extracted import validate_extracted
from validate import validate_canonical_irpf
from report import generate_report, save_report


def build_output_paths(input_path: str) -> dict:
    """
    Cria os nomes dos arquivos de saída a partir do arquivo extraído.

    Exemplo:
    tests/fixtures/extracted/recibo_medico_exemplo.json

    Gera:
    recibo_medico_exemplo.canonical.json
    recibo_medico_exemplo.report.md
    """
    file_path = Path(input_path)
    stem = file_path.stem

    return {
        "canonical_json": f"{stem}.canonical.json",
        "report": f"{stem}.report.md"
    }


def run_pipeline_from_extracted(input_path: str) -> dict:
    """
    Executa o fluxo:

    extração simulada
        -> validação da extração
        -> JSON canônico
        -> validação do JSON canônico
        -> relatório
    """
    output_paths = build_output_paths(input_path)

    extracted = load_json(input_path)

    extraction_validation = validate_extracted(extracted)

    if not extraction_validation["valid"]:
        return {
            "input_path": input_path,
            "canonical_json": None,
            "report": None,
            "extraction_validation": extraction_validation,
            "canonical_validation": None
        }

    canonical = build_canonical_json(extracted)
    save_json(canonical, output_paths["canonical_json"])

    canonical_validation = validate_canonical_irpf(canonical)

    report = generate_report(canonical)
    save_report(report, output_paths["report"])

    return {
        "input_path": input_path,
        "canonical_json": output_paths["canonical_json"],
        "report": output_paths["report"],
        "extraction_validation": extraction_validation,
        "canonical_validation": canonical_validation
    }


def print_validation_block(title: str, result: dict | None) -> None:
    """
    Imprime um bloco de validação no terminal.
    """
    print("")
    print(title)

    if result is None:
        print("Não executado.")
        return

    if result["valid"]:
        print("Status: válido.")
    else:
        print("Status: inválido.")

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    if errors:
        print("\nErros:")
        for error in errors:
            print(f"- {error['field']}: {error['message']}")

    if warnings:
        print("\nAvisos:")
        for warning in warnings:
            print(f"- {warning['field']}: {warning['message']}")


def print_result(result: dict) -> None:
    """
    Mostra o resultado do pipeline no terminal.
    """
    print("Pipeline a partir da extração finalizado.")
    print(f"Entrada extraída: {result['input_path']}")

    print_validation_block(
        "Validação da extração:",
        result["extraction_validation"]
    )

    if result["canonical_json"] is None:
        print("")
        print("Pipeline interrompido: a extração está inválida.")
        return

    print("")
    print(f"JSON canônico: {result['canonical_json']}")
    print(f"Relatório: {result['report']}")

    print_validation_block(
        "Validação do JSON canônico:",
        result["canonical_validation"]
    )


def main() -> None:
    """
    Uso:
        python3 tools/pipeline_from_extracted.py tests/fixtures/extracted/informe_pj_exemplo.json

        python3 tools/pipeline_from_extracted.py tests/fixtures/extracted/recibo_medico_exemplo.json
    """
    if len(sys.argv) != 2:
        print("Uso:")
        print("python3 tools/pipeline_from_extracted.py tests/fixtures/extracted/informe_pj_exemplo.json")
        print("python3 tools/pipeline_from_extracted.py tests/fixtures/extracted/recibo_medico_exemplo.json")
        sys.exit(1)

    input_path = sys.argv[1]

    result = run_pipeline_from_extracted(input_path)
    print_result(result)

    extraction_valid = result["extraction_validation"]["valid"]
    canonical_valid = (
        result["canonical_validation"]["valid"]
        if result["canonical_validation"] is not None
        else False
    )

    if not extraction_valid or not canonical_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()