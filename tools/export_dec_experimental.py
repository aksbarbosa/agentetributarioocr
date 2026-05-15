import json
import sys
from pathlib import Path


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def money_to_reais(value) -> str:
    if value is None:
        return "0,00"

    try:
        cents = int(value)
    except (TypeError, ValueError):
        return "0,00"

    reais = cents // 100
    centavos = cents % 100

    return f"{reais},{centavos:02d}"


def safe(value) -> str:
    if value is None:
        return ""

    return str(value).replace("|", " ").replace("\n", " ").strip()


def build_declarante_section(data: dict) -> list[str]:
    declarante = data.get("declarante", {})

    return [
        "[DECLARANTE]",
        f"nome={safe(declarante.get('nome'))}",
        f"cpf={safe(declarante.get('cpf'))}",
        f"data_nascimento={safe(declarante.get('data_nascimento'))}",
        "",
    ]


def build_rendimentos_section(data: dict) -> list[str]:
    lines = ["[RENDIMENTOS_TRIBUTAVEIS_PJ]"]

    rendimentos = (
        data.get("rendimentos", {})
        .get("tributaveis_pj", [])
    )

    for index, item in enumerate(rendimentos, start=1):
        lines.append(f"item={index}")
        lines.append(f"nome_pagador={safe(item.get('nome_pagador'))}")
        lines.append(f"cnpj_pagador={safe(item.get('cnpj_pagador'))}")
        lines.append(f"rendimento_total={money_to_reais(item.get('rendimento_total'))}")
        lines.append(f"previdencia_oficial={money_to_reais(item.get('previdencia_oficial'))}")
        lines.append(f"decimo_terceiro={money_to_reais(item.get('decimo_terceiro'))}")
        lines.append(f"irrf={money_to_reais(item.get('irrf'))}")
        lines.append(f"irrf_13={money_to_reais(item.get('irrf_13'))}")
        lines.append("")

    if not rendimentos:
        lines.append("nenhum_item=true")
        lines.append("")

    return lines


def build_pagamentos_section(data: dict) -> list[str]:
    lines = ["[PAGAMENTOS]"]

    pagamentos = data.get("pagamentos", [])

    for index, item in enumerate(pagamentos, start=1):
        lines.append(f"item={index}")
        lines.append(f"codigo={safe(item.get('codigo'))}")
        lines.append(f"descricao={safe(item.get('descricao'))}")
        lines.append(f"nome_prestador={safe(item.get('nome_prestador'))}")
        lines.append(f"cpf_cnpj_prestador={safe(item.get('cpf_cnpj_prestador'))}")
        lines.append(f"tipo_beneficiario={safe(item.get('tipo_beneficiario'))}")
        lines.append(f"tipo_documento={safe(item.get('tipo_documento'))}")
        lines.append(f"valor_pago={money_to_reais(item.get('valor_pago'))}")
        lines.append(f"valor_nao_dedutivel={money_to_reais(item.get('valor_nao_dedutivel'))}")
        lines.append(f"data_pagamento={safe(item.get('data_pagamento'))}")
        lines.append("")

    if not pagamentos:
        lines.append("nenhum_item=true")
        lines.append("")

    return lines


