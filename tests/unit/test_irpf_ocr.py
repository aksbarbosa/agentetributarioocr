import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from irpf_ocr import COMMANDS, parse_args


def test_commands_include_main_interface():
    assert "setup" in COMMANDS
    assert "status" in COMMANDS
    assert "project-status" in COMMANDS
    assert "run" in COMMANDS
    assert "review" in COMMANDS
    assert "continue" in COMMANDS
    assert "check" in COMMANDS


def test_setup_command_points_to_setup_project():
    command = COMMANDS["setup"]["command"]

    assert command[1] == "tools/setup_project.py"


def test_status_command_points_to_ocr_strategy_status():
    command = COMMANDS["status"]["command"]

    assert command[1] == "tools/ocr_strategy_status.py"


def test_project_status_command_points_to_project_status():
    command = COMMANDS["project-status"]["command"]

    assert command[1] == "tools/project_status.py"


def test_run_command_points_to_run_ocr_strategy():
    command = COMMANDS["run"]["command"]

    assert command[1] == "tools/run_ocr_strategy.py"


def test_review_command_points_to_strategy_review_pack():
    command = COMMANDS["review"]["command"]

    assert command[1] == "tools/review_ocr_strategy_pack.py"


def test_continue_command_points_to_strategy_continuation():
    command = COMMANDS["continue"]["command"]

    assert command[1] == "tools/continue_after_ocr_strategy_review.py"


def test_check_command_points_to_dev_check():
    command = COMMANDS["check"]["command"]

    assert command[1] == "tools/dev_check.py"


def test_parse_args_setup():
    assert parse_args(["tools/irpf_ocr.py", "setup"]) == "setup"


def test_parse_args_status():
    assert parse_args(["tools/irpf_ocr.py", "status"]) == "status"


def test_parse_args_project_status():
    assert parse_args(["tools/irpf_ocr.py", "project-status"]) == "project-status"


def test_parse_args_run():
    assert parse_args(["tools/irpf_ocr.py", "run"]) == "run"


def test_parse_args_review():
    assert parse_args(["tools/irpf_ocr.py", "review"]) == "review"


def test_parse_args_continue():
    assert parse_args(["tools/irpf_ocr.py", "continue"]) == "continue"


def test_parse_args_check():
    assert parse_args(["tools/irpf_ocr.py", "check"]) == "check"


def test_parse_args_unknown_command_fails():
    try:
        parse_args(["tools/irpf_ocr.py", "comando-invalido"])
    except SystemExit as exc:
        assert exc.code == 1
        return

    raise AssertionError("Comando inválido foi aceito.")


def test_parse_args_help_exits_zero():
    try:
        parse_args(["tools/irpf_ocr.py", "help"])
    except SystemExit as exc:
        assert exc.code == 0
        return

    raise AssertionError("Help não encerrou com código 0.")


def test_parse_args_help_short_exits_zero():
    try:
        parse_args(["tools/irpf_ocr.py", "-h"])
    except SystemExit as exc:
        assert exc.code == 0
        return

    raise AssertionError("-h não encerrou com código 0.")


def test_parse_args_help_long_exits_zero():
    try:
        parse_args(["tools/irpf_ocr.py", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
        return

    raise AssertionError("--help não encerrou com código 0.")


def test_parse_args_without_command_fails():
    try:
        parse_args(["tools/irpf_ocr.py"])
    except SystemExit as exc:
        assert exc.code == 1
        return

    raise AssertionError("Chamada sem comando foi aceita.")


def test_parse_args_with_too_many_args_fails():
    try:
        parse_args(["tools/irpf_ocr.py", "status", "extra"])
    except SystemExit as exc:
        assert exc.code == 1
        return

    raise AssertionError("Chamada com argumentos extras foi aceita.")


def run_tests():
    test_commands_include_main_interface()
    test_setup_command_points_to_setup_project()
    test_status_command_points_to_ocr_strategy_status()
    test_project_status_command_points_to_project_status()
    test_run_command_points_to_run_ocr_strategy()
    test_review_command_points_to_strategy_review_pack()
    test_continue_command_points_to_strategy_continuation()
    test_check_command_points_to_dev_check()
    test_parse_args_setup()
    test_parse_args_status()
    test_parse_args_project_status()
    test_parse_args_run()
    test_parse_args_review()
    test_parse_args_continue()
    test_parse_args_check()
    test_parse_args_unknown_command_fails()
    test_parse_args_help_exits_zero()
    test_parse_args_help_short_exits_zero()
    test_parse_args_help_long_exits_zero()
    test_parse_args_without_command_fails()
    test_parse_args_with_too_many_args_fails()

    print("test_irpf_ocr.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()