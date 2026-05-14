import json
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from extract_text import (
    build_summary,
    extract_text_from_file,
    extract_text_from_raw_inputs,
    read_text_file,
    safe_output_name,
)


def test_safe_output_name():
    assert safe_output_name("inputs/raw/recibo medico.txt") == "recibo_medico.txt"
    assert safe_output_name("inputs/raw/documento.pdf") == "documento.txt"
    assert safe_output_name("inputs/raw/imagem.jpg") == "imagem.txt"


def test_read_text_file_utf8():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "arquivo.txt"
        path.write_text("texto com acentuação", encoding="utf-8")

        text, warnings = read_text_file(path)

        assert text == "texto com acentuação"
        assert warnings == []


def test_extract_text_from_text_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "recibo.txt"
        output_dir = Path(temp_dir) / "extracted"

        input_path.write_text("RECIBO MEDICO\nCRM 12345", encoding="utf-8")

        file_info = {
            "path": str(input_path),
            "name": input_path.name,
            "extension": ".txt",
            "size_bytes": input_path.stat().st_size,
            "file_type": "text",
            "can_extract_text": True,
            "requires_ocr": False,
        }

        result = extract_text_from_file(file_info, str(output_dir))

        assert result["source_name"] == "recibo.txt"
        assert result["file_type"] == "text"
        assert result["status"] == "extracted"
        assert result["text_length"] > 0
        assert result["warnings"] == []

        output_path = Path(result["text_output_path"])

        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == "RECIBO MEDICO\nCRM 12345"


def test_extract_text_from_image_requires_ocr():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "imagem.jpg"
        output_dir = Path(temp_dir) / "extracted"

        input_path.write_text("fake image", encoding="utf-8")

        file_info = {
            "path": str(input_path),
            "name": input_path.name,
            "extension": ".jpg",
            "size_bytes": input_path.stat().st_size,
            "file_type": "image",
            "can_extract_text": True,
            "requires_ocr": True,
        }

        result = extract_text_from_file(file_info, str(output_dir))

        assert result["source_name"] == "imagem.jpg"
        assert result["file_type"] == "image"
        assert result["status"] in {"requires_ocr", "extracted"}

        if result["status"] == "requires_ocr":
            assert result["text_output_path"] is None
            assert result["text_length"] == 0
            assert result["warnings"]

        if result["status"] == "extracted":
            assert result["text_output_path"] is not None
            assert result["text_length"] > 0

def test_extract_text_from_unsupported_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "arquivo.xyz"
        output_dir = Path(temp_dir) / "extracted"

        input_path.write_text("conteudo", encoding="utf-8")

        file_info = {
            "path": str(input_path),
            "name": input_path.name,
            "extension": ".xyz",
            "size_bytes": input_path.stat().st_size,
            "file_type": "unsupported",
            "can_extract_text": False,
            "requires_ocr": False,
        }

        result = extract_text_from_file(file_info, str(output_dir))

        assert result["source_name"] == "arquivo.xyz"
        assert result["file_type"] == "unsupported"
        assert result["status"] == "unsupported"
        assert result["text_output_path"] is None
        assert result["text_length"] == 0
        assert "Tipo de arquivo não suportado" in result["warnings"][0]


def test_build_summary():
    results = [
        {"status": "extracted"},
        {"status": "requires_ocr"},
        {"status": "unsupported"},
        {"status": "extracted"},
    ]

    summary = build_summary(results)

    assert summary["by_status"]["extracted"] == 2
    assert summary["by_status"]["requires_ocr"] == 1
    assert summary["by_status"]["unsupported"] == 1
    assert summary["extracted_count"] == 2
    assert summary["requires_ocr_count"] == 1
    assert summary["unsupported_count"] == 1


def test_extract_text_from_raw_inputs():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "raw"
        output_dir = Path(temp_dir) / "extracted"

        input_dir.mkdir()

        (input_dir / "recibo.txt").write_text("RECIBO MEDICO\nCRM 12345", encoding="utf-8")
        (input_dir / "imagem.jpg").write_text("fake image", encoding="utf-8")
        (input_dir / "arquivo.xyz").write_text("nao suportado", encoding="utf-8")

        response = extract_text_from_raw_inputs(str(input_dir), str(output_dir))

        assert response["input_dir"] == str(input_dir)
        assert response["output_text_dir"] == str(output_dir)
        assert response["total_files"] == 3
        assert response["summary"]["extracted_count"] == 1
        assert response["summary"]["requires_ocr_count"] == 1
        assert response["summary"]["unsupported_count"] == 1

        extracted_file = output_dir / "recibo.txt"

        assert extracted_file.exists()
        assert "RECIBO MEDICO" in extracted_file.read_text(encoding="utf-8")


def test_extract_text_cli_outputs():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "raw"
        output_text_dir = Path(temp_dir) / "extracted"
        output_json = Path(temp_dir) / "extract-text.json"
        output_report = Path(temp_dir) / "extract-text.report.md"

        input_dir.mkdir()

        (input_dir / "recibo.txt").write_text("RECIBO MEDICO\nCRM 12345", encoding="utf-8")
        (input_dir / "imagem.jpg").write_text("fake image", encoding="utf-8")
        (input_dir / "arquivo.xyz").write_text("nao suportado", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "tools/extract_text.py",
                str(input_dir),
                str(output_text_dir),
                str(output_json),
                str(output_report),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_json.exists()
        assert output_report.exists()

        data = json.loads(output_json.read_text(encoding="utf-8"))

        assert data["total_files"] == 3
        assert data["summary"]["extracted_count"] == 1
        assert data["summary"]["requires_ocr_count"] == 1
        assert data["summary"]["unsupported_count"] == 1

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Relatório de extração de texto" in report_text
        assert "Textos extraídos: 1" in report_text
        assert "Arquivos que exigem OCR real: 1" in report_text
        assert "Arquivos não suportados: 1" in report_text


def test_extract_text_json_cli():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "raw"
        input_dir.mkdir()

        (input_dir / "recibo.txt").write_text("RECIBO MEDICO\nCRM 12345", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "tools/extract_text.py",
                str(input_dir),
                "--json",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        assert data["total_files"] == 1
        assert data["summary"]["extracted_count"] == 1
        assert data["results"][0]["status"] == "extracted"


def run_tests():
    test_safe_output_name()
    test_read_text_file_utf8()
    test_extract_text_from_text_file()
    test_extract_text_from_image_requires_ocr()
    test_extract_text_from_unsupported_file()
    test_build_summary()
    test_extract_text_from_raw_inputs()
    test_extract_text_cli_outputs()
    test_extract_text_json_cli()
    print("test_extract_text.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()