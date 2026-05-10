import json
import sys
from pathlib import Path

from normalize import (
    only_digits,
    normalize_name,
    normalize_date,
    money_to_cents,
)


def load_json(path: str) -> dict:
    """
    Carrega um arquivo JSON.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data: dict, path: str) -> None:
    """
    Salva um dicionário como JSON formatado.
    """
    file_path = Path(path)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_field(extracted: dict, field_name: str, default=None):
    """
    Busca o valor bruto de um campo extraído.
    """
    fields = extracted.get("fields", {})
    field = fields.get(field_name)

    if not field:
        return default

    return field.get("value", default)


def get_field_meta(extracted: dict, field_name: str) -> dict:
    """
    Busca metadados de um campo extraído.
    """
    fields = extracted.get("fields", {})
    field = fields.get(field_name)

    if not field:
        return {
            "confidence": "missing",
            "source_hint": ""
        }

    return {
        "confidence": field.get("confidence", "missing"),
        "source_hint": field.get("source_hint", "")
    }


def build_review_items(extracted: dict, required_fields: list[str]) -> list[dict]:
    """
    Cria pendências de revisão para campos com baixa confiança
    ou campos ausentes.
    """
    requires_review = []

    for field_name in required_fields:
        meta = get_field_meta(extracted, field_name)

        if meta["confidence"] == "missing":
            requires_review.append({
                "field": field_name,
                "reason": "Campo ausente na extração.",
                "source_hint": meta["source_hint"]
            })

        elif meta["confidence"] == "low":
            requires_review.append({
                "field": field_name,
                "reason": "Campo extraído com baixa confiança.",
                "source_hint": meta["source_hint"]
            })

    return requires_review


def build_base_canonical(extracted: dict, required_fields: list[str]) -> dict:
    """
    Cria a base comum do JSON canônico.
    """
    cpf_declarante = only_digits(get_field(extracted, "cpf_declarante", ""))
    nome_declarante = normalize_name(get_field(extracted, "nome_declarante", ""))
    data_nascimento = normalize_date(get_field(extracted, "data_nascimento", ""))

    return {
        "$schema": "irpf-2026-v1",
        "exercicio": 2026,
        "ano_calendario": 2025,
        "tipo_declaracao": "AJUSTE_ANUAL",
        "modelo": "AUTO",
        "declarante": {
            "cpf": cpf_declarante,
            "nome": nome_declarante,
            "data_nascimento": data_nascimento
        },
        "rendimentos": {
            "tributaveis_pj": []
        },
        "pagamentos": [],
        "bens": [],
        "dividas": [],
        "avisos": [],
        "requires_review": build_review_items(extracted, required_fields)
    }


def build_canonical_from_informe_pj(extracted: dict) -> dict:
    """
    Converte a saída extraída de um informe de rendimentos PJ
    para o JSON canônico mínimo.
    """
    required_fields = [
        "cpf_declarante",
        "nome_declarante",
        "data_nascimento",
        "cnpj_pagador",
        "nome_pagador",
        "rendimento_total",
        "previdencia_oficial",
        "decimo_terceiro",
        "irrf",
        "irrf_13",
    ]

    canonical = build_base_canonical(extracted, required_fields)

    rendimento = {
        "cnpj_pagador": only_digits(get_field(extracted, "cnpj_pagador", "")),
        "nome_pagador": normalize_name(get_field(extracted, "nome_pagador", "")),
        "rendimento_total": money_to_cents(get_field(extracted, "rendimento_total", 0)),
        "previdencia_oficial": money_to_cents(get_field(extracted, "previdencia_oficial", 0)),
        "decimo_terceiro": money_to_cents(get_field(extracted, "decimo_terceiro", 0)),
        "irrf": money_to_cents(get_field(extracted, "irrf", 0)),
        "irrf_13": money_to_cents(get_field(extracted, "irrf_13", 0)),
        "beneficiario": "TITULAR"
    }

    canonical["rendimentos"]["tributaveis_pj"].append(rendimento)

    return canonical


def build_canonical_from_recibo_medico(extracted: dict) -> dict:
    """
    Converte a saída extraída de um recibo médico
    para o JSON canônico mínimo.
    """
    required_fields = [
        "cpf_declarante",
        "nome_declarante",
        "data_nascimento",
        "cpf_cnpj_prestador",
        "nome_prestador",
        "valor_pago",
        "data_pagamento",
        "descricao",
    ]

    canonical = build_base_canonical(extracted, required_fields)

    pagamento = {
        "codigo": "10",
        "descricao": normalize_name(get_field(extracted, "descricao", "")),
        "beneficiario_cpf_cnpj": only_digits(get_field(extracted, "cpf_cnpj_prestador", "")),
        "beneficiario_nome": normalize_name(get_field(extracted, "nome_prestador", "")),
        "beneficiario_tipo": "T",
        "tipo_documento": 1,
        "valor_pago": money_to_cents(get_field(extracted, "valor_pago", 0)),
        "valor_nao_dedutivel": 0,
        "data_pagamento": normalize_date(get_field(extracted, "data_pagamento", ""))
    }

    canonical["pagamentos"].append(pagamento)

    return canonical


def build_canonical_from_plano_saude(extracted: dict) -> dict:
    """
    Converte a saída extraída de um informe de plano de saúde
    para o JSON canônico mínimo.
    """
    required_fields = [
        "cpf_declarante",
        "nome_declarante",
        "data_nascimento",
        "cnpj_operadora",
        "nome_operadora",
        "valor_pago",
        "valor_nao_dedutivel",
        "descricao",
    ]

    canonical = build_base_canonical(extracted, required_fields)

    pagamento = {
        "codigo": "26",
        "descricao": normalize_name(get_field(extracted, "descricao", "")),
        "beneficiario_cpf_cnpj": only_digits(get_field(extracted, "cnpj_operadora", "")),
        "beneficiario_nome": normalize_name(get_field(extracted, "nome_operadora", "")),
        "beneficiario_tipo": "T",
        "tipo_documento": 2,
        "valor_pago": money_to_cents(get_field(extracted, "valor_pago", 0)),
        "valor_nao_dedutivel": money_to_cents(get_field(extracted, "valor_nao_dedutivel", 0))
    }

    canonical["pagamentos"].append(pagamento)

    return canonical


def build_canonical_from_bem_imovel(extracted: dict) -> dict:
    """
    Converte a saída extraída de um bem imóvel
    para o JSON canônico mínimo.
    """
    required_fields = [
        "cpf_declarante",
        "nome_declarante",
        "data_nascimento",
        "codigo_bem",
        "grupo_bem",
        "descricao",
        "valor_anterior",
        "valor_atual",
        "cep",
        "logradouro",
        "numero",
        "bairro",
        "municipio",
        "uf",
        "iptu",
        "matricula",
        "data_aquisicao",
    ]

    canonical = build_base_canonical(extracted, required_fields)

    bem = {
        "tipo_bem": "IMOVEL",
        "grupo_bem": only_digits(get_field(extracted, "grupo_bem", "")),
        "codigo_bem": only_digits(get_field(extracted, "codigo_bem", "")),
        "descricao": normalize_name(get_field(extracted, "descricao", "")),
        "valor_anterior": money_to_cents(get_field(extracted, "valor_anterior", 0)),
        "valor_atual": money_to_cents(get_field(extracted, "valor_atual", 0)),
        "endereco": {
            "cep": only_digits(get_field(extracted, "cep", "")),
            "logradouro": normalize_name(get_field(extracted, "logradouro", "")),
            "numero": str(get_field(extracted, "numero", "")).strip(),
            "bairro": normalize_name(get_field(extracted, "bairro", "")),
            "municipio": normalize_name(get_field(extracted, "municipio", "")),
            "uf": normalize_name(get_field(extracted, "uf", "")),
        },
        "iptu": only_digits(get_field(extracted, "iptu", "")),
        "matricula": only_digits(get_field(extracted, "matricula", "")),
        "data_aquisicao": normalize_date(get_field(extracted, "data_aquisicao", "")),
        "beneficiario_tipo": "T"
    }

    canonical["bens"].append(bem)

    return canonical


def build_canonical_from_bem_veiculo(extracted: dict) -> dict:
    """
    Converte a saída extraída de um bem veículo
    para o JSON canônico mínimo.
    """
    required_fields = [
        "cpf_declarante",
        "nome_declarante",
        "data_nascimento",
        "grupo_bem",
        "codigo_bem",
        "descricao",
        "valor_anterior",
        "valor_atual",
        "renavam",
        "placa",
        "marca",
        "modelo",
        "ano_fabricacao",
        "data_aquisicao",
    ]

    canonical = build_base_canonical(extracted, required_fields)

    bem = {
        "tipo_bem": "VEICULO",
        "grupo_bem": only_digits(get_field(extracted, "grupo_bem", "")),
        "codigo_bem": only_digits(get_field(extracted, "codigo_bem", "")),
        "descricao": normalize_name(get_field(extracted, "descricao", "")),
        "valor_anterior": money_to_cents(get_field(extracted, "valor_anterior", 0)),
        "valor_atual": money_to_cents(get_field(extracted, "valor_atual", 0)),
        "renavam": only_digits(get_field(extracted, "renavam", "")),
        "placa": normalize_name(get_field(extracted, "placa", "")),
        "marca": normalize_name(get_field(extracted, "marca", "")),
        "modelo": normalize_name(get_field(extracted, "modelo", "")),
        "ano_fabricacao": only_digits(get_field(extracted, "ano_fabricacao", "")),
        "data_aquisicao": normalize_date(get_field(extracted, "data_aquisicao", "")),
        "beneficiario_tipo": "T"
    }

    canonical["bens"].append(bem)

    return canonical


def build_canonical_json(extracted: dict) -> dict:
    """
    Decide qual conversor usar com base no tipo do documento.
    """
    document_type = extracted.get("document_type")

    if document_type == "informe_rendimentos_pj":
        return build_canonical_from_informe_pj(extracted)

    if document_type == "recibo_medico":
        return build_canonical_from_recibo_medico(extracted)

    if document_type == "plano_saude":
        return build_canonical_from_plano_saude(extracted)

    if document_type == "bem_imovel":
        return build_canonical_from_bem_imovel(extracted)

    if document_type == "bem_veiculo":
        return build_canonical_from_bem_veiculo(extracted)

    raise ValueError(f"Tipo de documento ainda não suportado: {document_type}")


def main() -> None:
    """
    Uso:
        python3 tools/build_canonical_json.py inputs/extracted/bem_veiculo_exemplo.json bem_veiculo.canonical.json
    """
    if len(sys.argv) != 3:
        print("Uso:")
        print("python3 tools/build_canonical_json.py inputs/extracted/informe_pj_exemplo.json informe_pj.canonical.json")
        print("python3 tools/build_canonical_json.py inputs/extracted/recibo_medico_exemplo.json recibo_medico.canonical.json")
        print("python3 tools/build_canonical_json.py inputs/extracted/plano_saude_exemplo.json plano_saude.canonical.json")
        print("python3 tools/build_canonical_json.py inputs/extracted/bem_imovel_exemplo.json bem_imovel.canonical.json")
        print("python3 tools/build_canonical_json.py inputs/extracted/bem_veiculo_exemplo.json bem_veiculo.canonical.json")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    extracted = load_json(input_path)
    canonical = build_canonical_json(extracted)
    save_json(canonical, output_path)

    print(f"JSON canônico gerado em: {output_path}")


if __name__ == "__main__":
    main()