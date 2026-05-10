import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


TEST_FILES = [
    "tests/unit/test_normalize.py",
    "tests/unit/test_validate.py",
    "tests/unit/test_validate_config.py",
    "tests/unit/test_validate_extracted.py",
    "tests/unit/test_build_canonical_json.py",
    "tests/unit/test_pipeline_batch.py",
    "tests/unit/test_report.py",
    "tests/unit/test_clean_outputs.py",
    "tests/unit/test_run_project.py",
    "tests/unit/test_classify_document.py",
    "tests/unit/test_agent_simulator.py",
]


def run_test_file(path: str) -> bool:
    """
    Executa um arquivo de teste individual.

    Retorna True se o teste passou.
    Retorna False se o teste falhou.
    """
    print(f"Rodando {path}...")

    result = subprocess.run(
        [sys.executable, path],
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0


def main() -> None:
    """
    Executa todos os testes unitários do projeto.

    Uso:
        python3 tests/run_tests.py
    """
    all_ok = True

    for test_file in TEST_FILES:
        ok = run_test_file(test_file)

        if not ok:
            all_ok = False
            print(f"Falhou: {test_file}")
        else:
            print(f"OK: {test_file}")

        print("")

    if not all_ok:
        print("Alguns testes falharam.")
        sys.exit(1)

    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()
