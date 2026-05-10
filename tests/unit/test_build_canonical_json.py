import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from build_canonical_json import build_canonical_json


def load_fixture(filename: str) -> dict:
    path = PROJECT_ROOT / "inputs" / "extracted" / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_build_informe_pj():
    extracted = load_fixture("informe_pj_exemplo.json")
    canonical = build_canonical_json(extracted)

    rendimentos = canonical["rendimentos"]["tributaveis_pj"]

    assert len(rendimentos) == 1
    assert rendimentos[0]["cnpj_pagador"] == "11222333000181"
    assert rendimentos[0]["rendimento_total"] == 8500000
    assert canonical["pagamentos"] == []
    assert canonical["bens"] == []


def test_build_recibo_medico():
    extracted = load_fixture("recibo_medico_exemplo.json")
    canonical = build_canonical_json(extracted)

    pagamentos = canonical["pagamentos"]

    assert len(pagamentos) == 1
    assert pagamentos[0]["codigo"] == "10"
    assert pagamentos[0]["descricao"] == "CONSULTA MEDICA"
    assert pagamentos[0]["valor_pago"] == 50000
    assert pagamentos[0]["data_pagamento"] == "15032025"
    assert canonical["rendimentos"]["tributaveis_pj"] == []
    assert canonical["bens"] == []


def test_build_plano_saude():
    extracted = load_fixture("plano_saude_exemplo.json")
    canonical = build_canonical_json(extracted)

    pagamentos = canonical["pagamentos"]

    assert len(pagamentos) == 1
    assert pagamentos[0]["codigo"] == "26"
    assert pagamentos[0]["descricao"] == "PLANO DE SAUDE"
    assert pagamentos[0]["valor_pago"] == 360000
    assert pagamentos[0]["valor_nao_dedutivel"] == 0
    assert canonical["rendimentos"]["tributaveis_pj"] == []
    assert canonical["bens"] == []


def test_build_bem_imovel():
    extracted = load_fixture("bem_imovel_exemplo.json")
    canonical = build_canonical_json(extracted)

    bens = canonical["bens"]

    assert len(bens) == 1
    assert bens[0]["tipo_bem"] == "IMOVEL"
    assert bens[0]["grupo_bem"] == "01"
    assert bens[0]["codigo_bem"] == "11"
    assert bens[0]["valor_anterior"] == 25000000
    assert bens[0]["valor_atual"] == 25000000
    assert bens[0]["endereco"]["cep"] == "01234567"
    assert bens[0]["endereco"]["uf"] == "SP"

    requires_review = canonical["requires_review"]
    fields_review = [item["field"] for item in requires_review]

    assert "matricula" in fields_review


def test_build_bem_veiculo():
    extracted = load_fixture("bem_veiculo_exemplo.json")
    canonical = build_canonical_json(extracted)

    bens = canonical["bens"]

    assert len(bens) == 1
    assert bens[0]["tipo_bem"] == "VEICULO"
    assert bens[0]["grupo_bem"] == "02"
    assert bens[0]["codigo_bem"] == "01"
    assert bens[0]["descricao"] == "AUTOMOVEL MARCA TOYOTA, MODELO COROLLA XEI, ANO 2020, PLACA ABC1D23"
    assert bens[0]["valor_anterior"] == 8000000
    assert bens[0]["valor_atual"] == 8000000
    assert bens[0]["renavam"] == "12345678901"
    assert bens[0]["placa"] == "ABC1D23"
    assert bens[0]["marca"] == "TOYOTA"
    assert bens[0]["modelo"] == "COROLLA XEI"
    assert bens[0]["ano_fabricacao"] == "2020"
    assert bens[0]["data_aquisicao"] == "20082020"


def test_document_type_nao_suportado():
    extracted = {
        "document_type": "tipo_inexistente",
        "fields": {}
    }

    try:
        build_canonical_json(extracted)
    except ValueError as error:
        assert "Tipo de documento ainda não suportado" in str(error)
    else:
        raise AssertionError("Era esperado ValueError para document_type não suportado.")


def run_tests():
    test_build_informe_pj()
    test_build_recibo_medico()
    test_build_plano_saude()
    test_build_bem_imovel()
    test_build_bem_veiculo()
    test_document_type_nao_suportado()
    print("test_build_canonical_json.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()