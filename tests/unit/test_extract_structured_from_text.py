import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from extract_structured_from_text import (
    build_structured_extraction,
    extract_date_by_label,
    extract_labeled_cpf_from_text,
    parse_money_to_cents,
)


def test_parse_money_to_cents():
    assert parse_money_to_cents("R$ 300,00") == 30000
    assert parse_money_to_cents("300,00") == 30000
    assert parse_money_to_cents("1.250,50") == 125050


def test_extract_labeled_cpf_from_text():
    text = "CPF DO DECLARANTE: 11122233344\nCPF DO PROFISSIONAL: 12345678909"

    assert extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE") == "11122233344"
    assert extract_labeled_cpf_from_text(text, "CPF DO PROFISSIONAL") == "12345678909"


def test_extract_date_by_label():
    text = "DATA DE NASCIMENTO: 01011980\nDATA DO PAGAMENTO: 10/03/2025"

    assert extract_date_by_label(text, "DATA DE NASCIMENTO") == "01011980"
    assert extract_date_by_label(text, "DATA DO PAGAMENTO") == "10032025"


def test_build_structured_extraction_recibo_medico():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "teste_recibo.txt"

        input_path.write_text(
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

        response = build_structured_extraction(str(input_path))
        extraction = response["extraction"]

        assert response["classification"]["document_type"] == "recibo_medico"
        assert extraction["document_type"] == "recibo_medico"

        fields = extraction["fields"]

        assert fields["cpf_declarante"]["value"] == "11122233344"
        assert fields["nome_declarante"]["value"] == "JOSE DA SILVA"
        assert fields["data_nascimento"]["value"] == "01011980"
        assert fields["cpf_cnpj_prestador"]["value"] == "12345678909"
        assert fields["nome_prestador"]["value"] == "DR. CARLOS PEREIRA"
        assert fields["valor_pago"]["value"] == 30000
        assert fields["data_pagamento"]["value"] == "10032025"
        assert fields["descricao"]["value"] == "CONSULTA MEDICA"

        assert extraction["requires_review"] == []


def run_tests():
    test_parse_money_to_cents()
    test_extract_labeled_cpf_from_text()
    test_extract_date_by_label()
    test_build_structured_extraction_recibo_medico()
    print("test_extract_structured_from_text.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()