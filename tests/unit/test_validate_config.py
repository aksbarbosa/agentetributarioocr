import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from validate_config import validate_config


def valid_config() -> dict:
    return {
        "project_name": "IRPF OCR DEC",
        "schema_version": "irpf-2026-v1",
        "exercicio": 2026,
        "ano_calendario": 2025,
        "tipo_declaracao": "AJUSTE_ANUAL",
        "modelo": "AUTO",
        "input_raw_dir": "inputs/raw",
        "input_extracted_dir": "inputs/extracted",
        "output_dir": "outputs",
        "output_json": "outputs/irpf-consolidado.json",
        "output_report": "outputs/irpf-consolidado.report.md",
        "fail_on_invalid_extraction": False,
        "fail_on_canonical_error": True,
        "enable_duplicate_detection": True,
        "enable_human_review_report": True,
    }


def test_valid_config():
    config = valid_config()
    result = validate_config(config)

    assert result["valid"] is True
    assert result["errors"] == []


def test_missing_required_field():
    config = valid_config()
    del config["project_name"]

    result = validate_config(config)

    assert result["valid"] is False

    error_fields = [error["field"] for error in result["errors"]]

    assert "project_name" in error_fields


def test_invalid_field_type():
    config = valid_config()
    config["exercicio"] = "2026"

    result = validate_config(config)

    assert result["valid"] is False

    error_fields = [error["field"] for error in result["errors"]]

    assert "exercicio" in error_fields


def test_invalid_modelo():
    config = valid_config()
    config["modelo"] = "MODELO_INEXISTENTE"

    result = validate_config(config)

    assert result["valid"] is False

    error_fields = [error["field"] for error in result["errors"]]

    assert "modelo" in error_fields


def test_exercicio_warning():
    config = valid_config()
    config["exercicio"] = 2027
    config["ano_calendario"] = 2025

    result = validate_config(config)

    assert result["valid"] is True

    warning_fields = [warning["field"] for warning in result["warnings"]]

    assert "exercicio" in warning_fields


def run_tests():
    test_valid_config()
    test_missing_required_field()
    test_invalid_field_type()
    test_invalid_modelo()
    test_exercicio_warning()
    print("test_validate_config.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()