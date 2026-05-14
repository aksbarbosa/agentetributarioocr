import json
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from extract_structured_batch import (
    build_batch_response,
    collect_text_files,
    safe_json_name,
    should_save_extraction,
)


def test_collect_text_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir)

        (input_dir / "a.txt").write_text("A", encoding="utf-8")
        (input_dir / "b.txt").write_text("B", encoding="utf-8")
        (input_dir / "c.md").write_text("C", encoding="utf-8")

        files = collect_text_files(str(input_dir))

        assert [file.name for file in files] == ["a.txt", "b.txt"]


def test_safe_json_name():
    assert safe_json_name(Path("teste_recibo.txt")) == "teste_recibo.json"
    assert safe_json_name(Path("recibo medico.txt")) == "recibo medico.json"


def test_should_save_extraction_recibo_medico():
    response = {
        "extraction": {
            "document_type": "recibo_medico",
        }
    }

    assert should_save_extraction(response) is True


def test_should_not_save_unknown_extraction():
    response = {
        "extraction": {
            "document_type": "desconhecido",
        }
    }

    assert should_save_extraction(response) is False


def test_build_batch_response_saves_recibo_medico():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "texts"
        output_dir = Path(temp_dir) / "structured"

        input_dir.mkdir()

        (input_dir / "teste_recibo.txt").write_text(
            "\n".join(
                [
                    "RECIBO MEDICO",
                    "Recebi de JOSE DA SILVA o valor de R$ 300,00 referente a consulta medica.",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "DATA DO PAGAMENTO: 10032025",
                    "MEDICO: DR. CARLOS PEREIRA",
                    "CRM 12345",
                    "CPF DO PROFISSIONAL: 12345678909",
                    "PACIENTE: JOSE DA SILVA",
                ]
            ),
            encoding="utf-8",
        )

        (input_dir / "desconhecido.txt").write_text(
            "Texto aleatorio sem palavras fiscais reconhecidas.",
            encoding="utf-8",
        )

        response = build_batch_response(str(input_dir), str(output_dir))

        assert response["total_files"] == 2
        assert response["summary"]["saved_count"] == 1
        assert response["summary"]["requires_review_count"] == 1
        assert response["summary"]["by_document_type"]["recibo_medico"] == 1
        assert response["summary"]["by_document_type"]["desconhecido"] == 1

        saved_file = output_dir / "teste_recibo.json"

        assert saved_file.exists()

        data = json.loads(saved_file.read_text(encoding="utf-8"))

        assert data["document_type"] == "recibo_medico"
        assert data["fields"]["valor_pago"]["value"] == 30000


def test_extract_structured_batch_cli_outputs():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "texts"
        output_dir = Path(temp_dir) / "structured"
        output_json = Path(temp_dir) / "batch.json"
        output_report = Path(temp_dir) / "batch.report.md"

        input_dir.mkdir()

        (input_dir / "teste_recibo.txt").write_text(
            "\n".join(
                [
                    "RECIBO MEDICO",
                    "Recebi de JOSE DA SILVA o valor de R$ 300,00 referente a consulta medica.",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "DATA DO PAGAMENTO: 10032025",
                    "MEDICO: DR. CARLOS PEREIRA",
                    "CRM 12345",
                    "CPF DO PROFISSIONAL: 12345678909",
                    "PACIENTE: JOSE DA SILVA",
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "tools/extract_structured_batch.py",
                str(input_dir),
                str(output_dir),
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

        assert data["total_files"] == 1
        assert data["summary"]["saved_count"] == 1
        assert data["summary"]["requires_review_count"] == 0

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Relatório de extração estruturada em lote" in report_text
        assert "Extrações salvas: 1" in report_text
        assert "Arquivos que exigem revisão: 0" in report_text

        saved_file = output_dir / "teste_recibo.json"
        assert saved_file.exists()


def run_tests():
    test_collect_text_files()
    test_safe_json_name()
    test_should_save_extraction_recibo_medico()
    test_should_not_save_unknown_extraction()
    test_build_batch_response_saves_recibo_medico()
    test_extract_structured_batch_cli_outputs()
    print("test_extract_structured_batch.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()