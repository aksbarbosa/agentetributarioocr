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


def test_should_save_extraction_informe_rendimentos_pj():
    response = {
        "extraction": {
            "document_type": "informe_rendimentos_pj",
        }
    }

    assert should_save_extraction(response) is True


def test_should_save_extraction_plano_saude():
    response = {
        "extraction": {
            "document_type": "plano_saude",
        }
    }

    assert should_save_extraction(response) is True


def test_should_save_extraction_bem_veiculo():
    response = {
        "extraction": {
            "document_type": "bem_veiculo",
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


def test_build_batch_response_saves_supported_document_types():
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

        (input_dir / "informe_pj_teste.txt").write_text(
            "\n".join(
                [
                    "INFORME DE RENDIMENTOS PJ",
                    "",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "",
                    "FONTE PAGADORA: EMPRESA XYZ LTDA",
                    "CNPJ DA FONTE PAGADORA: 12345678000199",
                    "",
                    "RENDIMENTOS TRIBUTAVEIS: R$ 50000,00",
                    "PREVIDENCIA OFICIAL: R$ 5000,00",
                    "IMPOSTO DE RENDA RETIDO NA FONTE: R$ 7500,00",
                    "",
                    "DECIMO TERCEIRO SALARIO: R$ 4000,00",
                    "IRRF SOBRE DECIMO TERCEIRO: R$ 600,00",
                ]
            ),
            encoding="utf-8",
        )

        (input_dir / "plano_saude_teste.txt").write_text(
            "\n".join(
                [
                    "COMPROVANTE DE PAGAMENTO PLANO DE SAUDE",
                    "",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "",
                    "OPERADORA: SAUDE TOTAL LTDA",
                    "CNPJ DA OPERADORA: 11222333000144",
                    "",
                    "BENEFICIARIO: JOSE DA SILVA",
                    "VALOR PAGO: R$ 2400,00",
                    "VALOR NAO DEDUTIVEL: R$ 0,00",
                    "ANO CALENDARIO: 2025",
                ]
            ),
            encoding="utf-8",
        )

        (input_dir / "bem_veiculo_teste.txt").write_text(
            "\n".join(
                [
                    "DOCUMENTO DE VEICULO",
                    "",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "",
                    "VEICULO: HONDA CIVIC EXL",
                    "MARCA: HONDA",
                    "MODELO: CIVIC EXL",
                    "ANO FABRICACAO: 2020",
                    "PLACA: ABC1D23",
                    "RENAVAM: 12345678901",
                    "DATA DE AQUISICAO: 20082020",
                    "VALOR ANTERIOR: R$ 80000,00",
                    "VALOR ATUAL: R$ 85000,00",
                ]
            ),
            encoding="utf-8",
        )

        (input_dir / "desconhecido.txt").write_text(
            "Texto aleatorio sem palavras fiscais reconhecidas.",
            encoding="utf-8",
        )

        response = build_batch_response(str(input_dir), str(output_dir))

        assert response["total_files"] == 5
        assert response["summary"]["saved_count"] == 4
        assert response["summary"]["requires_review_count"] == 1

        assert response["summary"]["by_document_type"]["recibo_medico"] == 1
        assert response["summary"]["by_document_type"]["informe_rendimentos_pj"] == 1
        assert response["summary"]["by_document_type"]["plano_saude"] == 1
        assert response["summary"]["by_document_type"]["bem_veiculo"] == 1
        assert response["summary"]["by_document_type"]["desconhecido"] == 1

        recibo_file = output_dir / "teste_recibo.json"
        informe_file = output_dir / "informe_pj_teste.json"
        plano_file = output_dir / "plano_saude_teste.json"
        veiculo_file = output_dir / "bem_veiculo_teste.json"

        assert recibo_file.exists()
        assert informe_file.exists()
        assert plano_file.exists()
        assert veiculo_file.exists()

        recibo_data = json.loads(recibo_file.read_text(encoding="utf-8"))
        informe_data = json.loads(informe_file.read_text(encoding="utf-8"))
        plano_data = json.loads(plano_file.read_text(encoding="utf-8"))
        veiculo_data = json.loads(veiculo_file.read_text(encoding="utf-8"))

        assert recibo_data["document_type"] == "recibo_medico"
        assert recibo_data["fields"]["valor_pago"]["value"] == 30000

        assert informe_data["document_type"] == "informe_rendimentos_pj"
        assert informe_data["fields"]["nome_pagador"]["value"] == "EMPRESA XYZ LTDA"
        assert informe_data["fields"]["cnpj_pagador"]["value"] == "12345678000199"
        assert informe_data["fields"]["rendimento_total"]["value"] == 5000000
        assert informe_data["fields"]["previdencia_oficial"]["value"] == 500000
        assert informe_data["fields"]["irrf"]["value"] == 750000
        assert informe_data["fields"]["decimo_terceiro"]["value"] == 400000
        assert informe_data["fields"]["irrf_13"]["value"] == 60000

        assert plano_data["document_type"] == "plano_saude"
        assert plano_data["fields"]["nome_operadora"]["value"] == "SAUDE TOTAL LTDA"
        assert plano_data["fields"]["cnpj_operadora"]["value"] == "11222333000144"
        assert plano_data["fields"]["valor_pago"]["value"] == 240000
        assert plano_data["fields"]["valor_nao_dedutivel"]["value"] == 0
        assert plano_data["fields"]["descricao"]["value"] == "PLANO DE SAUDE"

        assert veiculo_data["document_type"] == "bem_veiculo"
        assert veiculo_data["fields"]["grupo_bem"]["value"] == "02"
        assert veiculo_data["fields"]["codigo_bem"]["value"] == "01"
        assert veiculo_data["fields"]["renavam"]["value"] == "12345678901"
        assert veiculo_data["fields"]["placa"]["value"] == "ABC1D23"
        assert veiculo_data["fields"]["marca"]["value"] == "HONDA"
        assert veiculo_data["fields"]["modelo"]["value"] == "CIVIC EXL"
        assert veiculo_data["fields"]["ano_fabricacao"]["value"] == "2020"
        assert veiculo_data["fields"]["data_aquisicao"]["value"] == "20082020"
        assert veiculo_data["fields"]["valor_anterior"]["value"] == 8000000
        assert veiculo_data["fields"]["valor_atual"]["value"] == 8500000


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

        (input_dir / "informe_pj_teste.txt").write_text(
            "\n".join(
                [
                    "INFORME DE RENDIMENTOS PJ",
                    "",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "",
                    "FONTE PAGADORA: EMPRESA XYZ LTDA",
                    "CNPJ DA FONTE PAGADORA: 12345678000199",
                    "",
                    "RENDIMENTOS TRIBUTAVEIS: R$ 50000,00",
                    "PREVIDENCIA OFICIAL: R$ 5000,00",
                    "IMPOSTO DE RENDA RETIDO NA FONTE: R$ 7500,00",
                    "",
                    "DECIMO TERCEIRO SALARIO: R$ 4000,00",
                    "IRRF SOBRE DECIMO TERCEIRO: R$ 600,00",
                ]
            ),
            encoding="utf-8",
        )

        (input_dir / "plano_saude_teste.txt").write_text(
            "\n".join(
                [
                    "COMPROVANTE DE PAGAMENTO PLANO DE SAUDE",
                    "",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "",
                    "OPERADORA: SAUDE TOTAL LTDA",
                    "CNPJ DA OPERADORA: 11222333000144",
                    "",
                    "BENEFICIARIO: JOSE DA SILVA",
                    "VALOR PAGO: R$ 2400,00",
                    "VALOR NAO DEDUTIVEL: R$ 0,00",
                    "ANO CALENDARIO: 2025",
                ]
            ),
            encoding="utf-8",
        )

        (input_dir / "bem_veiculo_teste.txt").write_text(
            "\n".join(
                [
                    "DOCUMENTO DE VEICULO",
                    "",
                    "DECLARANTE: JOSE DA SILVA",
                    "CPF DO DECLARANTE: 11122233344",
                    "DATA DE NASCIMENTO: 01011980",
                    "",
                    "VEICULO: HONDA CIVIC EXL",
                    "MARCA: HONDA",
                    "MODELO: CIVIC EXL",
                    "ANO FABRICACAO: 2020",
                    "PLACA: ABC1D23",
                    "RENAVAM: 12345678901",
                    "DATA DE AQUISICAO: 20082020",
                    "VALOR ANTERIOR: R$ 80000,00",
                    "VALOR ATUAL: R$ 85000,00",
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

        assert data["total_files"] == 4
        assert data["summary"]["saved_count"] == 4
        assert data["summary"]["requires_review_count"] == 0

        assert data["summary"]["by_document_type"]["recibo_medico"] == 1
        assert data["summary"]["by_document_type"]["informe_rendimentos_pj"] == 1
        assert data["summary"]["by_document_type"]["plano_saude"] == 1
        assert data["summary"]["by_document_type"]["bem_veiculo"] == 1

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Relatório de extração estruturada em lote" in report_text
        assert "Extrações salvas: 4" in report_text
        assert "Arquivos que exigem revisão: 0" in report_text
        assert "`recibo_medico`: 1" in report_text
        assert "`informe_rendimentos_pj`: 1" in report_text
        assert "`plano_saude`: 1" in report_text
        assert "`bem_veiculo`: 1" in report_text

        recibo_file = output_dir / "teste_recibo.json"
        informe_file = output_dir / "informe_pj_teste.json"
        plano_file = output_dir / "plano_saude_teste.json"
        veiculo_file = output_dir / "bem_veiculo_teste.json"

        assert recibo_file.exists()
        assert informe_file.exists()
        assert plano_file.exists()
        assert veiculo_file.exists()


def run_tests():
    test_collect_text_files()
    test_safe_json_name()
    test_should_save_extraction_recibo_medico()
    test_should_save_extraction_informe_rendimentos_pj()
    test_should_save_extraction_plano_saude()
    test_should_save_extraction_bem_veiculo()
    test_should_not_save_unknown_extraction()
    test_build_batch_response_saves_supported_document_types()
    test_extract_structured_batch_cli_outputs()
    print("test_extract_structured_batch.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()