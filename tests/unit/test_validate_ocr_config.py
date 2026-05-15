import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from validate_ocr_config import validate_ocr_config


def make_valid_config():
    return {
        "ocr_strategy": "best",
        "paths": {
            "raw_input_dir": "inputs/raw",
            "prepared_input_dir": "outputs/raw_prepared_for_ocr",
            "extracted_text_dir": "outputs/extracted_text",
            "extracted_text_prepared_dir": "outputs/extracted_text_prepared",
            "extracted_text_best_dir": "outputs/extracted_text_best",
        },
        "preprocessing": {
            "enabled": True,
            "scale_factor": 2,
            "contrast_factor": 1.8,
            "sharpness_factor": 1.5,
            "binarization_threshold": 180,
        },
        "selection": {
            "method": "longest_text",
            "prefer_original_on_tie": True,
        },
        "safety": {
            "allow_partial_preprocessing_errors": True,
            "allow_preflight_failure": True,
            "require_manual_review_for_invalid_identifiers": True,
        },
    }


def assert_invalid(config: dict, expected_message: str) -> None:
    try:
        validate_ocr_config(config)
    except ValueError as exc:
        assert expected_message in str(exc)
        return

    raise AssertionError("Configuração inválida foi aceita.")


def test_valid_config_passes():
    config = make_valid_config()

    validate_ocr_config(config)


def test_invalid_ocr_strategy_fails():
    config = make_valid_config()
    config["ocr_strategy"] = "invalida"

    assert_invalid(config, "ocr_strategy inválida")


def test_missing_paths_section_fails():
    config = make_valid_config()
    del config["paths"]

    assert_invalid(config, "Seção obrigatória ausente")


def test_missing_required_path_key_fails():
    config = make_valid_config()
    del config["paths"]["raw_input_dir"]

    assert_invalid(config, "Chaves ausentes em paths")


def test_empty_path_fails():
    config = make_valid_config()
    config["paths"]["raw_input_dir"] = ""

    assert_invalid(config, "deve ser uma string não vazia")


def test_invalid_scale_factor_fails():
    config = make_valid_config()
    config["preprocessing"]["scale_factor"] = 0

    assert_invalid(config, "scale_factor deve ser >= 1")


def test_invalid_binarization_threshold_fails():
    config = make_valid_config()
    config["preprocessing"]["binarization_threshold"] = 300

    assert_invalid(config, "binarization_threshold deve estar entre 0 e 255")


def test_invalid_selection_method_fails():
    config = make_valid_config()
    config["selection"]["method"] = "random"

    assert_invalid(config, "selection.method inválido")


def test_invalid_safety_boolean_fails():
    config = make_valid_config()
    config["safety"]["allow_preflight_failure"] = "sim"

    assert_invalid(config, "safety.allow_preflight_failure deve ser booleano")


def run_tests():
    test_valid_config_passes()
    test_invalid_ocr_strategy_fails()
    test_missing_paths_section_fails()
    test_missing_required_path_key_fails()
    test_empty_path_fails()
    test_invalid_scale_factor_fails()
    test_invalid_binarization_threshold_fails()
    test_invalid_selection_method_fails()
    test_invalid_safety_boolean_fails()

    print("test_validate_ocr_config.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()