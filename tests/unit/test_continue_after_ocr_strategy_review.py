import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from continue_after_ocr_strategy_review import (
    DEFAULT_CONFIG_PATH,
    CONTINUATION_COMMANDS,
    get_continuation_command,
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


def test_get_continuation_command_normal():
    command = get_continuation_command("normal")

    assert command is not None
    assert command[1] == "tools/continue_after_manual_review.py"


def test_get_continuation_command_best():
    command = get_continuation_command("best")

    assert command is not None
    assert command[1] == "tools/continue_after_best_manual_review.py"


def test_get_continuation_command_prepared_is_none():
    command = get_continuation_command("prepared")

    assert command is None


def test_parse_args_default():
    assert parse_args(["tools/continue_after_ocr_strategy_review.py"]) == DEFAULT_CONFIG_PATH


def test_parse_args_custom_path():
    assert (
        parse_args(
            [
                "tools/continue_after_ocr_strategy_review.py",
                "config/custom_ocr.json",
            ]
        )
        == "config/custom_ocr.json"
    )


def test_continuation_commands_are_expected():
    assert CONTINUATION_COMMANDS["normal"][1] == "tools/continue_after_manual_review.py"
    assert CONTINUATION_COMMANDS["best"][1] == "tools/continue_after_best_manual_review.py"


def run_tests():
    test_get_strategy_normal()
    test_get_strategy_prepared()
    test_get_strategy_best()
    test_get_strategy_invalid_fails()
    test_get_strategy_missing_fails()
    test_get_continuation_command_normal()
    test_get_continuation_command_best()
    test_get_continuation_command_prepared_is_none()
    test_parse_args_default()
    test_parse_args_custom_path()
    test_continuation_commands_are_expected()

    print("test_continue_after_ocr_strategy_review.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()