import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_run_project_command():
    """
    Testa se o comando principal do projeto roda com sucesso.
    """
    result = subprocess.run(
        [sys.executable, "tools/run_project.py"],
        cwd=PROJECT_ROOT,
    )

    assert result.returncode == 0


def run_tests():
    test_run_project_command()
    print("test_run_project.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()
