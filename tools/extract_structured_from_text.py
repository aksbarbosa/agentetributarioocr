import json
import re
import sys
from pathlib import Path

from classify_document import classify_document_text


def only_digits(value: str) -> str:
    """
    Mantém apenas dígitos.
    """
    return re.sub(r"\D", "", value or "")


def parse_money_to_cents(text: str) -> int | None:
    """
    Extrai o primeiro valor monetário encontrado e converte para centavos.

    Exemplos:
    R$ 300,00 -> 30000
    300,00 -> 30000
    """
    match = re.search(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*|\d+),(\d{2})", text)

    if not match:
        return None

    reais = match.group(1).replace(".", "")
    centavos = match.group(2)

    return int(reais) * 100 + int(centavos)


def extract_cpf_from_text(text: str) -> str | None:
    """
    Extrai o primeiro CPF encontrado no texto.
    """
    match = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", text)

    if not match:
        return None

    return only_digits(match.group(0))


def extract_labeled_cpf_from_text(text: str, label: str) -> str | None:
    """
    Extrai CPF associado a um rótulo específico.
    """
    pattern = rf"{label}\s*[:\-]?\s*(\d{{3}}\.?\d{{3}}\.?\d{{3}}-?\d{{2}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return only_digits(match.group(1))


def extract_date_by_label(text: str, label: str) -> str | None:
    """
    Extrai data associada a um rótulo específico.

    Aceita:
    01011980
    01/01/1980
    01-01-1980
    """
    pattern = rf"{label}\s*[:\-]?\s*(\d{{2}}[\/\-]?\d{{2}}[\/\-]?\d{{4}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return only_digits(match.group(1))


