import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from review_ocr_strategy_pack import (
    DEFAULT_CONFIG_PATH,
    PACK_BY_STRATEGY,
    get_pack_path,
    get_strategy,
    parse_args,
)


def test_get_strategy_normal():
    assert get_strategy({"ocr_strategy": "normal"}) == "normal"


def test_get_strategy_prepared():
    assert get_strategy({"ocr_strategy": "prepared"}) == "prepared"


def test_get_strategy_best():
    assert get_strategy({"ocr_strategy": "best"}) == "best"


def test_get_strategy_invalid_fails():
    try:
        get_strategy({"ocr_strategy": "invalida"})
    except ValueError as exc:
        assert "ocr_strategy inválida" in str(exc)
        return

    raise AssertionError("Estratégia inválida foi aceita.")


def test_get_strategy_missing_fails():
    try:
        get_strategy({})
    except ValueError as exc:
        assert "ocr_strategy inválida" in str(exc)
        return

    raise AssertionError("Estratégia ausente foi aceita.")


def test_get_pack_path_normal():
    assert get_pack_path("normal") == "outputs/manual-review-pack.json"


def test_get_pack_path_best():
    assert get_pack_path("best") == "outputs/manual-review-pack-best.json"


def test_get_pack_path_prepared_is_none():
    assert get_pack_path("prepared") is None


def test_pack_by_strategy_expected_values():
    assert PACK_BY_STRATEGY["normal"] == "outputs/manual-review-pack.json"
    assert PACK_BY_STRATEGY["best"] == "outputs/manual-review-pack-best.json"


def test_parse_args_default():
    assert parse_args(["tools/review_ocr_strategy_pack.py"]) == DEFAULT_CONFIG_PATH


def test_parse_args_custom_path():
    assert (
        parse_args(["tools/review_ocr_strategy_pack.py", "config/custom_ocr.json"])
        == "config/custom_ocr.json"
    )


def test_parse_args_too_many_fails():
    try:
        parse_args(["tools/review_ocr_strategy_pack.py", "a", "b"])
    except SystemExit as exc:
        assert exc.code == 1
        return

    raise AssertionError("parse_args aceitou argumentos demais.")


def run_tests():
    test_get_strategy_normal()
    test_get_strategy_prepared()
    test_get_strategy_best()
    test_get_strategy_invalid_fails()
    test_get_strategy_missing_fails()
    test_get_pack_path_normal()
    test_get_pack_path_best()
    test_get_pack_path_prepared_is_none()
    test_pack_by_strategy_expected_values()
    test_parse_args_default()
    test_parse_args_custom_path()
    test_parse_args_too_many_fails()

    print("test_review_ocr_strategy_pack.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()