import json
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from scan_raw_inputs import classify_file_extension, scan_raw_inputs


def test_classify_file_extension():
    assert classify_file_extension(Path("arquivo.txt")) == "text"
    assert classify_file_extension(Path("arquivo.pdf")) == "pdf"
    assert classify_file_extension(Path("arquivo.png")) == "image"
    assert classify_file_extension(Path("arquivo.jpg")) == "image"
    assert classify_file_extension(Path("arquivo.jpeg")) == "image"
    assert classify_file_extension(Path("arquivo.tif")) == "image"
    assert classify_file_extension(Path("arquivo.tiff")) == "image"
    assert classify_file_extension(Path("arquivo.xyz")) == "unsupported"


def test_scan_raw_inputs_with_mixed_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir)

        (input_dir / "documento.txt").write_text("texto", encoding="utf-8")
        (input_dir / "arquivo.pdf").write_text("pdf fake", encoding="utf-8")
        (input_dir / "imagem.jpg").write_text("imagem fake", encoding="utf-8")
        (input_dir / "arquivo.xyz").write_text("nao suportado", encoding="utf-8")

        manifest = scan_raw_inputs(str(input_dir))

        assert manifest["input_dir"] == str(input_dir)
        assert manifest["total_files"] == 4

        assert manifest["summary"]["by_file_type"]["text"] == 1
        assert manifest["summary"]["by_file_type"]["pdf"] == 1
        assert manifest["summary"]["by_file_type"]["image"] == 1
        assert manifest["summary"]["by_file_type"]["unsupported"] == 1

        assert manifest["summary"]["extractable_count"] == 3
        assert manifest["summary"]["requires_ocr_count"] == 1
        assert manifest["summary"]["unsupported_count"] == 1

        by_name = {item["name"]: item for item in manifest["files"]}

        assert by_name["documento.txt"]["file_type"] == "text"
        assert by_name["documento.txt"]["can_extract_text"] is True
        assert by_name["documento.txt"]["requires_ocr"] is False

        assert by_name["arquivo.pdf"]["file_type"] == "pdf"
        assert by_name["arquivo.pdf"]["can_extract_text"] is True
        assert by_name["arquivo.pdf"]["requires_ocr"] is False

        assert by_name["imagem.jpg"]["file_type"] == "image"
        assert by_name["imagem.jpg"]["can_extract_text"] is True
        assert by_name["imagem.jpg"]["requires_ocr"] is True

        assert by_name["arquivo.xyz"]["file_type"] == "unsupported"
        assert by_name["arquivo.xyz"]["can_extract_text"] is False
        assert by_name["arquivo.xyz"]["requires_ocr"] is False


def test_scan_raw_inputs_ignores_directories():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir)

        (input_dir / "documento.txt").write_text("texto", encoding="utf-8")
        (input_dir / "subpasta").mkdir()

        manifest = scan_raw_inputs(str(input_dir))

        assert manifest["total_files"] == 1
        assert manifest["files"][0]["name"] == "documento.txt"


def test_scan_raw_inputs_cli_outputs():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "raw"
        input_dir.mkdir()

        output_json = Path(temp_dir) / "manifest.json"
        output_report = Path(temp_dir) / "manifest.report.md"

        (input_dir / "documento.txt").write_text("texto", encoding="utf-8")
        (input_dir / "arquivo.pdf").write_text("pdf fake", encoding="utf-8")
        (input_dir / "imagem.png").write_text("imagem fake", encoding="utf-8")
        (input_dir / "arquivo.xyz").write_text("nao suportado", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "tools/scan_raw_inputs.py",
                str(input_dir),
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

        assert data["total_files"] == 4
        assert data["summary"]["extractable_count"] == 3
        assert data["summary"]["requires_ocr_count"] == 1
        assert data["summary"]["unsupported_count"] == 1

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Manifesto de documentos brutos" in report_text
        assert "Arquivos encontrados: 4" in report_text
        assert "Arquivos extraíveis: 3" in report_text
        assert "Arquivos que exigem OCR: 1" in report_text
        assert "Arquivos não suportados: 1" in report_text


def test_scan_raw_inputs_json_cli():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "raw"
        input_dir.mkdir()

        (input_dir / "documento.txt").write_text("texto", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "tools/scan_raw_inputs.py",
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
        assert data["summary"]["by_file_type"]["text"] == 1
        assert data["summary"]["extractable_count"] == 1


def run_tests():
    test_classify_file_extension()
    test_scan_raw_inputs_with_mixed_files()
    test_scan_raw_inputs_ignores_directories()
    test_scan_raw_inputs_cli_outputs()
    test_scan_raw_inputs_json_cli()
    print("test_scan_raw_inputs.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()