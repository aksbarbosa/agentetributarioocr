import json
import sys
import tempfile
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from prepare_raw_for_ocr import (
    build_response,
    collect_files,
    prepare_file,
)


def write_text(path: Path, content: str = "texto") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (20, 20), color="white")
    image.save(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_collect_files_from_input_dir():
    with tempfile.TemporaryDirectory() as tmp:
        input_dir = Path(tmp) / "raw"
        input_dir.mkdir()

        write_text(input_dir / "a.txt")
        write_text(input_dir / "b.pdf")

        files = collect_files(str(input_dir))

        assert len(files) == 2
        assert files[0].name == "a.txt"
        assert files[1].name == "b.pdf"


def test_prepare_file_copies_non_image():
    with tempfile.TemporaryDirectory() as tmp:
        input_dir = Path(tmp) / "raw"
        output_dir = Path(tmp) / "prepared"

        source = input_dir / "documento.txt"
        write_text(source, "conteudo original")

        result = prepare_file(source, output_dir)

        assert result["status"] == "ok"
        assert result["kind"] == "non_image"
        assert result["action"] == "copied"

        output_path = Path(result["output_path"])
        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == "conteudo original"


def test_prepare_file_preprocesses_image():
    with tempfile.TemporaryDirectory() as tmp:
        input_dir = Path(tmp) / "raw"
        output_dir = Path(tmp) / "prepared"

        source = input_dir / "imagem.png"
        make_image(source)

        result = prepare_file(source, output_dir)

        assert result["status"] == "ok"
        assert result["kind"] == "image"
        assert result["action"] == "preprocessed"
        assert result["original_size"] == [20, 20]
        assert result["prepared_size"] == [40, 40]

        output_path = Path(result["output_path"])
        assert output_path.exists()
        assert output_path.suffix == ".png"


def test_build_response_mixes_images_and_non_images():
    with tempfile.TemporaryDirectory() as tmp:
        input_dir = Path(tmp) / "raw"
        output_dir = Path(tmp) / "prepared"

        make_image(input_dir / "imagem.png")
        write_text(input_dir / "documento.txt", "abc")

        response = build_response(str(input_dir), str(output_dir))

        assert response["summary"]["files_found"] == 2
        assert response["summary"]["images_found"] == 1
        assert response["summary"]["files_copied"] == 1
        assert response["summary"]["images_preprocessed"] == 1
        assert response["summary"]["error_count"] == 0

        assert output_dir.exists()
        assert len(list(output_dir.iterdir())) == 2


def test_build_response_records_bad_image_error():
    with tempfile.TemporaryDirectory() as tmp:
        input_dir = Path(tmp) / "raw"
        output_dir = Path(tmp) / "prepared"

        bad_image = input_dir / "imagem.jpg"
        write_text(bad_image, "")

        response = build_response(str(input_dir), str(output_dir))

        assert response["summary"]["files_found"] == 1
        assert response["summary"]["images_found"] == 0 or response["summary"]["images_found"] == 1
        assert response["summary"]["error_count"] == 1
        assert response["files"][0]["status"] == "error"


def run_tests():
    test_collect_files_from_input_dir()
    test_prepare_file_copies_non_image()
    test_prepare_file_preprocesses_image()
    test_build_response_mixes_images_and_non_images()
    test_build_response_records_bad_image_error()

    print("test_prepare_raw_for_ocr.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()