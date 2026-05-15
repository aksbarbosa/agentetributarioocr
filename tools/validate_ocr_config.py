import json
import sys
from pathlib import Path


DEFAULT_CONFIG_PATH = "config/ocr_config.json"

VALID_OCR_STRATEGIES = {
    "normal",
    "prepared",
    "best",
}

VALID_SELECTION_METHODS = {
    "longest_text",
}


REQUIRED_PATH_KEYS = {
    "raw_input_dir",
    "prepared_input_dir",
    "extracted_text_dir",
    "extracted_text_prepared_dir",
    "extracted_text_best_dir",
}


REQUIRED_PREPROCESSING_KEYS = {
    "enabled",
    "scale_factor",
    "contrast_factor",
    "sharpness_factor",
    "binarization_threshold",
}


REQUIRED_SELECTION_KEYS = {
    "method",
    "prefer_original_on_tie",
}


REQUIRED_SAFETY_KEYS = {
    "allow_partial_preprocessing_errors",
    "allow_preflight_failure",
    "require_manual_review_for_invalid_identifiers",
}


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def require_section(config: dict, section: str) -> dict:
    value = config.get(section)

    if not isinstance(value, dict):
        raise ValueError(f"Seção obrigatória ausente ou inválida: {section}")

    return value


def validate_required_keys(section_name: str, section: dict, required_keys: set[str]) -> None:
    missing = sorted(required_keys - set(section.keys()))

    if missing:
        raise ValueError(
            f"Chaves ausentes em {section_name}: {', '.join(missing)}"
        )


def validate_ocr_strategy(config: dict) -> None:
    strategy = config.get("ocr_strategy")

    if strategy not in VALID_OCR_STRATEGIES:
        raise ValueError(
            f"ocr_strategy inválida: {strategy}. "
            f"Valores aceitos: {', '.join(sorted(VALID_OCR_STRATEGIES))}"
        )


def validate_paths(paths: dict) -> None:
    validate_required_keys("paths", paths, REQUIRED_PATH_KEYS)

    for key, value in paths.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"paths.{key} deve ser uma string não vazia.")


def validate_preprocessing(preprocessing: dict) -> None:
    validate_required_keys(
        "preprocessing",
        preprocessing,
        REQUIRED_PREPROCESSING_KEYS,
    )

    if not isinstance(preprocessing["enabled"], bool):
        raise ValueError("preprocessing.enabled deve ser booleano.")

    if not isinstance(preprocessing["scale_factor"], int):
        raise ValueError("preprocessing.scale_factor deve ser inteiro.")

    if preprocessing["scale_factor"] < 1:
        raise ValueError("preprocessing.scale_factor deve ser >= 1.")

    for key in ["contrast_factor", "sharpness_factor"]:
        if not isinstance(preprocessing[key], (int, float)):
            raise ValueError(f"preprocessing.{key} deve ser numérico.")

        if preprocessing[key] <= 0:
            raise ValueError(f"preprocessing.{key} deve ser > 0.")

    threshold = preprocessing["binarization_threshold"]

    if not isinstance(threshold, int):
        raise ValueError("preprocessing.binarization_threshold deve ser inteiro.")

    if threshold < 0 or threshold > 255:
        raise ValueError("preprocessing.binarization_threshold deve estar entre 0 e 255.")


def validate_selection(selection: dict) -> None:
    validate_required_keys("selection", selection, REQUIRED_SELECTION_KEYS)

    method = selection["method"]

    if method not in VALID_SELECTION_METHODS:
        raise ValueError(
            f"selection.method inválido: {method}. "
            f"Valores aceitos: {', '.join(sorted(VALID_SELECTION_METHODS))}"
        )

    if not isinstance(selection["prefer_original_on_tie"], bool):
        raise ValueError("selection.prefer_original_on_tie deve ser booleano.")


def validate_safety(safety: dict) -> None:
    validate_required_keys("safety", safety, REQUIRED_SAFETY_KEYS)

    for key in REQUIRED_SAFETY_KEYS:
        if not isinstance(safety[key], bool):
            raise ValueError(f"safety.{key} deve ser booleano.")


def validate_ocr_config(config: dict) -> None:
    validate_ocr_strategy(config)

    paths = require_section(config, "paths")
    preprocessing = require_section(config, "preprocessing")
    selection = require_section(config, "selection")
    safety = require_section(config, "safety")

    validate_paths(paths)
    validate_preprocessing(preprocessing)
    validate_selection(selection)
    validate_safety(safety)


def parse_args(argv: list[str]) -> str:
    if len(argv) == 1:
        return DEFAULT_CONFIG_PATH

    if len(argv) == 2:
        return argv[1]

    print("Uso:")
    print("python3 tools/validate_ocr_config.py")
    print("python3 tools/validate_ocr_config.py config/ocr_config.json")
    sys.exit(1)


def main() -> None:
    config_path = parse_args(sys.argv)

    config = load_json(config_path)
    validate_ocr_config(config)

    print("Configuração OCR válida.")
    print(f"Arquivo: {config_path}")
    print(f"Estratégia OCR: {config['ocr_strategy']}")


if __name__ == "__main__":
    main()
