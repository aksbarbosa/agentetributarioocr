import sys
from pathlib import Path
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import clean_outputs


def test_clean_outputs_removes_known_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        outputs_dir = temp_path / "outputs"
        outputs_dir.mkdir()

        json_file = outputs_dir / "irpf-consolidado.json"
        report_file = outputs_dir / "irpf-consolidado.report.md"
        other_file = outputs_dir / "nao_remover.txt"

        json_file.write_text("{}", encoding="utf-8")
        report_file.write_text("# relatório", encoding="utf-8")
        other_file.write_text("preservar", encoding="utf-8")

        original_outputs_dir = clean_outputs.OUTPUTS_DIR

        try:
            clean_outputs.OUTPUTS_DIR = outputs_dir

            removed = clean_outputs.clean_outputs()

            removed_names = sorted(path.name for path in removed)

            assert removed_names == [
                "irpf-consolidado.json",
                "irpf-consolidado.report.md",
            ]

            assert not json_file.exists()
            assert not report_file.exists()
            assert other_file.exists()

        finally:
            clean_outputs.OUTPUTS_DIR = original_outputs_dir


def run_tests():
    test_clean_outputs_removes_known_files()
    print("test_clean_outputs.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()