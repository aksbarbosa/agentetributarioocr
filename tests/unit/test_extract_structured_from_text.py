import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from extract_structured_from_text import (
    build_bem_imovel_extraction,
    build_structured_extraction,
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_structured_extraction_recibo_medico():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "recibo.txt"

        write_text(
            path,
            """
            Recibo Médico

            CPF DO DECLARANTE: 123.456.789-09
            Nome do Paciente
            JOSE DA SILVA

            CPF DO PROFISSIONAL: 987.654.321-00
            Nome do Médico
            DRA. MARIA OLIVEIRA

            DATA: 15/03/2025
            VALOR TOTAL: R$ 500,00
            CONSULTA MEDICA
            """,
        )

        response = build_structured_extraction(str(path))
        extraction = response["extraction"]

        assert extraction["document_type"] == "recibo_medico"
        assert extraction["fields"]["cpf_declarante"]["value"] == "12345678909"
        assert extraction["fields"]["nome_declarante"]["value"] == "JOSE DA SILVA"
        assert extraction["fields"]["cpf_cnpj_prestador"]["value"] == "98765432100"
        assert extraction["fields"]["nome_prestador"]["value"] == "DRA. MARIA OLIVEIRA"
        assert extraction["fields"]["valor_pago"]["value"] == 50000
        assert extraction["fields"]["data_pagamento"]["value"] == "15032025"


def test_build_structured_extraction_plano_saude():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "plano.txt"

        write_text(
            path,
            """
            PLANOS DE SAUDE
            UNIMED NORDESTE RS SOCIEDADE COOP DE SERV MEDICOS LTDA
            CNPJ/CPF: 87.827.689/0001-00

            TOMADOR DE SERVIÇOS
            CPF DO DECLARANTE: 123.456.789-09

            DISCRIMINAÇÃO DOS SERVIÇOS
            COPARTICIPACAO

            VALOR TOTAL DA NOTA FISCAL: R$ 908,00
            VALOR LÍQUIDO DA NOTA FISCAL: R$ 908,00
            """,
        )

        response = build_structured_extraction(str(path))
        extraction = response["extraction"]

        assert extraction["document_type"] == "plano_saude"
        assert extraction["fields"]["cpf_declarante"]["value"] == "12345678909"
        assert extraction["fields"]["cnpj_operadora"]["value"] == "87827689000100"
        assert extraction["fields"]["valor_pago"]["value"] == 90800
        assert extraction["fields"]["valor_nao_dedutivel"]["value"] == 0
        assert extraction["fields"]["descricao"]["value"] == "COPARTICIPACAO"


def test_build_structured_extraction_informe_rendimentos_pj():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "informe.txt"

        write_text(
            path,
            """
            COMPROVANTE DE RENDIMENTOS PAGOS E DE IMPOSTO SOBRE A RENDA RETIDO NA FONTE
            ANO-CALENDÁRIO 2025

            FONTE PAGADORA
            11.222.333/0001-81 EMPRESA EXEMPLO LTDA

            PESSOA FÍSICA BENEFICIÁRIA DOS RENDIMENTOS
            123.456.789-09 JOSE DA SILVA

            RENDIMENTOS TRIBUTÁVEIS: R$ 85.000,00
            PREVIDÊNCIA OFICIAL: R$ 8.500,00
            IMPOSTO DE RENDA RETIDO NA FONTE: R$ 4.250,00
            DÉCIMO TERCEIRO SALÁRIO: R$ 7.000,00
            IRRF SOBRE DÉCIMO TERCEIRO: R$ 350,00
            """,
        )

        response = build_structured_extraction(str(path))
        extraction = response["extraction"]

        assert extraction["document_type"] == "informe_rendimentos_pj"
        assert extraction["fields"]["cpf_declarante"]["value"] == "12345678909"
        assert extraction["fields"]["nome_declarante"]["value"] == "JOSE DA SILVA"
        assert extraction["fields"]["cnpj_pagador"]["value"] == "11222333000181"
        assert extraction["fields"]["nome_pagador"]["value"] == "EMPRESA EXEMPLO LTDA"
        assert extraction["fields"]["rendimento_total"]["value"] == 8500000
        assert extraction["fields"]["previdencia_oficial"]["value"] == 850000
        assert extraction["fields"]["irrf"]["value"] == 425000


def test_build_structured_extraction_bem_veiculo():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "veiculo.txt"

        write_text(
            path,
            """
            DOCUMENTO DE VEÍCULO
            CPF DO DECLARANTE: 123.456.789-09

            MARCA: TOYOTA
            MODELO: COROLLA XEI
            ANO FABRICAÇÃO: 2020
            PLACA: ABC1D23
            RENAVAM: 12345678901

            DATA DE AQUISIÇÃO: 20/08/2020
            VALOR ATUAL: R$ 80.000,00
            """,
        )

        response = build_structured_extraction(str(path))
        extraction = response["extraction"]

        assert extraction["document_type"] == "bem_veiculo"
        assert extraction["fields"]["cpf_declarante"]["value"] == "12345678909"
        assert extraction["fields"]["marca"]["value"] == "TOYOTA"
        assert extraction["fields"]["modelo"]["value"] == "COROLLA XEI"
        assert extraction["fields"]["ano_fabricacao"]["value"] == "2020"
        assert extraction["fields"]["placa"]["value"] == "ABC1D23"
        assert extraction["fields"]["renavam"]["value"] == "12345678901"
        assert extraction["fields"]["valor_atual"]["value"] == 8000000


def test_build_structured_extraction_bem_imovel():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "imovel.txt"

        write_text(
            path,
            """
            BEM IMÓVEL
            CPF DO DECLARANTE: 123.456.789-09

            LOGRADOURO: RUA DAS FLORES
            NUMERO: 123
            BAIRRO: CENTRO
            MUNICIPIO: SAO PAULO
            UF: SP
            CEP: 01234-567

            IPTU: 1234567890
            MATRICULA: 12345
            DATA DE AQUISIÇÃO: 10/05/2020
            VALOR ATUAL: R$ 250.000,00
            """,
        )

        response = build_structured_extraction(str(path))
        extraction = response["extraction"]

        assert extraction["document_type"] == "bem_imovel"
        assert extraction["fields"]["cpf_declarante"]["value"] == "12345678909"
        assert extraction["fields"]["logradouro"]["value"] == "RUA DAS FLORES"
        assert extraction["fields"]["numero"]["value"] == "123"
        assert extraction["fields"]["bairro"]["value"] == "CENTRO"
        assert extraction["fields"]["municipio"]["value"] == "SAO PAULO"
        assert extraction["fields"]["uf"]["value"] == "SP"
        assert extraction["fields"]["cep"]["value"] == "01234567"
        assert extraction["fields"]["iptu"]["value"] == "1234567890"
        assert extraction["fields"]["matricula"]["value"] == "12345"
        assert extraction["fields"]["valor_atual"]["value"] == 25000000


def test_build_bem_imovel_registry_description():
    text = """
    UNIDADE AUTÔNOMA:
    Apartamento localizado no 6º andar.
    20º Subdistrito Jardim América, desta Capital.
    área útil privativa de 36,250m²
    área total de 108,941m²
    fração ideal de 1,7676%.
    13º Oficial de Registro de Imóveis
    Comarca de São Paulo - SP
    """

    result = build_bem_imovel_extraction("imovel.txt", text)

    assert result["document_type"] == "bem_imovel"

    descricao = result["fields"]["descricao"]["value"]

    assert descricao is not None
    assert "UNIDADE AUTONOMA CONSTANTE EM MATRICULA DE REGISTRO DE IMOVEIS" in descricao
    assert "JARDIM AMERICA" in descricao
    assert "AREA UTIL PRIVATIVA DE 36.250 M2" in descricao
    assert "AREA TOTAL DE 108.941 M2" in descricao
    assert "FRACAO IDEAL DE 1.7676%" in descricao


def test_build_structured_extraction_unknown_document():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "desconhecido.txt"

        write_text(
            path,
            """
            DOCUMENTO SEM RELAÇÃO COM IRPF
            TRANSPORTE RODOVIÁRIO DE CARGAS
            CT-E
            DACTE
            """,
        )

        response = build_structured_extraction(str(path))
        extraction = response["extraction"]

        assert extraction["document_type"] == "desconhecido"
        assert extraction["fields"] == {}
        assert len(extraction["requires_review"]) == 1


def run_tests():
    test_build_structured_extraction_recibo_medico()
    test_build_structured_extraction_plano_saude()
    test_build_structured_extraction_informe_rendimentos_pj()
    test_build_structured_extraction_bem_veiculo()
    test_build_structured_extraction_bem_imovel()
    test_build_bem_imovel_registry_description()
    test_build_structured_extraction_unknown_document()

    print("test_extract_structured_from_text.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()