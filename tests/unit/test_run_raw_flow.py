import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import run_raw_flow as module


def test_run_step_success():
    module.run_step(
        "Comando de teste",
        [
            sys.executable,
            "-c",
            "print('ok')",
        ],
    )


def test_run_step_failure_exits():
    try:
        module.run_step(
            "Comando com falha",
            [
                sys.executable,
                "-c",
                "import sys; sys.exit(7)",
            ],
        )
    except SystemExit as exc:
        assert exc.code == 7
        return

    raise AssertionError("run_step não interrompeu em comando com falha.")


def test_run_step_allow_failure_does_not_exit():
    module.run_step(
        "Comando com falha permitida",
        [
            sys.executable,
            "-c",
            "import sys; sys.exit(3)",
        ],
        allow_failure=True,
    )


def test_validate_structured_extractions_missing_dir_does_not_fail():
    with tempfile.TemporaryDirectory() as tmp:
        missing_dir = Path(tmp) / "missing_structured_dir"

        module.validate_structured_extractions(str(missing_dir))


def test_validate_structured_extractions_empty_dir_does_not_fail():
    with tempfile.TemporaryDirectory() as tmp:
        empty_dir = Path(tmp) / "structured"
        empty_dir.mkdir(parents=True, exist_ok=True)

        module.validate_structured_extractions(str(empty_dir))


def test_run_raw_flow_script_compiles():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "tools/run_raw_flow.py",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""


def run_tests():
    test_run_step_success()
    test_run_step_failure_exits()
    test_run_step_allow_failure_does_not_exit()
    test_validate_structured_extractions_missing_dir_does_not_fail()
    test_validate_structured_extractions_empty_dir_does_not_fail()
    test_run_raw_flow_script_compiles()

    print("test_run_raw_flow.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()