import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from run_ocr_strategy import (
    DEFAULT_CONFIG_PATH,
    STRATEGY_COMMANDS,
    get_strategy,
    parse_args,
)


def test_get_strategy_normal():
    config = {"ocr_strategy": "normal"}

    assert get_strategy(config) == "normal"


def test_get_strategy_prepared():
    config = {"ocr_strategy": "prepared"}

    assert get_strategy(config) == "prepared"


def test_get_strategy_best():
    config = {"ocr_strategy": "best"}

    assert get_strategy(config) == "best"


def test_get_strategy_invalid_fails():
    config = {"ocr_strategy": "invalida"}

    try:
        get_strategy(config)
    except ValueError as exc:
        assert "ocr_strategy inválida" in str(exc)
        return

    raise AssertionError("Estratégia inválida foi aceita.")


def test_get_strategy_missing_fails():
    config = {}

    try:
        get_strategy(config)
    except ValueError as exc:
        assert "ocr_strategy inválida" in str(exc)
        return

    raise AssertionError("Configuração sem estratégia foi aceita.")


def test_parse_args_default():
    assert parse_args(["tools/run_ocr_strategy.py"]) == DEFAULT_CONFIG_PATH


def test_parse_args_custom_path():
    assert (
        parse_args(["tools/run_ocr_strategy.py", "config/custom_ocr.json"])
        == "config/custom_ocr.json"
    )


def test_strategy_commands_map_to_expected_scripts():
    assert STRATEGY_COMMANDS["normal"][1] == "tools/run_mvp_flow.py"
    assert STRATEGY_COMMANDS["prepared"][1] == "tools/run_prepared_raw_flow.py"
    assert STRATEGY_COMMANDS["best"][1] == "tools/run_best_mvp_flow.py"


def run_tests():
    test_get_strategy_normal()
    test_get_strategy_prepared()
    test_get_strategy_best()
    test_get_strategy_invalid_fails()
    test_get_strategy_missing_fails()
    test_parse_args_default()
    test_parse_args_custom_path()
    test_strategy_commands_map_to_expected_scripts()

    print("test_run_ocr_strategy.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()