import json
import sys
from pathlib import Path

from validate import validate_canonical_irpf


def load_json(path: str) -> dict:
    """
    Carrega um arquivo JSON e retorna um dicionário Python.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def print_validation_result(result: dict) -> None:
    """
    Mostra o resultado da validação de forma legível.
    """
    if result["valid"]:
        print("JSON válido.")
    else:
        print("JSON inválido.")

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


def main() -> None:
    """
    Uso:
        python3 tools/check_json.py tests/fixtures/assalariado_simples.json
    """
    if len(sys.argv) != 2:
        print("Uso:")
        print("python3 tools/check_json.py tests/fixtures/assalariado_simples.json")
        sys.exit(1)

    path = sys.argv[1]
    data = load_json(path)
    result = validate_canonical_irpf(data)
    print_validation_result(result)

    if not result["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()