import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from normalize import (
    only_digits,
    remove_accents,
    normalize_name,
    money_to_cents,
    normalize_date,
)


def test_only_digits():
    assert only_digits("123.456.789-09") == "12345678909"
    assert only_digits("11.222.333/0001-81") == "11222333000181"


def test_remove_accents():
    assert remove_accents("José São Paulo") == "Jose Sao Paulo"


def test_normalize_name():
    assert normalize_name("José da Silva") == "JOSE DA SILVA"
    assert normalize_name("Plano Saúde Exemplo S.A.") == "PLANO SAUDE EXEMPLO S.A."


def test_money_to_cents():
    assert money_to_cents("R$ 500,00") == 50000
    assert money_to_cents("R$ 3.600,00") == 360000
    assert money_to_cents("R$ 250.000,00") == 25000000


def test_normalize_date():
    assert normalize_date("15/03/2025") == "15032025"
    assert normalize_date("10/05/2020") == "10052020"


def run_tests():
    test_only_digits()
    test_remove_accents()
    test_normalize_name()
    test_money_to_cents()
    test_normalize_date()
    print("test_normalize.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()