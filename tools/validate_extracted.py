import json
import sys
from pathlib import Path


VALID_CONFIDENCES = {"high", "medium", "low"}


REQUIRED_INFORME_PJ_FIELDS = [
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


REQUIRED_RECIBO_MEDICO_FIELDS = [
    "cpf_declarante",
    "nome_declarante",
    "data_nascimento",
    "cpf_cnpj_prestador",
    "nome_prestador",
    "valor_pago",
    "data_pagamento",
    "descricao",
]


REQUIRED_PLANO_SAUDE_FIELDS = [
    "cpf_declarante",
    "nome_declarante",
    "data_nascimento",
    "cnpj_operadora",
    "nome_operadora",
    "valor_pago",
    "valor_nao_dedutivel",
    "descricao",
]


REQUIRED_BEM_IMOVEL_FIELDS = [
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


REQUIRED_BEM_VEICULO_FIELDS = [
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


def load_json(path: str) -> dict:
    """
    Carrega um arquivo JSON.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_extracted_field(field_name: str, field_data: object) -> list[dict]:
    """
    Valida a estrutura de um campo extraído.

    Cada campo deve ser um objeto com:
    - value
    - confidence
    - source_hint
    """
    errors = []

    if not isinstance(field_data, dict):
        errors.append({
            "field": field_name,
            "message": "Campo extraído deve ser um objeto."
        })
        return errors

    for required_key in ["value", "confidence", "source_hint"]:
        if required_key not in field_data:
            errors.append({
                "field": f"{field_name}.{required_key}",
                "message": f"Chave obrigatória ausente: {required_key}."
            })

    confidence = field_data.get("confidence")

    if confidence is not None and confidence not in VALID_CONFIDENCES:
        errors.append({
            "field": f"{field_name}.confidence",
            "message": "Confiança deve ser high, medium ou low."
        })

    return errors


def validate_required_extracted_fields(
    fields: dict,
    required_fields: list[str],
    document_label: str
) -> tuple[list[dict], list[dict]]:
    """
    Valida campos obrigatórios e campos extras de uma extração.
    """
    errors = []
    warnings = []

    for field_name in required_fields:
        if field_name not in fields:
            errors.append({
                "field": f"fields.{field_name}",
                "message": f"Campo obrigatório ausente para {document_label}."
            })
            continue

        field_errors = validate_extracted_field(
            f"fields.{field_name}",
            fields[field_name]
        )
        errors.extend(field_errors)

    for field_name, field_data in fields.items():
        if field_name not in required_fields:
            warnings.append({
                "field": f"fields.{field_name}",
                "message": f"Campo extra não reconhecido para {document_label}."
            })

        if isinstance(field_data, dict):
            confidence = field_data.get("confidence")
            if confidence == "low":
                warnings.append({
                    "field": f"fields.{field_name}",
                    "message": "Campo com baixa confiança; exigirá revisão humana."
                })

    return errors, warnings


def validate_base_extracted(
    data: dict,
    expected_document_type: str
) -> tuple[list[dict], list[dict], dict | None]:
    """
    Valida a estrutura base comum de uma extração.
    """
    errors = []
    warnings = []

    if data.get("document_type") != expected_document_type:
        errors.append({
            "field": "document_type",
            "message": f"document_type deve ser {expected_document_type}."
        })

    if not data.get("source_file"):
        errors.append({
            "field": "source_file",
            "message": "source_file é obrigatório."
        })

    fields = data.get("fields")

    if not isinstance(fields, dict):
        errors.append({
            "field": "fields",
            "message": "fields deve ser um objeto."
        })
        return errors, warnings, None

    return errors, warnings, fields


def validate_extracted_informe_pj(data: dict) -> dict:
    """
    Valida a estrutura da extração simulada de um informe de rendimentos PJ.
    """
    errors, warnings, fields = validate_base_extracted(
        data,
        "informe_rendimentos_pj"
    )

    if fields is not None:
        field_errors, field_warnings = validate_required_extracted_fields(
            fields,
            REQUIRED_INFORME_PJ_FIELDS,
            "informe de rendimentos PJ"
        )
        errors.extend(field_errors)
        warnings.extend(field_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_extracted_recibo_medico(data: dict) -> dict:
    """
    Valida a estrutura da extração simulada de um recibo médico.
    """
    errors, warnings, fields = validate_base_extracted(
        data,
        "recibo_medico"
    )

    if fields is not None:
        field_errors, field_warnings = validate_required_extracted_fields(
            fields,
            REQUIRED_RECIBO_MEDICO_FIELDS,
            "recibo médico"
        )
        errors.extend(field_errors)
        warnings.extend(field_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_extracted_plano_saude(data: dict) -> dict:
    """
    Valida a estrutura da extração simulada de um informe de plano de saúde.
    """
    errors, warnings, fields = validate_base_extracted(
        data,
        "plano_saude"
    )

    if fields is not None:
        field_errors, field_warnings = validate_required_extracted_fields(
            fields,
            REQUIRED_PLANO_SAUDE_FIELDS,
            "plano de saúde"
        )
        errors.extend(field_errors)
        warnings.extend(field_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_extracted_bem_imovel(data: dict) -> dict:
    """
    Valida a estrutura da extração simulada de um bem imóvel.
    """
    errors, warnings, fields = validate_base_extracted(
        data,
        "bem_imovel"
    )

    if fields is not None:
        field_errors, field_warnings = validate_required_extracted_fields(
            fields,
            REQUIRED_BEM_IMOVEL_FIELDS,
            "bem imóvel"
        )
        errors.extend(field_errors)
        warnings.extend(field_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_extracted_bem_veiculo(data: dict) -> dict:
    """
    Valida a estrutura da extração simulada de um bem veículo.
    """
    errors, warnings, fields = validate_base_extracted(
        data,
        "bem_veiculo"
    )

    if fields is not None:
        field_errors, field_warnings = validate_required_extracted_fields(
            fields,
            REQUIRED_BEM_VEICULO_FIELDS,
            "bem veículo"
        )
        errors.extend(field_errors)
        warnings.extend(field_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_extracted(data: dict) -> dict:
    """
    Valida uma extração com base no document_type.
    """
    document_type = data.get("document_type")

    if document_type == "informe_rendimentos_pj":
        return validate_extracted_informe_pj(data)

    if document_type == "recibo_medico":
        return validate_extracted_recibo_medico(data)

    if document_type == "plano_saude":
        return validate_extracted_plano_saude(data)

    if document_type == "bem_imovel":
        return validate_extracted_bem_imovel(data)

    if document_type == "bem_veiculo":
        return validate_extracted_bem_veiculo(data)

    return {
        "valid": False,
        "errors": [
            {
                "field": "document_type",
                "message": f"Tipo de documento não suportado: {document_type}"
            }
        ],
        "warnings": []
    }


def print_validation_result(result: dict) -> None:
    """
    Mostra o resultado da validação no terminal.
    """
    if result["valid"]:
        print("Extração válida.")
    else:
        print("Extração inválida.")

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    if errors:
        print("\nErros:")
        for error in errors:
            print(f"- {error['field']}: {error['message']}")

    if warnings:
        print("\nAvisos:")
        for warning in warnings:
            print(f"- {warning['field']}: {warning['message']}")


def main() -> None:
    """
    Uso:
        python3 tools/validate_extracted.py inputs/extracted/bem_veiculo_exemplo.json
    """
    if len(sys.argv) != 2:
        print("Uso:")
        print("python3 tools/validate_extracted.py inputs/extracted/informe_pj_exemplo.json")
        print("python3 tools/validate_extracted.py inputs/extracted/recibo_medico_exemplo.json")
        print("python3 tools/validate_extracted.py inputs/extracted/plano_saude_exemplo.json")
        print("python3 tools/validate_extracted.py inputs/extracted/bem_imovel_exemplo.json")
        print("python3 tools/validate_extracted.py inputs/extracted/bem_veiculo_exemplo.json")
        sys.exit(1)

    input_path = sys.argv[1]

    data = load_json(input_path)
    result = validate_extracted(data)

    print_validation_result(result)

    if not result["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()