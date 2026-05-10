import json
import sys
from pathlib import Path

from validate import validate_canonical_irpf


def cents_to_brl(value: int | None) -> str:
    """
    Converte centavos inteiros para formato brasileiro.

    Exemplo:
    8500000 -> R$ 85.000,00
    """
    if value is None:
        value = 0

    reais = value // 100
    centavos = value % 100

    reais_formatado = f"{reais:,}".replace(",", ".")

    return f"R$ {reais_formatado},{centavos:02d}"


def load_json(path: str) -> dict:
    """
    Carrega um arquivo JSON.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def add_validation_section(lines: list[str], validation: dict) -> None:
    """
    Adiciona a seção de validação ao relatório.
    """
    lines.append("## Validação")
    lines.append("")

    if validation["valid"]:
        lines.append("Status: **JSON válido**")
    else:
        lines.append("Status: **JSON inválido**")

    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])

    if errors:
        lines.append("")
        lines.append("### Erros")
        lines.append("")
        for error in errors:
            lines.append(f"- `{error['field']}`: {error['message']}")

    if warnings:
        lines.append("")
        lines.append("### Avisos da validação")
        lines.append("")
        for warning in warnings:
            lines.append(f"- `{warning['field']}`: {warning['message']}")

    if not errors and not warnings:
        lines.append("")
        lines.append("Nenhum erro ou aviso encontrado na validação.")

    lines.append("")


def add_declarante_section(lines: list[str], data: dict) -> None:
    """
    Adiciona a seção do declarante.
    """
    declarante = data.get("declarante", {})

    lines.append("## Declarante")
    lines.append("")
    lines.append(f"- Nome: {declarante.get('nome', '')}")
    lines.append(f"- CPF: {declarante.get('cpf', '')}")
    lines.append(f"- Data de nascimento: {declarante.get('data_nascimento', '')}")
    lines.append("")


def add_processing_warnings_section(lines: list[str], data: dict) -> None:
    """
    Adiciona avisos gerados pelo processamento/consolidação.
    """
    avisos = data.get("avisos", [])

    lines.append("## Avisos do processamento")
    lines.append("")

    if not avisos:
        lines.append("Nenhum aviso de processamento informado.")
        lines.append("")
        return

    for aviso in avisos:
        field = aviso.get("field", "")
        message = aviso.get("message", "")

        if field:
            lines.append(f"- `{field}`: {message}")
        else:
            lines.append(f"- {message}")

    lines.append("")


def add_rendimentos_pj_section(lines: list[str], data: dict) -> None:
    """
    Adiciona a seção de rendimentos tributáveis PJ.
    """
    rendimentos_pj = (
        data.get("rendimentos", {})
        .get("tributaveis_pj", [])
    )

    lines.append("## Rendimentos tributáveis PJ")
    lines.append("")

    if not rendimentos_pj:
        lines.append("Nenhum rendimento tributável PJ informado.")
        lines.append("")
        return

    for index, rendimento in enumerate(rendimentos_pj, start=1):
        lines.append(f"### Fonte pagadora {index}")
        lines.append("")
        lines.append(f"- Nome pagador: {rendimento.get('nome_pagador', '')}")
        lines.append(f"- CNPJ pagador: {rendimento.get('cnpj_pagador', '')}")
        lines.append(
            f"- Rendimento total: "
            f"{cents_to_brl(rendimento.get('rendimento_total', 0))}"
        )
        lines.append(
            f"- Previdência oficial: "
            f"{cents_to_brl(rendimento.get('previdencia_oficial', 0))}"
        )
        lines.append(
            f"- 13º salário: "
            f"{cents_to_brl(rendimento.get('decimo_terceiro', 0))}"
        )
        lines.append(
            f"- IRRF: "
            f"{cents_to_brl(rendimento.get('irrf', 0))}"
        )
        lines.append(
            f"- IRRF sobre 13º: "
            f"{cents_to_brl(rendimento.get('irrf_13', 0))}"
        )
        lines.append(f"- Beneficiário: {rendimento.get('beneficiario', '')}")
        lines.append("")


def add_pagamentos_section(lines: list[str], data: dict) -> None:
    """
    Adiciona a seção de pagamentos.
    """
    pagamentos = data.get("pagamentos", [])

    lines.append("## Pagamentos")
    lines.append("")

    if not pagamentos:
        lines.append("Nenhum pagamento informado.")
        lines.append("")
        return

    for index, pagamento in enumerate(pagamentos, start=1):
        lines.append(f"### Pagamento {index}")
        lines.append("")
        lines.append(f"- Código: {pagamento.get('codigo', '')}")
        lines.append(f"- Descrição: {pagamento.get('descricao', '')}")
        lines.append(f"- Prestador/beneficiário: {pagamento.get('beneficiario_nome', '')}")
        lines.append(f"- CPF/CNPJ: {pagamento.get('beneficiario_cpf_cnpj', '')}")
        lines.append(f"- Tipo beneficiário: {pagamento.get('beneficiario_tipo', '')}")
        lines.append(f"- Tipo documento: {pagamento.get('tipo_documento', '')}")
        lines.append(
            f"- Valor pago: "
            f"{cents_to_brl(pagamento.get('valor_pago', 0))}"
        )
        lines.append(
            f"- Valor não dedutível: "
            f"{cents_to_brl(pagamento.get('valor_nao_dedutivel', 0))}"
        )

        if pagamento.get("data_pagamento"):
            lines.append(f"- Data do pagamento: {pagamento.get('data_pagamento', '')}")

        lines.append("")


def add_bem_common_fields(lines: list[str], bem: dict) -> None:
    """
    Adiciona campos comuns de qualquer bem.
    """
    lines.append(f"- Tipo do bem: {bem.get('tipo_bem', '')}")
    lines.append(f"- Grupo: {bem.get('grupo_bem', '')}")
    lines.append(f"- Código: {bem.get('codigo_bem', '')}")
    lines.append(f"- Descrição: {bem.get('descricao', '')}")
    lines.append(f"- Valor em 31/12 anterior: {cents_to_brl(bem.get('valor_anterior', 0))}")
    lines.append(f"- Valor em 31/12 atual: {cents_to_brl(bem.get('valor_atual', 0))}")
    lines.append(f"- Data de aquisição: {bem.get('data_aquisicao', '')}")
    lines.append(f"- Beneficiário: {bem.get('beneficiario_tipo', '')}")
    lines.append("")


def add_bem_imovel_details(lines: list[str], bem: dict) -> None:
    """
    Adiciona detalhes específicos de imóvel.
    """
    endereco = bem.get("endereco", {})

    lines.append("#### Endereço")
    lines.append("")
    lines.append(f"- CEP: {endereco.get('cep', '')}")
    lines.append(f"- Logradouro: {endereco.get('logradouro', '')}")
    lines.append(f"- Número: {endereco.get('numero', '')}")
    lines.append(f"- Bairro: {endereco.get('bairro', '')}")
    lines.append(f"- Município: {endereco.get('municipio', '')}")
    lines.append(f"- UF: {endereco.get('uf', '')}")
    lines.append("")

    lines.append("#### Dados do imóvel")
    lines.append("")
    lines.append(f"- IPTU: {bem.get('iptu', '')}")
    lines.append(f"- Matrícula: {bem.get('matricula', '')}")
    lines.append("")


def add_bem_veiculo_details(lines: list[str], bem: dict) -> None:
    """
    Adiciona detalhes específicos de veículo.
    """
    lines.append("#### Dados do veículo")
    lines.append("")
    lines.append(f"- RENAVAM: {bem.get('renavam', '')}")
    lines.append(f"- Placa: {bem.get('placa', '')}")
    lines.append(f"- Marca: {bem.get('marca', '')}")
    lines.append(f"- Modelo: {bem.get('modelo', '')}")
    lines.append(f"- Ano de fabricação: {bem.get('ano_fabricacao', '')}")
    lines.append("")


def add_bens_section(lines: list[str], data: dict) -> None:
    """
    Adiciona a seção de bens e direitos.
    """
    bens = data.get("bens", [])

    lines.append("## Bens e direitos")
    lines.append("")

    if not bens:
        lines.append("Nenhum bem informado.")
        lines.append("")
        return

    for index, bem in enumerate(bens, start=1):
        tipo_bem = bem.get("tipo_bem", "")

        lines.append(f"### Bem {index}")
        lines.append("")

        add_bem_common_fields(lines, bem)

        if tipo_bem == "IMOVEL":
            add_bem_imovel_details(lines, bem)
        elif tipo_bem == "VEICULO":
            add_bem_veiculo_details(lines, bem)
        else:
            lines.append("#### Dados específicos")
            lines.append("")
            lines.append("Tipo de bem não reconhecido para detalhamento específico.")
            lines.append("")


def add_review_section(lines: list[str], data: dict) -> None:
    """
    Adiciona a seção de pendências de revisão.
    """
    requires_review = data.get("requires_review", [])

    lines.append("## Pendências de revisão")
    lines.append("")

    if not requires_review:
        lines.append("Nenhuma pendência de revisão informada.")
    else:
        for item in requires_review:
            field = item.get("field", "")
            reason = item.get("reason", "")
            source_hint = item.get("source_hint", "")
            source_file = item.get("source_file", "")

            details = reason

            if source_hint:
                details += f" Fonte: {source_hint}"

            if source_file:
                details += f" Arquivo: {source_file}"

            lines.append(f"- `{field}`: {details}")

    lines.append("")


def add_next_steps_section(lines: list[str]) -> None:
    """
    Adiciona próximos passos.
    """
    lines.append("## Próximos passos")
    lines.append("")
    lines.append("1. Conferir os dados acima com os documentos originais.")
    lines.append("2. Corrigir o JSON canônico, se necessário.")
    lines.append("3. Rodar novamente a validação.")
    lines.append("4. Somente depois avançar para geração experimental do `.DEC`.")
    lines.append("")


def generate_report(data: dict) -> str:
    """
    Gera um relatório em Markdown a partir do JSON canônico.
    """
    validation = validate_canonical_irpf(data)

    lines = []

    lines.append(f"# Relatório IRPF {data.get('exercicio', '')}")
    lines.append("")
    lines.append("## Aviso")
    lines.append("")
    lines.append(
        "Este relatório é apenas uma prévia para revisão humana. "
        "Ele não substitui conferência no PGD oficial nem orientação contábil."
    )
    lines.append("")

    add_declarante_section(lines, data)
    add_validation_section(lines, validation)
    add_processing_warnings_section(lines, data)
    add_rendimentos_pj_section(lines, data)
    add_pagamentos_section(lines, data)
    add_bens_section(lines, data)
    add_review_section(lines, data)
    add_next_steps_section(lines)

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva o relatório em arquivo Markdown.
    """
    file_path = Path(output_path)

    with file_path.open("w", encoding="utf-8") as file:
        file.write(report)


def main() -> None:
    """
    Uso:
        python3 tools/report.py outputs/irpf-consolidado.json outputs/irpf-consolidado.report.md
    """
    if len(sys.argv) != 3:
        print("Uso:")
        print("python3 tools/report.py outputs/irpf-consolidado.json outputs/irpf-consolidado.report.md")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    data = load_json(input_path)
    report = generate_report(data)
    save_report(report, output_path)

    print(f"Relatório gerado em: {output_path}")


if __name__ == "__main__":
    main()