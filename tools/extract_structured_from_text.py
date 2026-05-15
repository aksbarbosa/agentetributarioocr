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
    1.250,50 -> 125050
    """
    match = re.search(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*|\d+),(\d{2})", text)

    if not match:
        return None

    reais = match.group(1).replace(".", "")
    centavos = match.group(2)

    return int(reais) * 100 + int(centavos)


def parse_money_by_label(text: str, label: str) -> int | None:
    """
    Extrai valor monetário associado a um rótulo específico.
    """
    pattern = rf"{label}\s*[:\-]?\s*(?:R\$\s*)?(\d{{1,3}}(?:\.\d{{3}})*|\d+),(\d{{2}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    reais = match.group(1).replace(".", "")
    centavos = match.group(2)

    return int(reais) * 100 + int(centavos)


def parse_all_money_to_cents(text: str) -> list[int]:
    """
    Extrai todos os valores monetários com R$ do texto e converte para centavos.
    """
    values = []

    money_pattern = re.compile(
        r"R\$\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:,(\d{2}))?",
        flags=re.IGNORECASE,
    )

    for match in money_pattern.finditer(text):
        reais = match.group(1).replace(".", "")
        centavos = match.group(2) or "00"

        try:
            values.append(int(reais) * 100 + int(centavos))
        except ValueError:
            continue

    return values


def parse_total_money_from_text(text: str) -> int | None:
    """
    Tenta extrair o valor total do documento.
    """
    values = parse_all_money_to_cents(text)

    if values:
        return max(values)

    return parse_money_to_cents(text)


def extract_cpf_from_text(text: str) -> str | None:
    """
    Extrai o primeiro CPF encontrado no texto.
    """
    match = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", text)

    if not match:
        return None

    return only_digits(match.group(0))


def extract_first_cpf_from_text(text: str) -> str | None:
    """
    Extrai o primeiro CPF encontrado no texto, tolerando OCR com vírgula/espaço.
    """
    match = re.search(
        r"\b\d{3}\.?\d{3}[,.]?\s*\d{3}-?\d{2}\b",
        text,
        flags=re.IGNORECASE,
    )

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


def extract_cnpj_by_label(text: str, label: str) -> str | None:
    """
    Extrai CNPJ associado a um rótulo específico.
    """
    pattern = rf"{label}\s*[:\-]?\s*(\d{{2}}\.?\d{{3}}\.?\d{{3}}\/?\d{{4}}-?\d{{2}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return only_digits(match.group(1))


def extract_first_cnpj_from_text(text: str) -> str | None:
    """
    Extrai o primeiro CNPJ encontrado no texto.
    """
    match = re.search(
        r"\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return only_digits(match.group(0))


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


def extract_year_by_label(text: str, label: str) -> str | None:
    """
    Extrai ano com 4 dígitos associado a um rótulo específico.
    """
    pattern = rf"{label}\s*[:\-]?\s*(\d{{4}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(1)


def extract_labeled_text_from_line(text: str, label: str) -> str | None:
    """
    Extrai texto associado a um rótulo em uma linha.
    """
    pattern = rf"^{label}\s*[:\-]?\s*(.+)$"

    for line in text.splitlines():
        line_clean = line.strip()

        if not line_clean:
            continue

        match = re.search(pattern, line_clean, flags=re.IGNORECASE)

        if match:
            value = match.group(1).strip()
            return value.upper()

    return None


def extract_value_after_label(text: str, label: str) -> str | None:
    """
    Extrai o valor da linha seguinte a um rótulo.

    Exemplo:
    Nome do Paciente
    Ana Silva
    """
    lines = [line.strip() for line in text.splitlines()]

    for index, line in enumerate(lines):
        if re.fullmatch(label, line, flags=re.IGNORECASE):
            for next_line in lines[index + 1:]:
                if next_line:
                    return next_line.upper()

    return None


def extract_date_after_label(text: str, label: str) -> str | None:
    """
    Extrai data da linha seguinte a um rótulo.
    """
    value = extract_value_after_label(text, label)

    if not value:
        return None

    match = re.search(r"\d{2}[\/\-]?\d{2}[\/\-]?\d{4}", value)

    if not match:
        return None

    return only_digits(match.group(0))


def extract_numeric_text_by_label(text: str, label: str) -> str | None:
    """
    Extrai texto numérico associado a um rótulo.
    """
    pattern = rf"{label}\s*[:\-]?\s*([0-9]+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(1)


def extract_cep_by_label(text: str, label: str) -> str | None:
    """
    Extrai CEP associado a um rótulo.
    """
    pattern = rf"{label}\s*[:\-]?\s*(\d{{5}}-?\d{{3}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return only_digits(match.group(1))


def extract_uf_by_label(text: str, label: str) -> str | None:
    """
    Extrai UF com 2 letras.
    """
    pattern = rf"{label}\s*[:\-]?\s*([A-Z]{{2}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(1).upper()


def extract_crm_from_text(text: str) -> str | None:
    """
    Extrai CRM simples do texto.
    """
    match = re.search(
        r"\bCRM\s*[:\-]?\s*([A-Z]{2}\s*)?\d{3,10}\b",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(0).strip().upper()


def extract_professional_name(text: str) -> str | None:
    """
    Extrai nome do profissional em padrões simples.
    """
    name_after_label = (
        extract_value_after_label(text, r"Nome do Médico")
        or extract_value_after_label(text, r"Nome do Medico")
    )

    if name_after_label:
        return name_after_label

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
    name_after_label = extract_value_after_label(text, r"Nome do Paciente")

    if name_after_label:
        return name_after_label

    match = re.search(
        r"PACIENTE\s*[:\-]?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ ]+)",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    name = match.group(1).strip()
    name = re.split(r"\n|CPF|CRM|VALOR", name, flags=re.IGNORECASE)[0].strip()

    return name.upper()


def extract_vehicle_plate(text: str) -> str | None:
    """
    Extrai placa de veículo nos padrões antigo ou Mercosul.
    """
    match = re.search(r"\b[A-Z]{3}[0-9][A-Z0-9][0-9]{2}\b", text, flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(0).upper()


def extract_renavam(text: str) -> str | None:
    """
    Extrai RENAVAM com 9 a 11 dígitos.
    """
    match = re.search(r"RENAVAM\s*[:\-]?\s*(\d{9,11})", text, flags=re.IGNORECASE)

    if not match:
        return None

    return only_digits(match.group(1))


def extract_unimed_operator_name(text: str) -> str | None:
    """
    Extrai nome da operadora em notas fiscais de plano de saúde,
    especialmente quando aparece como Nome/Razão Social.
    """
    lines = [line.strip() for line in text.splitlines()]

    for line in lines:
        match = re.search(
            r"Nome/Razão Social\s*:\s*(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if match:
            value = match.group(1).strip()
            if value:
                return value.upper()

    for line in lines:
        if "UNIMED" in line.upper():
            return line.strip().upper()

    return None


def extract_informe_pagador(text: str) -> tuple[str | None, str | None]:
    """
    Extrai CNPJ e nome da fonte pagadora em informe de rendimentos.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        cnpj_match = re.search(
            r"(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})\s+(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if cnpj_match:
            cnpj = only_digits(cnpj_match.group(1))
            nome = cnpj_match.group(2).strip().upper()
            return cnpj, nome

    return None, None


def extract_informe_beneficiario(text: str) -> tuple[str | None, str | None]:
    """
    Extrai CPF e nome do beneficiário em informe de rendimentos.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        cpf_match = re.search(
            r"(\d{3}\.?\d{3}[,.]?\s*\d{3}-?\d{2})\s+(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if cpf_match:
            cpf = only_digits(cpf_match.group(1))
            nome = cpf_match.group(2).strip().upper()
            return cpf, nome

    return None, None


def extract_line_containing(text: str, keywords: list[str]) -> str | None:
    """
    Retorna a primeira linha que contém alguma das palavras-chave.
    """
    for line in text.splitlines():
        clean = line.strip()

        if not clean:
            continue

        upper = clean.upper()

        for keyword in keywords:
            if keyword.upper() in upper:
                return clean.upper()

    return None


def extract_area_util(text: str) -> str | None:
    """
    Extrai área útil em textos de matrícula de imóvel.
    """
    match = re.search(
        r"ÁREA\s+ÚTIL\s+PRIVATIVA\s+DE\s+([\d\.,]+)\s*M",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        match = re.search(
            r"AREA\s+UTIL\s+PRIVATIVA\s+DE\s+([\d\.,]+)\s*M",
            text,
            flags=re.IGNORECASE,
        )

    if not match:
        match = re.search(
            r"ÁREA\s+ÚTIL\s+.*?DE\s+([\d\.,]+)\s*M",
            text,
            flags=re.IGNORECASE,
        )

    if not match:
        return None

    return match.group(1).replace(",", ".").strip()


def extract_area_total(text: str) -> str | None:
    """
    Extrai área total em textos de matrícula de imóvel.
    """
    match = re.search(
        r"ÁREA\s+TOTAL\s+DE\s+([\d\.,]+)\s*M",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        match = re.search(
            r"AREA\s+TOTAL\s+DE\s+([\d\.,]+)\s*M",
            text,
            flags=re.IGNORECASE,
        )

    if not match:
        return None

    return match.group(1).replace(",", ".").strip()


def extract_fracao_ideal(text: str) -> str | None:
    """
    Extrai fração ideal em textos de matrícula.
    """
    match = re.search(
        r"FRA[CÇ][AÃ]O\s+IDEAL\s+DE\s+([\d\.,]+)\s*%",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1).replace(",", ".").strip()


def build_matricula_imovel_description(text: str) -> str | None:
    """
    Monta descrição para matrícula antiga de imóvel quando não há campos
    estruturados como logradouro, CEP, IPTU e valor.
    """
    upper = text.upper()

    is_matricula = (
        "UNIDADE AUTÔNOMA" in upper
        or "UNIDADE AUTONOMA" in upper
        or "REGISTRO DE IMÓVEIS" in upper
        or "REGISTRO DE IMOVEIS" in upper
        or "OFICIAL DE REGISTRO DE IMÓVEIS" in upper
        or "OFICIAL DE REGISTRO DE IMOVEIS" in upper
        or "MATRÍCULA" in upper
        or "MATRICULA" in upper
    )

    if not is_matricula:
        return None

    parts = ["UNIDADE AUTONOMA CONSTANTE EM MATRICULA DE REGISTRO DE IMOVEIS"]

    if "JARDIM AMÉRICA" in upper or "JARDIM AMERICA" in upper:
        parts.append("LOCALIZADA NO 20 SUBDISTRITO JARDIM AMERICA")

    if "GARAGEM" in upper:
        parts.append("COM VAGA DE GARAGEM")

    area_util = extract_area_util(text)

    if area_util:
        parts.append(f"AREA UTIL PRIVATIVA DE {area_util} M2")

    area_total = extract_area_total(text)

    if area_total:
        parts.append(f"AREA TOTAL DE {area_total} M2")

    fracao_ideal = extract_fracao_ideal(text)

    if fracao_ideal:
        parts.append(f"FRACAO IDEAL DE {fracao_ideal}%")

    return ", ".join(parts)


def make_field(value, confidence: str, source_hint: str) -> dict:
    """
    Cria campo no formato esperado pelo validador.
    """
    return {
        "value": value,
        "confidence": confidence,
        "source_hint": source_hint,
    }


def build_requires_review(fields: dict) -> list[dict]:
    """
    Cria lista de revisão para campos ausentes ou de baixa confiança.
    """
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

    return requires_review


def build_recibo_medico_extraction(input_path: str, text: str) -> dict:
    """
    Cria extração estruturada simples para recibo médico.
    """
    valor_centavos = parse_total_money_from_text(text)

    cpf_declarante = extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE")

    cpf_profissional = (
        extract_labeled_cpf_from_text(text, "CPF DO PROFISSIONAL")
        or extract_cpf_from_text(text)
    )

    data_nascimento = extract_date_by_label(text, "DATA DE NASCIMENTO")

    data_pagamento = (
        extract_date_by_label(text, "DATA DO PAGAMENTO")
        or extract_date_by_label(text, "DATA")
        or extract_date_after_label(text, r"Data")
    )

    nome_profissional = extract_professional_name(text)
    nome_paciente = extract_patient_name(text)

    descricao_value = (
        "CONSULTA MEDICA"
        if "CONSULTA" in text.upper()
        else "SERVICOS MEDICOS"
    )

    descricao_confidence = (
        "medium"
        if (
            "CONSULTA" in text.upper()
            or "SERVIÇO" in text.upper()
            or "SERVICO" in text.upper()
            or "RECIBO MÉDICO" in text.upper()
            or "RECIBO MEDICO" in text.upper()
        )
        else "low"
    )

    fields = {
        "cpf_declarante": make_field(
            cpf_declarante,
            "medium" if cpf_declarante else "low",
            "Extraído da linha CPF DO DECLARANTE, quando disponível.",
        ),
        "nome_declarante": make_field(
            nome_paciente,
            "medium" if nome_paciente else "low",
            "Extraído da linha do paciente, quando disponível.",
        ),
        "data_nascimento": make_field(
            data_nascimento,
            "medium" if data_nascimento else "low",
            "Extraído da linha DATA DE NASCIMENTO, quando disponível.",
        ),
        "cpf_cnpj_prestador": make_field(
            cpf_profissional,
            "medium" if cpf_profissional else "low",
            "Extraído da linha CPF DO PROFISSIONAL, quando disponível.",
        ),
        "nome_prestador": make_field(
            nome_profissional,
            "medium" if nome_profissional else "low",
            "Extraído da linha iniciada por MEDICO, MÉDICO, DR, DRA ou Nome do Médico.",
        ),
        "valor_pago": make_field(
            valor_centavos,
            "medium" if valor_centavos is not None else "low",
            "Extraído do valor total do recibo, quando disponível.",
        ),
        "data_pagamento": make_field(
            data_pagamento,
            "medium" if data_pagamento else "low",
            "Extraído da linha DATA DO PAGAMENTO ou DATA, quando disponível.",
        ),
        "descricao": make_field(
            descricao_value,
            descricao_confidence,
            "Inferido a partir de CONSULTA, SERVIÇO/SERVICO ou RECIBO MEDICO no texto.",
        ),
    }

    return {
        "source_file": input_path,
        "document_type": "recibo_medico",
        "fields": fields,
        "requires_review": build_requires_review(fields),
    }


def build_informe_rendimentos_pj_extraction(input_path: str, text: str) -> dict:
    """
    Cria extração estruturada simples para informe de rendimentos PJ.
    """
    cnpj_pagador_extraido, nome_pagador_extraido = extract_informe_pagador(text)
    cpf_beneficiario_extraido, nome_beneficiario_extraido = extract_informe_beneficiario(text)

    cpf_declarante = (
        extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE")
        or cpf_beneficiario_extraido
        or extract_first_cpf_from_text(text)
    )

    nome_declarante = (
        extract_labeled_text_from_line(text, "DECLARANTE")
        or nome_beneficiario_extraido
    )

    data_nascimento = extract_date_by_label(text, "DATA DE NASCIMENTO")

    nome_pagador = (
        extract_labeled_text_from_line(text, "FONTE PAGADORA")
        or extract_labeled_text_from_line(text, "PAGADOR")
        or extract_labeled_text_from_line(text, "EMPRESA")
        or nome_pagador_extraido
    )

    cnpj_pagador = (
        extract_cnpj_by_label(text, "CNPJ DA FONTE PAGADORA")
        or extract_cnpj_by_label(text, "CNPJ DO PAGADOR")
        or extract_cnpj_by_label(text, "CNPJ")
        or cnpj_pagador_extraido
        or extract_first_cnpj_from_text(text)
    )

    rendimento_total = (
        parse_money_by_label(text, "RENDIMENTOS TRIBUTAVEIS")
        or parse_money_by_label(text, "RENDIMENTOS TRIBUTÁVEIS")
        or parse_money_by_label(text, "TOTAL DOS RENDIMENTOS")
    )

    previdencia_oficial = (
        parse_money_by_label(text, "PREVIDENCIA OFICIAL")
        or parse_money_by_label(text, "PREVIDÊNCIA OFICIAL")
    )

    irrf = (
        parse_money_by_label(text, "IMPOSTO DE RENDA RETIDO NA FONTE")
        or parse_money_by_label(text, "IMPOSTO SOBRE A RENDA RETIDO NA FONTE")
        or parse_money_by_label(text, "IRRF")
    )

    decimo_terceiro = (
        parse_money_by_label(text, "DECIMO TERCEIRO SALARIO")
        or parse_money_by_label(text, "DÉCIMO TERCEIRO SALÁRIO")
        or parse_money_by_label(text, "13")
    )

    irrf_13 = (
        parse_money_by_label(text, "IRRF SOBRE DECIMO TERCEIRO")
        or parse_money_by_label(text, "IRRF SOBRE DÉCIMO TERCEIRO")
        or parse_money_by_label(text, "IRRF SOBRE 13")
    )

    fields = {
        "cpf_declarante": make_field(
            cpf_declarante,
            "medium" if cpf_declarante else "low",
            "Extraído da área de beneficiário ou linha CPF DO DECLARANTE.",
        ),
        "nome_declarante": make_field(
            nome_declarante,
            "medium" if nome_declarante else "low",
            "Extraído da área de beneficiário ou linha DECLARANTE.",
        ),
        "data_nascimento": make_field(
            data_nascimento,
            "medium" if data_nascimento else "low",
            "Extraído da linha DATA DE NASCIMENTO, quando disponível.",
        ),
        "nome_pagador": make_field(
            nome_pagador,
            "medium" if nome_pagador else "low",
            "Extraído da área Fonte Pagadora, FONTE PAGADORA, PAGADOR ou EMPRESA.",
        ),
        "cnpj_pagador": make_field(
            cnpj_pagador,
            "medium" if cnpj_pagador else "low",
            "Extraído da área Fonte Pagadora ou linha CNPJ.",
        ),
        "rendimento_total": make_field(
            rendimento_total,
            "medium" if rendimento_total is not None else "low",
            "Extraído da linha RENDIMENTOS TRIBUTAVEIS/TOTAL DOS RENDIMENTOS.",
        ),
        "previdencia_oficial": make_field(
            previdencia_oficial,
            "medium" if previdencia_oficial is not None else "low",
            "Extraído da linha PREVIDENCIA OFICIAL.",
        ),
        "decimo_terceiro": make_field(
            decimo_terceiro,
            "medium" if decimo_terceiro is not None else "low",
            "Extraído da linha DECIMO TERCEIRO SALARIO.",
        ),
        "irrf": make_field(
            irrf,
            "medium" if irrf is not None else "low",
            "Extraído da linha IMPOSTO DE RENDA RETIDO NA FONTE ou IRRF.",
        ),
        "irrf_13": make_field(
            irrf_13,
            "medium" if irrf_13 is not None else "low",
            "Extraído da linha IRRF SOBRE DECIMO TERCEIRO.",
        ),
    }

    return {
        "source_file": input_path,
        "document_type": "informe_rendimentos_pj",
        "fields": fields,
        "requires_review": build_requires_review(fields),
    }


def build_plano_saude_extraction(input_path: str, text: str) -> dict:
    """
    Cria extração estruturada simples para plano de saúde.

    Também cobre notas fiscais de coparticipação de operadora,
    como documentos da Unimed.
    """
    cpf_declarante = extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE")
    nome_declarante = extract_labeled_text_from_line(text, "DECLARANTE")
    data_nascimento = extract_date_by_label(text, "DATA DE NASCIMENTO")

    nome_operadora = (
        extract_labeled_text_from_line(text, "OPERADORA")
        or extract_labeled_text_from_line(text, "PLANO DE SAUDE")
        or extract_labeled_text_from_line(text, "PLANO DE SAÚDE")
        or extract_unimed_operator_name(text)
    )

    cnpj_operadora = (
        extract_cnpj_by_label(text, "CNPJ DA OPERADORA")
        or extract_cnpj_by_label(text, "CNPJ DO PLANO")
        or extract_cnpj_by_label(text, "CNPJ/CPF")
        or extract_cnpj_by_label(text, "CNPJ")
        or extract_first_cnpj_from_text(text)
    )

    valor_pago = (
        parse_money_by_label(text, "VALOR PAGO")
        or parse_money_by_label(text, "TOTAL PAGO")
        or parse_money_by_label(text, "VALOR TOTAL DA NOTA FISCAL")
        or parse_money_by_label(text, "VALOR LÍQUIDO DA NOTA FISCAL")
        or parse_money_by_label(text, "VALOR LIQUIDO DA NOTA FISCAL")
        or parse_money_by_label(text, "VALOR TOTAL")
    )

    valor_nao_dedutivel = (
        parse_money_by_label(text, "VALOR NAO DEDUTIVEL")
        or parse_money_by_label(text, "VALOR NÃO DEDUTÍVEL")
        or parse_money_by_label(text, "PARCELA NAO DEDUTIVEL")
        or parse_money_by_label(text, "PARCELA NÃO DEDUTÍVEL")
    )

    if valor_nao_dedutivel is None:
        valor_nao_dedutivel = 0

    upper = text.upper()

    if "COPARTICIPACAO" in upper or "COPARTICIPAÇÃO" in upper:
        descricao_value = "COPARTICIPACAO"
    elif "PLANOS DE SAUDE" in upper or "PLANOS DE SAÚDE" in upper:
        descricao_value = "PLANO DE SAUDE"
    else:
        descricao_value = "PLANO DE SAUDE"

    fields = {
        "cpf_declarante": make_field(
            cpf_declarante,
            "medium" if cpf_declarante else "low",
            "Extraído da linha CPF DO DECLARANTE, quando disponível.",
        ),
        "nome_declarante": make_field(
            nome_declarante,
            "medium" if nome_declarante else "low",
            "Extraído da linha DECLARANTE, quando disponível.",
        ),
        "data_nascimento": make_field(
            data_nascimento,
            "medium" if data_nascimento else "low",
            "Extraído da linha DATA DE NASCIMENTO, quando disponível.",
        ),
        "nome_operadora": make_field(
            nome_operadora,
            "medium" if nome_operadora else "low",
            "Extraído da linha OPERADORA, PLANO DE SAUDE ou Nome/Razão Social.",
        ),
        "cnpj_operadora": make_field(
            cnpj_operadora,
            "medium" if cnpj_operadora else "low",
            "Extraído da linha CNPJ DA OPERADORA, CNPJ DO PLANO ou CNPJ/CPF.",
        ),
        "valor_pago": make_field(
            valor_pago,
            "medium" if valor_pago is not None else "low",
            "Extraído da linha VALOR PAGO, VALOR TOTAL DA NOTA FISCAL ou VALOR LÍQUIDO DA NOTA FISCAL.",
        ),
        "valor_nao_dedutivel": make_field(
            valor_nao_dedutivel,
            "medium",
            "Extraído da linha VALOR NAO DEDUTIVEL ou assumido como 0 quando ausente.",
        ),
        "descricao": make_field(
            descricao_value,
            "medium",
            "Inferido a partir de COPARTICIPACAO, PLANOS DE SAUDE ou tipo do documento.",
        ),
    }

    return {
        "source_file": input_path,
        "document_type": "plano_saude",
        "fields": fields,
        "requires_review": build_requires_review(fields),
    }


def build_bem_veiculo_extraction(input_path: str, text: str) -> dict:
    """
    Cria extração estruturada simples para bem veículo.
    """
    cpf_declarante = extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE")
    nome_declarante = extract_labeled_text_from_line(text, "DECLARANTE")
    data_nascimento = extract_date_by_label(text, "DATA DE NASCIMENTO")

    marca = extract_labeled_text_from_line(text, "MARCA")
    modelo = extract_labeled_text_from_line(text, "MODELO")
    veiculo = (
        extract_labeled_text_from_line(text, "VEICULO")
        or extract_labeled_text_from_line(text, "VEÍCULO")
    )

    ano_fabricacao = (
        extract_year_by_label(text, "ANO FABRICACAO")
        or extract_year_by_label(text, "ANO FABRICAÇÃO")
        or extract_year_by_label(text, "ANO")
    )

    placa = extract_labeled_text_from_line(text, "PLACA") or extract_vehicle_plate(text)
    renavam = extract_renavam(text)

    data_aquisicao = (
        extract_date_by_label(text, "DATA DE AQUISICAO")
        or extract_date_by_label(text, "DATA DE AQUISIÇÃO")
    )

    valor_anterior = parse_money_by_label(text, "VALOR ANTERIOR")
    valor_atual = (
        parse_money_by_label(text, "VALOR ATUAL")
        or parse_money_by_label(text, "VALOR DO BEM")
        or parse_money_by_label(text, "VALOR")
    )

    descricao_value = None

    if veiculo:
        descricao_value = veiculo
    elif marca and modelo:
        descricao_value = f"{marca} {modelo}"
    elif marca:
        descricao_value = marca

    if descricao_value and ano_fabricacao and placa:
        descricao_value = f"Automóvel marca/modelo {descricao_value}, ano {ano_fabricacao}, placa {placa}"

    fields = {
        "cpf_declarante": make_field(
            cpf_declarante,
            "medium" if cpf_declarante else "low",
            "Extraído da linha CPF DO DECLARANTE, quando disponível.",
        ),
        "nome_declarante": make_field(
            nome_declarante,
            "medium" if nome_declarante else "low",
            "Extraído da linha DECLARANTE, quando disponível.",
        ),
        "data_nascimento": make_field(
            data_nascimento,
            "medium" if data_nascimento else "low",
            "Extraído da linha DATA DE NASCIMENTO, quando disponível.",
        ),
        "grupo_bem": make_field(
            "02",
            "medium",
            "Inferido como grupo 02 para bens móveis.",
        ),
        "codigo_bem": make_field(
            "01",
            "medium",
            "Inferido como código 01 para veículo automotor terrestre.",
        ),
        "descricao": make_field(
            descricao_value,
            "medium" if descricao_value else "low",
            "Construído a partir de VEICULO, MARCA, MODELO, ANO e PLACA.",
        ),
        "valor_anterior": make_field(
            valor_anterior,
            "medium" if valor_anterior is not None else "low",
            "Extraído da linha VALOR ANTERIOR, quando disponível.",
        ),
        "valor_atual": make_field(
            valor_atual,
            "medium" if valor_atual is not None else "low",
            "Extraído da linha VALOR ATUAL, VALOR DO BEM ou VALOR.",
        ),
        "renavam": make_field(
            renavam,
            "medium" if renavam else "low",
            "Extraído da linha RENAVAM.",
        ),
        "placa": make_field(
            placa,
            "medium" if placa else "low",
            "Extraído da linha PLACA ou por padrão de placa.",
        ),
        "marca": make_field(
            marca,
            "medium" if marca else "low",
            "Extraído da linha MARCA.",
        ),
        "modelo": make_field(
            modelo,
            "medium" if modelo else "low",
            "Extraído da linha MODELO.",
        ),
        "ano_fabricacao": make_field(
            ano_fabricacao,
            "medium" if ano_fabricacao else "low",
            "Extraído da linha ANO FABRICACAO, ANO FABRICAÇÃO ou ANO.",
        ),
        "data_aquisicao": make_field(
            data_aquisicao,
            "medium" if data_aquisicao else "low",
            "Extraído da linha DATA DE AQUISICAO ou DATA DE AQUISIÇÃO.",
        ),
    }

    return {
        "source_file": input_path,
        "document_type": "bem_veiculo",
        "fields": fields,
        "requires_review": build_requires_review(fields),
    }


def build_bem_imovel_extraction(input_path: str, text: str) -> dict:
    """
    Cria extração estruturada simples para bem imóvel.

    Também cobre matrículas antigas de registro de imóveis quando não há
    campos fiscais completos como CEP, IPTU, valor do bem etc.
    """
    cpf_declarante = extract_labeled_cpf_from_text(text, "CPF DO DECLARANTE")
    nome_declarante = extract_labeled_text_from_line(text, "DECLARANTE")
    data_nascimento = extract_date_by_label(text, "DATA DE NASCIMENTO")

    imovel = (
        extract_labeled_text_from_line(text, "IMOVEL")
        or extract_labeled_text_from_line(text, "IMÓVEL")
    )

    matricula = (
        extract_numeric_text_by_label(text, "MATRICULA")
        or extract_numeric_text_by_label(text, "MATRÍCULA")
    )

    iptu = (
        extract_numeric_text_by_label(text, "IPTU")
        or extract_numeric_text_by_label(text, "INSCRICAO IMOBILIARIA")
        or extract_numeric_text_by_label(text, "INSCRIÇÃO IMOBILIÁRIA")
        or extract_numeric_text_by_label(text, "NUMERO DO CONTRIBUINTE")
        or extract_numeric_text_by_label(text, "NÚMERO DO CONTRIBUINTE")
    )

    data_aquisicao = (
        extract_date_by_label(text, "DATA DE AQUISICAO")
        or extract_date_by_label(text, "DATA DE AQUISIÇÃO")
    )

    logradouro = extract_labeled_text_from_line(text, "LOGRADOURO")
    numero = (
        extract_numeric_text_by_label(text, "NUMERO")
        or extract_numeric_text_by_label(text, "NÚMERO")
    )
    bairro = extract_labeled_text_from_line(text, "BAIRRO")
    municipio = (
        extract_labeled_text_from_line(text, "MUNICIPIO")
        or extract_labeled_text_from_line(text, "MUNICÍPIO")
        or extract_labeled_text_from_line(text, "CIDADE")
    )
    uf = extract_uf_by_label(text, "UF")
    cep = extract_cep_by_label(text, "CEP")

    valor_anterior = parse_money_by_label(text, "VALOR ANTERIOR")
    valor_atual = (
        parse_money_by_label(text, "VALOR ATUAL")
        or parse_money_by_label(text, "VALOR DO BEM")
        or parse_money_by_label(text, "VALOR")
    )

    descricao_parts = []

    if imovel:
        descricao_parts.append(imovel)

    if logradouro:
        descricao_parts.append(f"localizado em {logradouro}")

    if numero:
        descricao_parts.append(f"número {numero}")

    if bairro:
        descricao_parts.append(f"bairro {bairro}")

    if municipio:
        descricao_parts.append(municipio)

    if uf:
        descricao_parts.append(uf)

    descricao_value = ", ".join(descricao_parts) if descricao_parts else None

    if not descricao_value:
        descricao_value = build_matricula_imovel_description(text)

    fields = {
        "cpf_declarante": make_field(
            cpf_declarante,
            "medium" if cpf_declarante else "low",
            "Extraído da linha CPF DO DECLARANTE, quando disponível.",
        ),
        "nome_declarante": make_field(
            nome_declarante,
            "medium" if nome_declarante else "low",
            "Extraído da linha DECLARANTE, quando disponível.",
        ),
        "data_nascimento": make_field(
            data_nascimento,
            "medium" if data_nascimento else "low",
            "Extraído da linha DATA DE NASCIMENTO, quando disponível.",
        ),
        "codigo_bem": make_field(
            "11",
            "medium",
            "Inferido como código 11 para apartamento/imóvel residencial.",
        ),
        "grupo_bem": make_field(
            "01",
            "medium",
            "Inferido como grupo 01 para bens imóveis.",
        ),
        "descricao": make_field(
            descricao_value,
            "medium" if descricao_value else "low",
            "Construído a partir de endereço ou, quando ausente, de matrícula/registro de imóveis.",
        ),
        "valor_anterior": make_field(
            valor_anterior,
            "medium" if valor_anterior is not None else "low",
            "Extraído da linha VALOR ANTERIOR, quando disponível.",
        ),
        "valor_atual": make_field(
            valor_atual,
            "medium" if valor_atual is not None else "low",
            "Extraído da linha VALOR ATUAL, VALOR DO BEM ou VALOR.",
        ),
        "cep": make_field(
            cep,
            "medium" if cep else "low",
            "Extraído da linha CEP.",
        ),
        "logradouro": make_field(
            logradouro,
            "medium" if logradouro else "low",
            "Extraído da linha LOGRADOURO.",
        ),
        "numero": make_field(
            numero,
            "medium" if numero else "low",
            "Extraído da linha NUMERO/NÚMERO.",
        ),
        "bairro": make_field(
            bairro,
            "medium" if bairro else "low",
            "Extraído da linha BAIRRO.",
        ),
        "municipio": make_field(
            municipio,
            "medium" if municipio else "low",
            "Extraído da linha MUNICIPIO/MUNICÍPIO/CIDADE.",
        ),
        "uf": make_field(
            uf,
            "medium" if uf else "low",
            "Extraído da linha UF.",
        ),
        "iptu": make_field(
            iptu,
            "medium" if iptu else "low",
            "Extraído da linha IPTU, INSCRICAO IMOBILIARIA ou NUMERO DO CONTRIBUINTE.",
        ),
        "matricula": make_field(
            matricula,
            "medium" if matricula else "low",
            "Extraído da linha MATRICULA/MATRÍCULA.",
        ),
        "data_aquisicao": make_field(
            data_aquisicao,
            "medium" if data_aquisicao else "low",
            "Extraído da linha DATA DE AQUISICAO/DATA DE AQUISIÇÃO.",
        ),
    }

    return {
        "source_file": input_path,
        "document_type": "bem_imovel",
        "fields": fields,
        "requires_review": build_requires_review(fields),
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

    elif document_type == "informe_rendimentos_pj":
        extraction = build_informe_rendimentos_pj_extraction(str(path), text)

    elif document_type == "plano_saude":
        extraction = build_plano_saude_extraction(str(path), text)

    elif document_type == "bem_veiculo":
        extraction = build_bem_veiculo_extraction(str(path), text)

    elif document_type == "bem_imovel":
        extraction = build_bem_imovel_extraction(str(path), text)

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