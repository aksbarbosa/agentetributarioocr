import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from validate import (
    validate_cpf,
    validate_cnpj,
    validate_cpf_or_cnpj,
    is_ddmmaaaa,
    validate_canonical_irpf,
)


def test_validate_cpf():
    assert validate_cpf("12345678909") is True
    assert validate_cpf("12345678900") is False
    assert validate_cpf("11111111111") is False


def test_validate_cnpj():
    assert validate_cnpj("11222333000181") is True
    assert validate_cnpj("11222333000180") is False
    assert validate_cnpj("11111111111111") is False


def test_validate_cpf_or_cnpj():
    assert validate_cpf_or_cnpj("12345678909") is True
    assert validate_cpf_or_cnpj("11222333000181") is True
    assert validate_cpf_or_cnpj("123") is False


def test_is_ddmmaaaa():
    assert is_ddmmaaaa("15032025") is True
    assert is_ddmmaaaa("32132025") is False
    assert is_ddmmaaaa("150325") is False


def test_validate_canonical_minimal():
    data = {
        "$schema": "irpf-2026-v1",
        "exercicio": 2026,
        "ano_calendario": 2025,
        "tipo_declaracao": "AJUSTE_ANUAL",
        "modelo": "AUTO",
        "declarante": {
            "cpf": "12345678909",
            "nome": "JOSE DA SILVA",
            "data_nascimento": "01011980"
        },
        "rendimentos": {
            "tributaveis_pj": []
        },
        "pagamentos": [],
        "bens": [],
        "dividas": [],
        "avisos": [],
        "requires_review": []
    }

    result = validate_canonical_irpf(data)

    assert result["valid"] is True
    assert result["errors"] == []


def run_tests():
    test_validate_cpf()
    test_validate_cnpj()
    test_validate_cpf_or_cnpj()
    test_is_ddmmaaaa()
    test_validate_canonical_minimal()
    print("test_validate.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()