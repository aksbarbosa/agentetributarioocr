import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from export_dec_experimental import (
    build_bens_section,
    build_declarante_section,
    build_experimental_dec,
    build_pagamentos_section,
    build_report,
    build_rendimentos_section,
    money_to_reais,
    safe,
)


def make_canonical_data():
    return {
        "declarante": {
            "nome": "JOSE DA SILVA",
            "cpf": "12345678909",
            "data_nascimento": "01011980",
        },
        "rendimentos": {
            "tributaveis_pj": [
                {
                    "nome_pagador": "EMPRESA EXEMPLO LTDA",
                    "cnpj_pagador": "11222333000181",
                    "rendimento_total": 8500000,
                    "previdencia_oficial": 850000,
                    "decimo_terceiro": 700000,
                    "irrf": 425000,
                    "irrf_13": 35000,
                }
            ]
        },
        "pagamentos": [
            {
                "codigo": "10",
                "descricao": "CONSULTA MEDICA",
                "nome_prestador": "DRA MARIA OLIVEIRA",
                "cpf_cnpj_prestador": "12345678909",
                "tipo_beneficiario": "T",
                "tipo_documento": "1",
                "valor_pago": 50000,
                "valor_nao_dedutivel": 0,
                "data_pagamento": "15032025",
            }
        ],
        "bens": [
            {
                "tipo_bem": "VEICULO",
                "grupo": "02",
                "codigo": "01",
                "descricao": "AUTOMOVEL TOYOTA COROLLA",
                "valor_anterior": 8000000,
                "valor_atual": 8000000,
                "data_aquisicao": "20082020",
                "beneficiario": "T",
                "dados_veiculo": {
                    "renavam": "12345678901",
                    "placa": "ABC1D23",
                    "marca": "TOYOTA",
                    "modelo": "COROLLA XEI",
                    "ano_fabricacao": "2020",
                },
            }
        ],
    }


def test_money_to_reais():
    assert money_to_reais(0) == "0,00"
    assert money_to_reais(None) == "0,00"
    assert money_to_reais(50000) == "500,00"
    assert money_to_reais(8500000) == "85000,00"
    assert money_to_reais("abc") == "0,00"


def test_safe_removes_pipe_and_newline():
    assert safe(None) == ""
    assert safe("A|B") == "A B"
    assert safe("A\nB") == "A B"
    assert safe("  TEXTO  ") == "TEXTO"


def test_build_declarante_section():
    data = make_canonical_data()

    lines = build_declarante_section(data)
    joined = "\n".join(lines)

    assert "[DECLARANTE]" in joined
    assert "nome=JOSE DA SILVA" in joined
    assert "cpf=12345678909" in joined
    assert "data_nascimento=01011980" in joined


def test_build_rendimentos_section():
    data = make_canonical_data()

    lines = build_rendimentos_section(data)
    joined = "\n".join(lines)

    assert "[RENDIMENTOS_TRIBUTAVEIS_PJ]" in joined
    assert "nome_pagador=EMPRESA EXEMPLO LTDA" in joined
    assert "cnpj_pagador=11222333000181" in joined
    assert "rendimento_total=85000,00" in joined
    assert "irrf=4250,00" in joined


def test_build_pagamentos_section():
    data = make_canonical_data()

    lines = build_pagamentos_section(data)
    joined = "\n".join(lines)

    assert "[PAGAMENTOS]" in joined
    assert "codigo=10" in joined
    assert "descricao=CONSULTA MEDICA" in joined
    assert "nome_prestador=DRA MARIA OLIVEIRA" in joined
    assert "valor_pago=500,00" in joined


def test_build_bens_section():
    data = make_canonical_data()

    lines = build_bens_section(data)
    joined = "\n".join(lines)

    assert "[BENS_E_DIREITOS]" in joined
    assert "tipo_bem=VEICULO" in joined
    assert "descricao=AUTOMOVEL TOYOTA COROLLA" in joined
    assert "valor_atual=80000,00" in joined
    assert "renavam=12345678901" in joined
    assert "placa=ABC1D23" in joined


def test_build_experimental_dec():
    data = make_canonical_data()

    content = build_experimental_dec(data)

    assert "# IRPF OCR DEC - EXPORTAÇÃO EXPERIMENTAL" in content
    assert "[DECLARANTE]" in content
    assert "[RENDIMENTOS_TRIBUTAVEIS_PJ]" in content
    assert "[PAGAMENTOS]" in content
    assert "[BENS_E_DIREITOS]" in content


def test_build_report():
    data = make_canonical_data()

    report = build_report(
        "outputs/irpf-consolidado.json",
        "outputs/irpf-export-dec-experimental.txt",
        data,
    )

    assert "# Relatório de exportação DEC experimental" in report
    assert "Rendimentos tributáveis PJ: 1" in report
    assert "Pagamentos: 1" in report
    assert "Bens e direitos: 1" in report


def run_tests():
    test_money_to_reais()
    test_safe_removes_pipe_and_newline()
    test_build_declarante_section()
    test_build_rendimentos_section()
    test_build_pagamentos_section()
    test_build_bens_section()
    test_build_experimental_dec()
    test_build_report()

    print("test_export_dec_experimental.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()