def build_bens_section(data: dict) -> list[str]:
    lines = ["[BENS_E_DIREITOS]"]

    bens = data.get("bens", [])

    for index, item in enumerate(bens, start=1):
        endereco = item.get("endereco", {})
        dados_imovel = item.get("dados_imovel", {})
        dados_veiculo = item.get("dados_veiculo", {})

        lines.append(f"item={index}")
        lines.append(f"tipo_bem={safe(item.get('tipo_bem'))}")
        lines.append(f"grupo={safe(item.get('grupo'))}")
        lines.append(f"codigo={safe(item.get('codigo'))}")
        lines.append(f"descricao={safe(item.get('descricao'))}")
        lines.append(f"valor_anterior={money_to_reais(item.get('valor_anterior'))}")
        lines.append(f"valor_atual={money_to_reais(item.get('valor_atual'))}")
        lines.append(f"data_aquisicao={safe(item.get('data_aquisicao'))}")
        lines.append(f"beneficiario={safe(item.get('beneficiario'))}")

        if endereco:
            lines.append(f"endereco_cep={safe(endereco.get('cep'))}")
            lines.append(f"endereco_logradouro={safe(endereco.get('logradouro'))}")
            lines.append(f"endereco_numero={safe(endereco.get('numero'))}")
            lines.append(f"endereco_bairro={safe(endereco.get('bairro'))}")
            lines.append(f"endereco_municipio={safe(endereco.get('municipio'))}")
            lines.append(f"endereco_uf={safe(endereco.get('uf'))}")

        if dados_imovel:
            lines.append(f"iptu={safe(dados_imovel.get('iptu'))}")
            lines.append(f"matricula={safe(dados_imovel.get('matricula'))}")

        if dados_veiculo:
            lines.append(f"renavam={safe(dados_veiculo.get('renavam'))}")
            lines.append(f"placa={safe(dados_veiculo.get('placa'))}")
            lines.append(f"marca={safe(dados_veiculo.get('marca'))}")
            lines.append(f"modelo={safe(dados_veiculo.get('modelo'))}")
            lines.append(f"ano_fabricacao={safe(dados_veiculo.get('ano_fabricacao'))}")

        lines.append("")

    if not bens:
        lines.append("nenhum_item=true")
        lines.append("")

    return lines


def build_experimental_dec(data: dict) -> str:
    lines = [
        "# IRPF OCR DEC - EXPORTAÇÃO EXPERIMENTAL",
        "# Este arquivo NÃO é um .DEC oficial.",
        "# Serve apenas para estudo de mapeamento e futura geração compatível.",
        "",
    ]

    lines.extend(build_declarante_section(data))
    lines.extend(build_rendimentos_section(data))
    lines.extend(build_pagamentos_section(data))
    lines.extend(build_bens_section(data))

    return "\n".join(lines)


def build_report(input_path: str, output_path: str, data: dict) -> str:
    rendimentos = data.get("rendimentos", {}).get("tributaveis_pj", [])
    pagamentos = data.get("pagamentos", [])
    bens = data.get("bens", [])

    lines = [
        "# Relatório de exportação DEC experimental",
        "",
        "## Aviso",
        "",
        "Este relatório descreve uma exportação experimental.",
        "",
        "O arquivo gerado não é um `.DEC` oficial e não deve ser importado no PGD.",
        "",
        "## Arquivos",
        "",
        f"- Entrada: `{input_path}`",
        f"- Saída experimental: `{output_path}`",
        "",
        "## Resumo",
        "",
        f"- Rendimentos tributáveis PJ: {len(rendimentos)}",
        f"- Pagamentos: {len(pagamentos)}",
        f"- Bens e direitos: {len(bens)}",
        "",
        "## Próximos passos",
        "",
        "1. Estudar o layout real do `.DEC`.",
        "2. Mapear cada seção canônica para registros oficiais.",
        "3. Criar testes com fixtures pequenas.",
        "4. Validar compatibilidade com o PGD em ambiente controlado.",
    ]

    return "\n".join(lines)


def save_text(content: str, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[str, str, str]:
    input_json = "outputs/irpf-consolidado.json"
    output_txt = "outputs/irpf-export-dec-experimental.txt"
    output_report = "outputs/irpf-export-dec-experimental.report.md"

    args = argv[1:]

    if len(args) == 0:
        return input_json, output_txt, output_report

    if len(args) == 3:
        return args[0], args[1], args[2]

    print("Uso:")
    print("python3 tools/export_dec_experimental.py")
    print("python3 tools/export_dec_experimental.py input.json output.txt output.report.md")
    sys.exit(1)


def main() -> None:
    input_json, output_txt, output_report = parse_args(sys.argv)

    data = load_json(input_json)

    export_content = build_experimental_dec(data)
    report_content = build_report(input_json, output_txt, data)

    save_text(export_content, output_txt)
    save_text(report_content, output_report)

    print("Exportação DEC experimental finalizada.")
    print(f"Entrada: {input_json}")
    print(f"Saída experimental: {output_txt}")
    print(f"Relatório: {output_report}")


if __name__ == "__main__":
    main()