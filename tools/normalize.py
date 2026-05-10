import re
import unicodedata
from decimal import Decimal, InvalidOperation


def only_digits(value: str | None) -> str:
    """
    Remove tudo que não for dígito.

    Exemplo:
    '123.456.789-09' -> '12345678909'
    """
    if value is None:
        return ""

    return re.sub(r"\D", "", str(value))


def remove_accents(value: str | None) -> str:
    """
    Remove acentos de uma string.

    Exemplo:
    'JOSÉ DA SILVA' -> 'JOSE DA SILVA'
    """
    if value is None:
        return ""

    normalized = unicodedata.normalize("NFD", str(value))
    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def normalize_name(value: str | None) -> str:
    """
    Normaliza nomes para uso no JSON canônico.

    Exemplo:
    '  José   da Silva ' -> 'JOSE DA SILVA'
    """
    if value is None:
        return ""

    value = remove_accents(value)
    value = value.upper()
    value = " ".join(value.split())

    return value


def money_to_cents(value: str | int | float | Decimal | None) -> int:
    """
    Converte valores monetários para centavos inteiros.

    Exemplos:
    'R$ 1.234,56' -> 123456
    '1234,56'     -> 123456
    1234.56       -> 123456

    Observação:
    No JSON canônico, dinheiro sempre será int em centavos.
    """
    if value is None or value == "":
        return 0

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(Decimal(str(value)) * 100)

    if isinstance(value, Decimal):
        return int(value * 100)

    text = str(value).strip()
    text = text.replace("R$", "").replace(" ", "")

    # Formato brasileiro: 1.234,56
    if "," in text:
        text = text.replace(".", "")
        text = text.replace(",", ".")

    try:
        number = Decimal(text)
    except InvalidOperation:
        raise ValueError(f"Valor monetário inválido: {value}")

    return int(number * 100)


def normalize_date(value: str | None) -> str:
    """
    Normaliza datas para DDMMAAAA.

    Exemplos:
    '01/01/1980' -> '01011980'
    '01-01-1980' -> '01011980'
    '01011980'   -> '01011980'
    """
    digits = only_digits(value)

    if len(digits) != 8:
        raise ValueError(f"Data inválida: {value}")

    day = int(digits[0:2])
    month = int(digits[2:4])
    year = int(digits[4:8])

    if not 1 <= day <= 31:
        raise ValueError(f"Dia inválido: {value}")

    if not 1 <= month <= 12:
        raise ValueError(f"Mês inválido: {value}")

    if year < 1900:
        raise ValueError(f"Ano inválido: {value}")

    return digits


if __name__ == "__main__":
    print(only_digits("123.456.789-09"))
    print(normalize_name("  José   da Silva "))
    print(money_to_cents("R$ 1.234,56"))
    print(normalize_date("01/01/1980"))