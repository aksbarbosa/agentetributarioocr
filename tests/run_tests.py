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
    "tests/unit/test_scan_raw_inputs.py",
    "tests/unit/test_extract_text.py",
    "tests/unit/test_run_project.py",
    "tests/unit/test_classify_document.py",
    "tests/unit/test_agent_simulator.py",
    "tests/unit/test_agent_batch_simulator.py",
    "tests/unit/test_preflight_documents.py",
    "tests/unit/test_extract_structured_from_text.py",
    "tests/unit/test_review_promoted_extractions.py",
    "tests/unit/test_generate_manual_review_pack.py",
    "tests/unit/test_apply_manual_review_pack.py",
    "tests/unit/test_generate_manual_review_pack.py",
    "tests/unit/test_continue_after_manual_review.py",
    "tests/unit/test_run_raw_flow.py",
    "tests/unit/test_extract_structured_batch.py",
    "tests/unit/test_promote_structured_extractions.py",
    "tests/unit/test_export_dec_experimental.py",
    "tests/unit/test_project_status.py",
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
