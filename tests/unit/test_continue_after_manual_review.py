import json
import shutil
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import continue_after_manual_review as module


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_load_json_existing_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "data.json"

        write_json(
            path,
            {
                "summary": {
                    "pending_field_count": 3,
                }
            },
        )

        data = module.load_json(str(path))

        assert data["summary"]["pending_field_count"] == 3


def test_load_json_missing_file_returns_empty_dict():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "missing.json"

        data = module.load_json(str(path))

        assert data == {}


def test_get_pending_review_count_from_pack():
    with tempfile.TemporaryDirectory() as tmp:
        original_pack_path = module.MANUAL_REVIEW_PACK_JSON

        try:
            pack_path = Path(tmp) / "manual-review-pack.json"
            module.MANUAL_REVIEW_PACK_JSON = str(pack_path)

            write_json(
                pack_path,
                {
                    "summary": {
                        "pending_field_count": 8,
                    }
                },
            )

            assert module.get_pending_review_count() == 8

        finally:
            module.MANUAL_REVIEW_PACK_JSON = original_pack_path


def test_get_pending_review_count_missing_pack_returns_zero():
    with tempfile.TemporaryDirectory() as tmp:
        original_pack_path = module.MANUAL_REVIEW_PACK_JSON

        try:
            pack_path = Path(tmp) / "missing-manual-review-pack.json"
            module.MANUAL_REVIEW_PACK_JSON = str(pack_path)

            assert module.get_pending_review_count() == 0

        finally:
            module.MANUAL_REVIEW_PACK_JSON = original_pack_path


def test_clean_approved_dir_removes_old_files_and_recreates_dir():
    with tempfile.TemporaryDirectory() as tmp:
        original_approved_dir = module.APPROVED_DIR

        try:
            approved_dir = Path(tmp) / "approved_test"
            approved_dir.mkdir(parents=True, exist_ok=True)

            old_file = approved_dir / "old.json"
            old_file.write_text("{}", encoding="utf-8")

            module.APPROVED_DIR = approved_dir

            module.clean_approved_dir()

            assert approved_dir.exists()
            assert approved_dir.is_dir()
            assert not old_file.exists()
            assert list(approved_dir.iterdir()) == []

        finally:
            module.APPROVED_DIR = original_approved_dir


def run_tests():
    test_load_json_existing_file()
    test_load_json_missing_file_returns_empty_dict()
    test_get_pending_review_count_from_pack()
    test_get_pending_review_count_missing_pack_returns_zero()
    test_clean_approved_dir_removes_old_files_and_recreates_dir()

    print("test_continue_after_manual_review.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()