def extract_crm_from_text(text: str) -> str | None:
    """
    Extrai CRM simples do texto.
    """
    match = re.search(r"\bCRM\s*[:\-]?\s*([A-Z]{2}\s*)?\d{3,10}\b", text, flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(0).strip().upper()


def extract_professional_name(text: str) -> str | None:
    """
    Extrai nome do profissional em padrões simples.

    Evita capturar o cabeçalho "RECIBO MEDICO" como se fosse o nome.
    """
    lines = text.splitlines()

    for line in lines:
        line_clean = line.strip()

        if not line_clean:
            continue

        if re.fullmatch(r"RECIBO\s+M[EÉ]DICO", line_clean, flags=re.IGNORECASE):
            continue

        patterns = [
            r"^MEDICO\s*[:\-]?\s*(.+)$",
            r"^MÉDICO\s*[:\-]?\s*(.+)$",
            r"^DR\.?\s*(.+)$",
            r"^DRA\.?\s*(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, line_clean, flags=re.IGNORECASE)

            if match:
                name = match.group(1).strip()
                name = re.split(
                    r"\bCRM\b|\bCPF\b|\bPACIENTE\b",
                    name,
                    flags=re.IGNORECASE,
                )[0].strip()
                return name.upper()

    return None


def extract_patient_name(text: str) -> str | None:
    """
    Extrai nome do paciente em padrões simples.
    """
    match = re.search(r"PACIENTE\s*[:\-]?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ ]+)", text, flags=re.IGNORECASE)

    if not match:
        return None

    name = match.group(1).strip()
    name = re.split(r"\n|CPF|CRM|VALOR", name, flags=re.IGNORECASE)[0].strip()

    return name.upper()


def build_recibo_medico_extraction(input_path: str, text: str) -> dict:
    """
    Cria extração estruturada simples para recibo médico.

    Esta função segue o contrato esperado por validate_extracted.py.
    Campos não encontrados são incluídos com confidence low para revisão humana.
    """
    valor_centavos = parse_money_to_cents(text)
    cpf_declarante = extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE")
    cpf_profissional = extract_labeled_cpf_from_text(text, "CPF DO PROFISSIONAL") or extract_cpf_from_text(text)
    data_nascimento = extract_date_by_label(text, "DATA DE NASCIMENTO")
    data_pagamento = extract_date_by_label(text, "DATA DO PAGAMENTO")
    nome_profissional = extract_professional_name(text)
    nome_paciente = extract_patient_name(text)

    fields = {
        "cpf_declarante": {
            "value": cpf_declarante,
            "confidence": "medium" if cpf_declarante else "low",
            "source_hint": "Extraído da linha CPF DO DECLARANTE, quando disponível.",
        },
        "nome_declarante": {
            "value": nome_paciente,
            "confidence": "medium" if nome_paciente else "low",
            "source_hint": "Extraído da linha do paciente, quando disponível.",
        },
        "data_nascimento": {
            "value": data_nascimento,
            "confidence": "medium" if data_nascimento else "low",
            "source_hint": "Extraído da linha DATA DE NASCIMENTO, quando disponível.",
        },
        "cpf_cnpj_prestador": {
            "value": cpf_profissional,
            "confidence": "medium" if cpf_profissional else "low",
            "source_hint": "Extraído da linha CPF DO PROFISSIONAL, quando disponível.",
        },
        "nome_prestador": {
            "value": nome_profissional,
            "confidence": "medium" if nome_profissional else "low",
            "source_hint": "Extraído da linha iniciada por MEDICO, MÉDICO, DR ou DRA.",
        },
        "valor_pago": {
            "value": valor_centavos,
            "confidence": "medium" if valor_centavos is not None else "low",
            "source_hint": "Extraído do primeiro valor monetário encontrado no texto.",
        },
        "data_pagamento": {
            "value": data_pagamento,
            "confidence": "medium" if data_pagamento else "low",
            "source_hint": "Extraído da linha DATA DO PAGAMENTO, quando disponível.",
        },
        "descricao": {
            "value": "CONSULTA MEDICA",
            "confidence": "medium" if "CONSULTA" in text.upper() else "low",
            "source_hint": "Inferido a partir da ocorrência de CONSULTA no texto.",
        },
    }

    requires_review = []

    for field_name, field_data in fields.items():
        if field_data["value"] in {None, ""}:
            requires_review.append(
                {
                    "field": field_name,
                    "reason": "Campo não extraído automaticamente.",
                }
            )

        if field_data["confidence"] == "low":
            requires_review.append(
                {
                    "field": field_name,
                    "reason": "Campo com baixa confiança.",
                }
            )

    return {
        "source_file": input_path,
        "document_type": "recibo_medico",
        "fields": fields,
        "requires_review": requires_review,
    }


def build_structured_extraction(input_path: str) -> dict:
    """
    Classifica o texto extraído e cria extração estruturada quando suportado.
    """
    path = Path(input_path)
    text = path.read_text(encoding="utf-8")

    classification = classify_document_text(text)
    document_type = classification["document_type"]

    if document_type == "recibo_medico":
        extraction = build_recibo_medico_extraction(str(path), text)
    else:
        extraction = {
            "source_file": str(path),
            "document_type": document_type,
            "fields": {},
            "requires_review": [
                {
                    "field": "document_type",
                    "reason": "Extração estruturada automática ainda não implementada para este tipo.",
                }
            ],
        }

    return {
        "input_path": str(path),
        "classification": classification,
        "extraction": extraction,
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def parse_args(argv: list[str]) -> tuple[str, str | None, bool]:
    """
    Uso:
        python3 tools/extract_structured_from_text.py arquivo.txt
        python3 tools/extract_structured_from_text.py arquivo.txt --json
        python3 tools/extract_structured_from_text.py arquivo.txt output.json
        python3 tools/extract_structured_from_text.py arquivo.txt output.json --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/extract_structured_from_text.py arquivo.txt")
        print("python3 tools/extract_structured_from_text.py arquivo.txt --json")
        print("python3 tools/extract_structured_from_text.py arquivo.txt output.json")
        print("python3 tools/extract_structured_from_text.py arquivo.txt output.json --json")
        sys.exit(1)

    input_path = argv[1]
    args = argv[2:]

    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    output_path = args[0] if args else None

    if len(args) > 1:
        print("Uso inválido.")
        sys.exit(1)

    return input_path, output_path, print_json


def main() -> None:
    input_path, output_path, should_print_json = parse_args(sys.argv)

    response = build_structured_extraction(input_path)

    if output_path:
        save_json(response["extraction"], output_path)

    if should_print_json or not output_path:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("Extração estruturada gerada.")
        print(f"Entrada: {input_path}")
        print(f"Saída: {output_path}")
        print(f"document_type: {response['extraction']['document_type']}")
        print(f"requires_review: {len(response['extraction']['requires_review'])}")


if __name__ == "__main__":
    main()