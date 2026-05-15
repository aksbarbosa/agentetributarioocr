import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from ocr_strategy_status import (
    DEFAULT_CONFIG_PATH,
    STRATEGY_COMMANDS,
    load_json,
    parse_args,
)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_load_json_existing_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ocr_config.json"

        write_json(
            path,
            {
                "ocr_strategy": "best",
                "preprocessing": {
                    "enabled": True,
                },
            },
        )

        data = load_json(str(path))

        assert data["ocr_strategy"] == "best"
        assert data["preprocessing"]["enabled"] is True


def test_load_json_missing_file_fails():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "missing.json"

        try:
            load_json(str(path))
        except FileNotFoundError as exc:
            assert "Arquivo não encontrado" in str(exc)
            return

        raise AssertionError("Arquivo inexistente foi aceito.")


def test_parse_args_default():
    assert parse_args(["tools/ocr_strategy_status.py"]) == DEFAULT_CONFIG_PATH


def test_parse_args_custom_path():
    assert (
        parse_args(["tools/ocr_strategy_status.py", "config/custom_ocr.json"])
        == "config/custom_ocr.json"
    )


def test_strategy_commands():
    assert STRATEGY_COMMANDS["normal"] == "python3 tools/run_mvp_flow.py"
    assert STRATEGY_COMMANDS["prepared"] == "python3 tools/run_prepared_raw_flow.py"
    assert STRATEGY_COMMANDS["best"] == "python3 tools/run_best_mvp_flow.py"


def run_tests():
    test_load_json_existing_file()
    test_load_json_missing_file_fails()
    test_parse_args_default()
    test_parse_args_custom_path()
    test_strategy_commands()

    print("test_ocr_strategy_status.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()