import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import project_status as module


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def patch_paths(base_dir: Path):
    original_paths = module.PATHS.copy()

    module.PATHS = {
        "review_json": base_dir / "outputs" / "review-promoted-extractions.json",
        "manual_pack": base_dir / "outputs" / "manual-review-pack.json",
        "approved_dir": base_dir / "outputs" / "approved_test",
        "canonical_json": base_dir / "outputs" / "irpf-consolidado.json",
        "canonical_report": base_dir / "outputs" / "irpf-consolidado.report.md",
        "dec_export": base_dir / "outputs" / "irpf-export-dec-experimental.txt",
        "dec_report": base_dir / "outputs" / "irpf-export-dec-experimental.report.md",
    }

    return original_paths


def test_detect_status_initial_state():
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        original_paths = patch_paths(base_dir)

        try:
            status, next_step = module.detect_status()

            assert status == "fluxo ainda não iniciado ou outputs limpos"
            assert "run_mvp_flow.py" in next_step

        finally:
            module.PATHS = original_paths


def test_detect_status_waiting_manual_review():
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        original_paths = patch_paths(base_dir)

        try:
            write_json(
                module.PATHS["manual_pack"],
                {
                    "summary": {
                        "pending_field_count": 3,
                    }
                },
            )

            status, next_step = module.detect_status()

            assert status == "aguardando revisão manual"
            assert "continue_after_manual_review.py" in next_step

        finally:
            module.PATHS = original_paths


def test_detect_status_manual_review_without_pending_and_no_approved_files():
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        original_paths = patch_paths(base_dir)

        try:
            write_json(
                module.PATHS["manual_pack"],
                {
                    "summary": {
                        "pending_field_count": 0,
                    }
                },
            )

            status, next_step = module.detect_status()

            assert status == "revisão manual sem pendências, aguardando continuação"
            assert "continue_after_manual_review.py" in next_step

        finally:
            module.PATHS = original_paths


def test_detect_status_approved_waiting_canonical():
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        original_paths = patch_paths(base_dir)

        try:
            module.PATHS["approved_dir"].mkdir(parents=True, exist_ok=True)
            write_json(module.PATHS["approved_dir"] / "recibo.json", {"document_type": "recibo_medico"})

            status, next_step = module.detect_status()

            assert status == "extrações aprovadas, aguardando JSON canônico"
            assert "run_project.py outputs/approved_test" in next_step

        finally:
            module.PATHS = original_paths


def test_detect_status_canonical_waiting_export():
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        original_paths = patch_paths(base_dir)

        try:
            write_json(module.PATHS["canonical_json"], {"declarante": {}})

            status, next_step = module.detect_status()

            assert status == "JSON canônico gerado, aguardando exportação experimental"
            assert "export_dec_experimental.py" in next_step

        finally:
            module.PATHS = original_paths


def test_detect_status_completed_flow():
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        original_paths = patch_paths(base_dir)

        try:
            write_json(module.PATHS["canonical_json"], {"declarante": {}})
            module.PATHS["dec_export"].parent.mkdir(parents=True, exist_ok=True)
            module.PATHS["dec_export"].write_text("export experimental", encoding="utf-8")

            status, next_step = module.detect_status()

            assert status == "fluxo completo finalizado"
            assert "irpf-consolidado.report.md" in next_step

        finally:
            module.PATHS = original_paths


def run_tests():
    test_detect_status_initial_state()
    test_detect_status_waiting_manual_review()
    test_detect_status_manual_review_without_pending_and_no_approved_files()
    test_detect_status_approved_waiting_canonical()
    test_detect_status_canonical_waiting_export()
    test_detect_status_completed_flow()

    print("test_project_status.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()