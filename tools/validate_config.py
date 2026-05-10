import json
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "project_name": str,
    "schema_version": str,
    "exercicio": int,
    "ano_calendario": int,
    "tipo_declaracao": str,
    "modelo": str,
    "input_raw_dir": str,
    "input_extracted_dir": str,
    "output_dir": str,
    "output_json": str,
    "output_report": str,
    "fail_on_invalid_extraction": bool,
    "fail_on_canonical_error": bool,
    "enable_duplicate_detection": bool,
    "enable_human_review_report": bool,
}


VALID_TIPO_DECLARACAO = {"AJUSTE_ANUAL"}
VALID_MODELO = {"AUTO", "SIMPLIFICADA", "COMPLETA"}


def load_config(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_config(config: dict) -> dict:
    errors = []
    warnings = []

    for field_name, expected_type in REQUIRED_FIELDS.items():
        if field_name not in config:
            errors.append({
                "field": field_name,
                "message": "Campo obrigatório ausente."
            })
            continue

        value = config[field_name]

        if not isinstance(value, expected_type):
            errors.append({
                "field": field_name,
                "message": f"Tipo inválido. Esperado: {expected_type.__name__}."
            })

    tipo_declaracao = config.get("tipo_declaracao")
    if tipo_declaracao and tipo_declaracao not in VALID_TIPO_DECLARACAO:
        errors.append({
            "field": "tipo_declaracao",
            "message": "Tipo de declaração não suportado."
        })

    modelo = config.get("modelo")
    if modelo and modelo not in VALID_MODELO:
        errors.append({
            "field": "modelo",
            "message": "Modelo de declaração não suportado."
        })

    exercicio = config.get("exercicio")
    ano_calendario = config.get("ano_calendario")

    if isinstance(exercicio, int) and isinstance(ano_calendario, int):
        if exercicio != ano_calendario + 1:
            warnings.append({
                "field": "exercicio",
                "message": "Normalmente o exercício é o ano-calendário + 1. Verifique."
            })

    input_extracted_dir = config.get("input_extracted_dir")
    if isinstance(input_extracted_dir, str):
        path = Path(input_extracted_dir)
        if not path.exists():
            errors.append({
                "field": "input_extracted_dir",
                "message": "Pasta de extrações não existe."
            })
        elif not path.is_dir():
            errors.append({
                "field": "input_extracted_dir",
                "message": "input_extracted_dir deve apontar para uma pasta."
            })

    output_json = config.get("output_json")
    output_report = config.get("output_report")

    if isinstance(output_json, str) and not output_json.endswith(".json"):
        warnings.append({
            "field": "output_json",
            "message": "O arquivo de saída JSON normalmente deve terminar com .json."
        })

    if isinstance(output_report, str) and not output_report.endswith(".md"):
        warnings.append({
            "field": "output_report",
            "message": "O relatório normalmente deve terminar com .md."
        })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def print_validation_result(result: dict) -> None:
    if result["valid"]:
        print("Configuração válida.")
    else:
        print("Configuração inválida.")

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    if errors:
        print("")
        print("Erros:")
        for error in errors:
            print(f"- {error['field']}: {error['message']}")

    if warnings:
        print("")
        print("Avisos:")
        for warning in warnings:
            print(f"- {warning['field']}: {warning['message']}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso:")
        print("python3 tools/validate_config.py config/project_config.json")
        sys.exit(1)

    config_path = sys.argv[1]

    config = load_config(config_path)
    result = validate_config(config)

    print_validation_result(result)

    if not result["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()