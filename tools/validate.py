from normalize import only_digits


VALID_PAYMENT_CODES = {
    "10": "Médicos no Brasil",
    "26": "Planos de saúde no Brasil",
}


VALID_BENEFICIARIO_TIPOS = {"T", "D"}


VALID_TIPO_DOCUMENTO = {1, 2}
# 1 = CPF
# 2 = CNPJ


VALID_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
}


VALID_TIPOS_BEM = {"IMOVEL", "VEICULO"}


def validate_cpf(cpf: str | None) -> bool:
    """
    Valida CPF pelo cálculo dos dígitos verificadores.
    """
    cpf = only_digits(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    total = 0
    for i in range(9):
        total += int(cpf[i]) * (10 - i)

    digit_1 = (total * 10) % 11
    if digit_1 == 10:
        digit_1 = 0

    if digit_1 != int(cpf[9]):
        return False

    total = 0
    for i in range(10):
        total += int(cpf[i]) * (11 - i)

    digit_2 = (total * 10) % 11
    if digit_2 == 10:
        digit_2 = 0

    if digit_2 != int(cpf[10]):
        return False

    return True


def validate_cnpj(cnpj: str | None) -> bool:
    """
    Valida CNPJ pelo cálculo dos dígitos verificadores.
    """
    cnpj = only_digits(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_2 = [6] + weights_1

    total = 0
    for i in range(12):
        total += int(cnpj[i]) * weights_1[i]

    remainder = total % 11
    digit_1 = 0 if remainder < 2 else 11 - remainder

    if digit_1 != int(cnpj[12]):
        return False

    total = 0
    for i in range(13):
        total += int(cnpj[i]) * weights_2[i]

    remainder = total % 11
    digit_2 = 0 if remainder < 2 else 11 - remainder

    if digit_2 != int(cnpj[13]):
        return False

    return True


def validate_cpf_or_cnpj(value: str | None) -> bool:
    """
    Valida um identificador que pode ser CPF ou CNPJ.
    """
    digits = only_digits(value)

    if len(digits) == 11:
        return validate_cpf(digits)

    if len(digits) == 14:
        return validate_cnpj(digits)

    return False


def is_ddmmaaaa(value: str | None) -> bool:
    """
    Valida formato simples DDMMAAAA.

    Observação:
    Ainda não valida se a data existe no calendário.
    """
    if value is None:
        return False

    text = str(value)

    if len(text) != 8:
        return False

    if not text.isdigit():
        return False

    day = int(text[0:2])
    month = int(text[2:4])
    year = int(text[4:8])

    if not 1 <= day <= 31:
        return False

    if not 1 <= month <= 12:
        return False

    if year < 1900:
        return False

    return True


def validate_required_fields(data: dict) -> list[dict]:
    """
    Verifica campos obrigatórios mínimos do JSON canônico.
    Retorna uma lista de erros.
    """
    errors = []

    declarante = data.get("declarante", {})

    if not declarante.get("cpf"):
        errors.append({
            "field": "declarante.cpf",
            "message": "CPF do declarante é obrigatório."
        })

    if not declarante.get("nome"):
        errors.append({
            "field": "declarante.nome",
            "message": "Nome do declarante é obrigatório."
        })

    if not declarante.get("data_nascimento"):
        errors.append({
            "field": "declarante.data_nascimento",
            "message": "Data de nascimento do declarante é obrigatória."
        })

    return errors


def validate_rendimentos_pj(data: dict) -> tuple[list[dict], list[dict]]:
    """
    Valida rendimentos tributáveis recebidos de PJ.
    """
    errors = []
    warnings = []

    rendimentos_pj = (
        data.get("rendimentos", {})
        .get("tributaveis_pj", [])
    )

    for index, rendimento in enumerate(rendimentos_pj):
        cnpj = rendimento.get("cnpj_pagador")

        if not cnpj:
            errors.append({
                "field": f"rendimentos.tributaveis_pj[{index}].cnpj_pagador",
                "message": "CNPJ do pagador é obrigatório."
            })
        elif not validate_cnpj(cnpj):
            errors.append({
                "field": f"rendimentos.tributaveis_pj[{index}].cnpj_pagador",
                "message": "CNPJ do pagador é inválido."
            })

        rendimento_total = rendimento.get("rendimento_total", 0)
        irrf = rendimento.get("irrf", 0)

        if rendimento_total < 0:
            errors.append({
                "field": f"rendimentos.tributaveis_pj[{index}].rendimento_total",
                "message": "Rendimento total não pode ser negativo."
            })

        if irrf < 0:
            errors.append({
                "field": f"rendimentos.tributaveis_pj[{index}].irrf",
                "message": "IRRF não pode ser negativo."
            })

        if irrf > rendimento_total:
            warnings.append({
                "field": f"rendimentos.tributaveis_pj[{index}].irrf",
                "message": "IRRF maior que rendimento total. Verifique o informe."
            })

    return errors, warnings


def validate_pagamentos(data: dict) -> tuple[list[dict], list[dict]]:
    """
    Valida pagamentos do JSON canônico.
    """
    errors = []
    warnings = []

    pagamentos = data.get("pagamentos", [])

    if not isinstance(pagamentos, list):
        errors.append({
            "field": "pagamentos",
            "message": "Pagamentos deve ser uma lista."
        })
        return errors, warnings

    for index, pagamento in enumerate(pagamentos):
        field_prefix = f"pagamentos[{index}]"

        codigo = pagamento.get("codigo")
        descricao = pagamento.get("descricao")
        beneficiario_cpf_cnpj = pagamento.get("beneficiario_cpf_cnpj")
        beneficiario_nome = pagamento.get("beneficiario_nome")
        beneficiario_tipo = pagamento.get("beneficiario_tipo")
        tipo_documento = pagamento.get("tipo_documento")
        valor_pago = pagamento.get("valor_pago", 0)
        valor_nao_dedutivel = pagamento.get("valor_nao_dedutivel", 0)
        data_pagamento = pagamento.get("data_pagamento")

        if codigo not in VALID_PAYMENT_CODES:
            errors.append({
                "field": f"{field_prefix}.codigo",
                "message": "Código de pagamento inválido ou ainda não suportado."
            })

        if not descricao:
            errors.append({
                "field": f"{field_prefix}.descricao",
                "message": "Descrição do pagamento é obrigatória."
            })

        if not beneficiario_nome:
            errors.append({
                "field": f"{field_prefix}.beneficiario_nome",
                "message": "Nome do prestador/beneficiário é obrigatório."
            })

        if not beneficiario_cpf_cnpj:
            errors.append({
                "field": f"{field_prefix}.beneficiario_cpf_cnpj",
                "message": "CPF/CNPJ do prestador é obrigatório."
            })
        elif not validate_cpf_or_cnpj(beneficiario_cpf_cnpj):
            errors.append({
                "field": f"{field_prefix}.beneficiario_cpf_cnpj",
                "message": "CPF/CNPJ do prestador é inválido."
            })

        if beneficiario_tipo not in VALID_BENEFICIARIO_TIPOS:
            errors.append({
                "field": f"{field_prefix}.beneficiario_tipo",
                "message": "beneficiario_tipo deve ser T ou D."
            })

        if tipo_documento not in VALID_TIPO_DOCUMENTO:
            errors.append({
                "field": f"{field_prefix}.tipo_documento",
                "message": "tipo_documento deve ser 1 para CPF ou 2 para CNPJ."
            })

        if valor_pago <= 0:
            errors.append({
                "field": f"{field_prefix}.valor_pago",
                "message": "valor_pago deve ser maior que zero."
            })

        if valor_nao_dedutivel < 0:
            errors.append({
                "field": f"{field_prefix}.valor_nao_dedutivel",
                "message": "valor_nao_dedutivel não pode ser negativo."
            })

        if valor_nao_dedutivel > valor_pago:
            warnings.append({
                "field": f"{field_prefix}.valor_nao_dedutivel",
                "message": "Valor não dedutível maior que valor pago. Verifique."
            })

        if data_pagamento and not is_ddmmaaaa(data_pagamento):
            errors.append({
                "field": f"{field_prefix}.data_pagamento",
                "message": "data_pagamento deve estar no formato DDMMAAAA."
            })

    return errors, warnings


def validate_bem_common(bem: dict, field_prefix: str) -> tuple[list[dict], list[dict]]:
    """
    Valida campos comuns a qualquer bem.
    """
    errors = []
    warnings = []

    tipo_bem = bem.get("tipo_bem")
    grupo_bem = bem.get("grupo_bem")
    codigo_bem = bem.get("codigo_bem")
    descricao = bem.get("descricao")
    valor_anterior = bem.get("valor_anterior", 0)
    valor_atual = bem.get("valor_atual", 0)
    data_aquisicao = bem.get("data_aquisicao")
    beneficiario_tipo = bem.get("beneficiario_tipo")

    if tipo_bem not in VALID_TIPOS_BEM:
        errors.append({
            "field": f"{field_prefix}.tipo_bem",
            "message": "tipo_bem deve ser IMOVEL ou VEICULO."
        })

    if not grupo_bem:
        errors.append({
            "field": f"{field_prefix}.grupo_bem",
            "message": "grupo_bem é obrigatório."
        })
    elif len(str(grupo_bem)) != 2:
        errors.append({
            "field": f"{field_prefix}.grupo_bem",
            "message": "grupo_bem deve ter 2 dígitos."
        })

    if not codigo_bem:
        errors.append({
            "field": f"{field_prefix}.codigo_bem",
            "message": "codigo_bem é obrigatório."
        })
    elif len(str(codigo_bem)) != 2:
        errors.append({
            "field": f"{field_prefix}.codigo_bem",
            "message": "codigo_bem deve ter 2 dígitos."
        })

    if not descricao:
        errors.append({
            "field": f"{field_prefix}.descricao",
            "message": "Descrição do bem é obrigatória."
        })

    if valor_anterior < 0:
        errors.append({
            "field": f"{field_prefix}.valor_anterior",
            "message": "valor_anterior não pode ser negativo."
        })

    if valor_atual < 0:
        errors.append({
            "field": f"{field_prefix}.valor_atual",
            "message": "valor_atual não pode ser negativo."
        })

    if valor_atual == 0 and valor_anterior == 0:
        warnings.append({
            "field": f"{field_prefix}.valor_atual",
            "message": "Bem com valor anterior e atual iguais a zero. Verifique."
        })

    if data_aquisicao and not is_ddmmaaaa(data_aquisicao):
        errors.append({
            "field": f"{field_prefix}.data_aquisicao",
            "message": "data_aquisicao deve estar no formato DDMMAAAA."
        })

    if beneficiario_tipo not in VALID_BENEFICIARIO_TIPOS:
        errors.append({
            "field": f"{field_prefix}.beneficiario_tipo",
            "message": "beneficiario_tipo deve ser T ou D."
        })

    return errors, warnings


def validate_bem_imovel(bem: dict, field_prefix: str) -> tuple[list[dict], list[dict]]:
    """
    Valida campos específicos de imóvel.
    """
    errors = []
    warnings = []

    endereco = bem.get("endereco", {})
    iptu = bem.get("iptu")
    matricula = bem.get("matricula")

    if not isinstance(endereco, dict):
        errors.append({
            "field": f"{field_prefix}.endereco",
            "message": "endereco deve ser um objeto."
        })
        return errors, warnings

    cep = endereco.get("cep")
    logradouro = endereco.get("logradouro")
    numero = endereco.get("numero")
    bairro = endereco.get("bairro")
    municipio = endereco.get("municipio")
    uf = endereco.get("uf")

    if not cep:
        errors.append({
            "field": f"{field_prefix}.endereco.cep",
            "message": "CEP é obrigatório."
        })
    elif len(only_digits(cep)) != 8:
        errors.append({
            "field": f"{field_prefix}.endereco.cep",
            "message": "CEP deve ter 8 dígitos."
        })

    if not logradouro:
        errors.append({
            "field": f"{field_prefix}.endereco.logradouro",
            "message": "Logradouro é obrigatório."
        })

    if not numero:
        warnings.append({
            "field": f"{field_prefix}.endereco.numero",
            "message": "Número do imóvel ausente. Verifique se é S/N."
        })

    if not bairro:
        warnings.append({
            "field": f"{field_prefix}.endereco.bairro",
            "message": "Bairro ausente."
        })

    if not municipio:
        errors.append({
            "field": f"{field_prefix}.endereco.municipio",
            "message": "Município é obrigatório."
        })

    if not uf:
        errors.append({
            "field": f"{field_prefix}.endereco.uf",
            "message": "UF é obrigatória."
        })
    elif str(uf).upper() not in VALID_UFS:
        errors.append({
            "field": f"{field_prefix}.endereco.uf",
            "message": "UF inválida."
        })

    if not iptu:
        warnings.append({
            "field": f"{field_prefix}.iptu",
            "message": "IPTU ausente. Verifique se o imóvel possui cadastro municipal."
        })

    if not matricula:
        warnings.append({
            "field": f"{field_prefix}.matricula",
            "message": "Matrícula ausente. Verifique o registro do imóvel."
        })

    return errors, warnings


def validate_bem_veiculo(bem: dict, field_prefix: str) -> tuple[list[dict], list[dict]]:
    """
    Valida campos específicos de veículo.
    """
    errors = []
    warnings = []

    renavam = bem.get("renavam")
    placa = bem.get("placa")
    marca = bem.get("marca")
    modelo = bem.get("modelo")
    ano_fabricacao = bem.get("ano_fabricacao")

    if not renavam:
        errors.append({
            "field": f"{field_prefix}.renavam",
            "message": "RENAVAM é obrigatório."
        })
    elif len(only_digits(renavam)) not in {9, 10, 11}:
        warnings.append({
            "field": f"{field_prefix}.renavam",
            "message": "RENAVAM com quantidade incomum de dígitos. Verifique."
        })

    if not placa:
        errors.append({
            "field": f"{field_prefix}.placa",
            "message": "Placa é obrigatória."
        })
    elif len(str(placa)) not in {7, 8}:
        warnings.append({
            "field": f"{field_prefix}.placa",
            "message": "Placa com tamanho incomum. Verifique."
        })

    if not marca:
        errors.append({
            "field": f"{field_prefix}.marca",
            "message": "Marca do veículo é obrigatória."
        })

    if not modelo:
        errors.append({
            "field": f"{field_prefix}.modelo",
            "message": "Modelo do veículo é obrigatório."
        })

    if not ano_fabricacao:
        errors.append({
            "field": f"{field_prefix}.ano_fabricacao",
            "message": "Ano de fabricação é obrigatório."
        })
    elif len(str(ano_fabricacao)) != 4:
        errors.append({
            "field": f"{field_prefix}.ano_fabricacao",
            "message": "Ano de fabricação deve ter 4 dígitos."
        })

    return errors, warnings


def validate_bens(data: dict) -> tuple[list[dict], list[dict]]:
    """
    Valida bens e direitos do JSON canônico.
    """
    errors = []
    warnings = []

    bens = data.get("bens", [])

    if not isinstance(bens, list):
        errors.append({
            "field": "bens",
            "message": "Bens deve ser uma lista."
        })
        return errors, warnings

    for index, bem in enumerate(bens):
        field_prefix = f"bens[{index}]"

        common_errors, common_warnings = validate_bem_common(bem, field_prefix)
        errors.extend(common_errors)
        warnings.extend(common_warnings)

        tipo_bem = bem.get("tipo_bem")

        if tipo_bem == "IMOVEL":
            specific_errors, specific_warnings = validate_bem_imovel(bem, field_prefix)
            errors.extend(specific_errors)
            warnings.extend(specific_warnings)

        elif tipo_bem == "VEICULO":
            specific_errors, specific_warnings = validate_bem_veiculo(bem, field_prefix)
            errors.extend(specific_errors)
            warnings.extend(specific_warnings)

    return errors, warnings


def validate_canonical_irpf(data: dict) -> dict:
    """
    Valida o JSON canônico mínimo.
    """
    errors = []
    warnings = []

    errors.extend(validate_required_fields(data))

    declarante = data.get("declarante", {})
    cpf = declarante.get("cpf")
    data_nascimento = declarante.get("data_nascimento")

    if cpf and not validate_cpf(cpf):
        errors.append({
            "field": "declarante.cpf",
            "message": "CPF inválido."
        })

    if data_nascimento and not is_ddmmaaaa(data_nascimento):
        errors.append({
            "field": "declarante.data_nascimento",
            "message": "Data de nascimento deve estar no formato DDMMAAAA."
        })

    rendimento_errors, rendimento_warnings = validate_rendimentos_pj(data)
    errors.extend(rendimento_errors)
    warnings.extend(rendimento_warnings)

    pagamento_errors, pagamento_warnings = validate_pagamentos(data)
    errors.extend(pagamento_errors)
    warnings.extend(pagamento_warnings)

    bens_errors, bens_warnings = validate_bens(data)
    errors.extend(bens_errors)
    warnings.extend(bens_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


if __name__ == "__main__":
    print("CPF válido?", validate_cpf("12345678909"))
    print("CPF inválido?", validate_cpf("12345678900"))
    print("CNPJ válido?", validate_cnpj("11222333000181"))
    print("CNPJ inválido?", validate_cnpj("11222333000180"))
    print("CPF/CNPJ válido?", validate_cpf_or_cnpj("12345678909"))
    print("Data válida?", is_ddmmaaaa("15032025"))
    print("Data inválida?", is_ddmmaaaa("32132025"))