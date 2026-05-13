import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from clean_outputs import OUTPUT_FILES, clean_outputs, remove_file


def test_remove_file_existing_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "arquivo.txt"
        path.write_text("conteudo", encoding="utf-8")

        removed = remove_file(str(path))

        assert removed is True
        assert not path.exists()


def test_remove_file_missing_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "arquivo-inexistente.txt"

        removed = remove_file(str(path))

        assert removed is False


def test_remove_file_directory_is_not_removed():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "pasta"
        path.mkdir()

        removed = remove_file(str(path))

        assert removed is False
        assert path.exists()
        assert path.is_dir()


def test_output_files_contains_known_outputs():
    expected_outputs = [
        "outputs/irpf-consolidado.json",
        "outputs/irpf-consolidado.report.md",
        "outputs/agent-decision.json",
        "outputs/agent-decisions.json",
        "outputs/agent-decisions.report.md",
        "outputs/preflight-documents.json",
        "outputs/preflight-documents.report.md",
        "outputs/raw-inputs-manifest.json",
        "outputs/raw-inputs-manifest.report.md",
    ]

    for output_file in expected_outputs:
        assert output_file in OUTPUT_FILES


def test_clean_outputs_removes_known_outputs_from_project_root():
    created_files = []

    try:
        for output_file in OUTPUT_FILES:
            path = PROJECT_ROOT / output_file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("arquivo temporario de teste", encoding="utf-8")
            created_files.append(path)

        removed_files = clean_outputs()

        for output_file in OUTPUT_FILES:
            assert output_file in removed_files
            assert not (PROJECT_ROOT / output_file).exists()

    finally:
        for path in created_files:
            if path.exists() and path.is_file():
                path.unlink()


def run_tests():
    test_remove_file_existing_file()
    test_remove_file_missing_file()
    test_remove_file_directory_is_not_removed()
    test_output_files_contains_known_outputs()
    test_clean_outputs_removes_known_outputs_from_project_root()
    print("test_clean_outputs.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()