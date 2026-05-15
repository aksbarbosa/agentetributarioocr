import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from compare_ocr_outputs import (
    build_response,
    collect_txt_files,
    compare_file,
    read_text,
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_collect_txt_files_only_txt():
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)

        write_text(directory / "a.txt", "abc")
        write_text(directory / "b.md", "markdown")
        write_text(directory / "c.txt", "def")

        files = collect_txt_files(str(directory))

        assert sorted(files.keys()) == ["a.txt", "c.txt"]


def test_collect_txt_files_missing_dir_returns_empty():
    with tempfile.TemporaryDirectory() as tmp:
        missing_dir = Path(tmp) / "missing"

        files = collect_txt_files(str(missing_dir))

        assert files == {}


def test_read_text_with_utf8():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "texto.txt"
        write_text(path, "Olá mundo")

        assert read_text(path) == "Olá mundo"


def test_compare_file_prepared_longer():
    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "original.txt"
        prepared = Path(tmp) / "prepared.txt"

        write_text(original, "abc")
        write_text(prepared, "abcdef")

        result = compare_file("doc.txt", original, prepared)

        assert result["file"] == "doc.txt"
        assert result["status"] == "prepared_longer"
        assert result["original_chars"] == 3
        assert result["prepared_chars"] == 6
        assert result["delta_chars"] == 3


def test_compare_file_prepared_shorter():
    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "original.txt"
        prepared = Path(tmp) / "prepared.txt"

        write_text(original, "abcdef")
        write_text(prepared, "abc")

        result = compare_file("doc.txt", original, prepared)

        assert result["status"] == "prepared_shorter"
        assert result["delta_chars"] == -3


def test_compare_file_same_length():
    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "original.txt"
        prepared = Path(tmp) / "prepared.txt"

        write_text(original, "abc")
        write_text(prepared, "xyz")

        result = compare_file("doc.txt", original, prepared)

        assert result["status"] == "same_length"
        assert result["original_chars"] == 3
        assert result["prepared_chars"] == 3
        assert result["delta_chars"] == 0


def test_compare_file_missing_prepared():
    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "original.txt"
        write_text(original, "abc")

        result = compare_file("doc.txt", original, None)

        assert result["status"] == "missing_prepared"
        assert result["original_chars"] == 3
        assert result["prepared_chars"] == 0


def test_compare_file_missing_original():
    with tempfile.TemporaryDirectory() as tmp:
        prepared = Path(tmp) / "prepared.txt"
        write_text(prepared, "abc")

        result = compare_file("doc.txt", None, prepared)

        assert result["status"] == "missing_original"
        assert result["original_chars"] == 0
        assert result["prepared_chars"] == 3


def test_build_response_summary():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        original_dir = base / "original"
        prepared_dir = base / "prepared"

        write_text(original_dir / "a.txt", "abc")
        write_text(prepared_dir / "a.txt", "abcdef")

        write_text(original_dir / "b.txt", "abcdef")
        write_text(prepared_dir / "b.txt", "abc")

        write_text(original_dir / "c.txt", "abc")
        write_text(prepared_dir / "c.txt", "xyz")

        write_text(original_dir / "only_original.txt", "abc")
        write_text(prepared_dir / "only_prepared.txt", "abc")

        response = build_response(str(original_dir), str(prepared_dir))

        assert response["summary"]["files_compared"] == 5
        assert response["summary"]["prepared_longer"] == 1
        assert response["summary"]["prepared_shorter"] == 1
        assert response["summary"]["same_length"] == 1
        assert response["summary"]["missing_prepared"] == 1
        assert response["summary"]["missing_original"] == 1


def run_tests():
    test_collect_txt_files_only_txt()
    test_collect_txt_files_missing_dir_returns_empty()
    test_read_text_with_utf8()
    test_compare_file_prepared_longer()
    test_compare_file_prepared_shorter()
    test_compare_file_same_length()
    test_compare_file_missing_prepared()
    test_compare_file_missing_original()
    test_build_response_summary()

    print("test_compare_ocr_outputs.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()