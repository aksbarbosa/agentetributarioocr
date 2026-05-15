import json
import sys
from pathlib import Path
from copy import deepcopy

from build_canonical_json import (
    load_json,
    save_json,
    build_canonical_json,
)

from validate_extracted import validate_extracted
from validate import validate_canonical_irpf
from report import generate_report, save_report


DEFAULT_INPUT_DIR = "inputs/extracted"
DEFAULT_OUTPUT_JSON = "outputs/irpf-consolidado.json"
DEFAULT_OUTPUT_REPORT = "outputs/irpf-consolidado.report.md"


def deduplicate_items_by_key(items: list[dict], key_fields: list[str]) -> list[dict]:
    """
    Remove itens duplicados preservando a primeira ocorrência.
    """
    seen = set()
    unique = []

    for item in items:
        key = tuple(item.get(field) for field in key_fields)

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return unique


def deduplicate_consolidated_records(consolidated: dict) -> dict:
    """
    Remove duplicidades óbvias do JSON consolidado.

    Esta etapa é aplicada depois da junção dos canônicos individuais.
    Ela evita que o mesmo documento entre duplicado por causa de OCR normal,
    OCR pré-processado ou arquivos repetidos.
    """
    consolidated["pagamentos"] = deduplicate_items_by_key(
        consolidated.get("pagamentos", []),
        [
            "codigo",
            "descricao",
            "beneficiario_cpf_cnpj",
            "beneficiario_nome",
            "beneficiario_tipo",
            "tipo_documento",
            "valor_pago",
            "valor_nao_dedutivel",
            "data_pagamento",
        ],
    )

    rendimentos = consolidated.get("rendimentos", {})
    rendimentos["tributaveis_pj"] = deduplicate_items_by_key(
        rendimentos.get("tributaveis_pj", []),
        [
            "cnpj_pagador",
            "nome_pagador",
            "rendimento_total",
            "previdencia_oficial",
            "decimo_terceiro",
            "irrf",
            "irrf_13",
            "beneficiario",
        ],
    )
    consolidated["rendimentos"] = rendimentos

    consolidated["bens"] = deduplicate_items_by_key(
        consolidated.get("bens", []),
        [
            "tipo_bem",
            "grupo",
            "codigo",
            "descricao",
            "valor_anterior",
            "valor_atual",
            "data_aquisicao",
            "beneficiario",
        ],
    )

    return consolidated


def load_config(config_path: str) -> dict:
    """
    Carrega o arquivo de configuração do projeto.

    Exemplo:
        config/project_config.json
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_paths_from_config(config: dict) -> tuple[str, str, str]:
    """
    Lê os caminhos principais a partir do config.
    Se algum campo estiver ausente, usa valores padrão.
    """
    input_dir = config.get("input_extracted_dir", DEFAULT_INPUT_DIR)
    output_json = config.get("output_json", DEFAULT_OUTPUT_JSON)
    output_report = config.get("output_report", DEFAULT_OUTPUT_REPORT)

    return input_dir, output_json, output_report


def empty_canonical(config: dict | None = None) -> dict:
    """
    Cria um JSON canônico vazio.
    Ele será preenchido a partir de vários documentos extraídos.
    """
    config = config or {}

    return {
        "$schema": config.get("schema_version", "irpf-2026-v1"),
        "exercicio": config.get("exercicio", 2026),
        "ano_calendario": config.get("ano_calendario", 2025),
        "tipo_declaracao": config.get("tipo_declaracao", "AJUSTE_ANUAL"),
        "modelo": config.get("modelo", "AUTO"),
        "declarante": {
            "cpf": "",
            "nome": "",
            "data_nascimento": ""
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


def merge_declarante(target: dict, source: dict, source_file: str) -> None:
    """
    Mescla dados do declarante.

    Regra atual:
    - se o campo do destino estiver vazio, copia do source;
    - se já existir valor diferente, cria aviso.
    """
    target_declarante = target["declarante"]
    source_declarante = source.get("declarante", {})

    for field in ["cpf", "nome", "data_nascimento"]:
        source_value = source_declarante.get(field, "")
        target_value = target_declarante.get(field, "")

        if not source_value:
            continue

        if not target_value:
            target_declarante[field] = source_value
            continue

        if target_value != source_value:
            target["avisos"].append({
                "field": f"declarante.{field}",
                "message": (
                    f"Valor conflitante no arquivo {source_file}. "
                    f"Valor consolidado: {target_value}. "
                    f"Valor encontrado: {source_value}."
                )
            })


def merge_canonical(target: dict, source: dict, source_file: str) -> None:
    """
    Mescla um JSON canônico parcial dentro do JSON consolidado.
    """
    merge_declarante(target, source, source_file)

    source_rendimentos = (
        source.get("rendimentos", {})
        .get("tributaveis_pj", [])
    )

    for rendimento in source_rendimentos:
        target["rendimentos"]["tributaveis_pj"].append(deepcopy(rendimento))

    for pagamento in source.get("pagamentos", []):
        target["pagamentos"].append(deepcopy(pagamento))

    for bem in source.get("bens", []):
        target["bens"].append(deepcopy(bem))

    for divida in source.get("dividas", []):
        target["dividas"].append(deepcopy(divida))

    for aviso in source.get("avisos", []):
        target["avisos"].append(deepcopy(aviso))

    for review_item in source.get("requires_review", []):
        item = deepcopy(review_item)
        item["source_file"] = source_file
        target["requires_review"].append(item)


def payment_key(pagamento: dict) -> tuple:
    """
    Cria uma chave para identificar pagamentos potencialmente duplicados.

    Regras atuais:

    - Código 10, recibo médico:
      usa CPF/CNPJ do prestador, valor pago, data de pagamento e descrição.

    - Código 26, plano de saúde:
      usa CNPJ da operadora, valor pago, valor não dedutível e descrição.
      Não usa data_pagamento porque o informe do plano costuma representar
      o valor anual consolidado.

    - Outros códigos:
      usa uma chave genérica.
    """
    codigo = pagamento.get("codigo", "")

    if codigo == "10":
        return (
            "pagamento_medico",
            pagamento.get("beneficiario_cpf_cnpj", ""),
            pagamento.get("valor_pago", 0),
            pagamento.get("data_pagamento", ""),
            pagamento.get("descricao", ""),
        )

    if codigo == "26":
        return (
            "plano_saude",
            pagamento.get("beneficiario_cpf_cnpj", ""),
            pagamento.get("valor_pago", 0),
            pagamento.get("valor_nao_dedutivel", 0),
            pagamento.get("descricao", ""),
        )

    return (
        "pagamento_generico",
        pagamento.get("codigo", ""),
        pagamento.get("beneficiario_cpf_cnpj", ""),
        pagamento.get("valor_pago", 0),
        pagamento.get("data_pagamento", ""),
        pagamento.get("descricao", ""),
    )


def detect_duplicate_payments(consolidated: dict) -> None:
    """
    Detecta pagamentos duplicados no JSON consolidado.

    A função não remove pagamentos.
    Ela apenas adiciona avisos em consolidated["avisos"].
    """
    seen = {}

    pagamentos = consolidated.get("pagamentos", [])

    for index, pagamento in enumerate(pagamentos):
        key = payment_key(pagamento)

        if key in seen:
            first_index = seen[key]

            consolidated["avisos"].append({
                "field": f"pagamentos[{index}]",
                "message": (
                    "Pagamento possivelmente duplicado. "
                    f"Já existe pagamento semelhante em pagamentos[{first_index}]."
                )
            })
        else:
            seen[key] = index


def list_extracted_files(input_dir: str) -> list[Path]:
    """
    Lista arquivos JSON de extração dentro de uma pasta.
    """
    directory = Path(input_dir)

    if not directory.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Não é uma pasta: {input_dir}")

    return sorted(directory.glob("*.json"))


def should_skip_invalid_extraction(config: dict | None) -> bool:
    """
    Decide se o pipeline deve ignorar extrações inválidas.

    Padrão:
    - fail_on_invalid_extraction = false
    - então arquivos inválidos são ignorados e registrados em skipped_files.
    """
    config = config or {}
    return not config.get("fail_on_invalid_extraction", False)


def should_fail_on_canonical_error(config: dict | None) -> bool:
    """
    Decide se erro canônico deve fazer o pipeline falhar.

    Padrão:
    - fail_on_canonical_error = true
    """
    config = config or {}
    return config.get("fail_on_canonical_error", True)


def should_detect_duplicates(config: dict | None) -> bool:
    """
    Decide se o pipeline deve detectar pagamentos duplicados.

    Padrão:
    - enable_duplicate_detection = true
    """
    config = config or {}
    return config.get("enable_duplicate_detection", True)


def should_generate_report(config: dict | None) -> bool:
    """
    Decide se o pipeline deve gerar relatório humano.

    Padrão:
    - enable_human_review_report = true
    """
    config = config or {}
    return config.get("enable_human_review_report", True)


def run_batch_pipeline(
    input_dir: str,
    output_json_path: str = DEFAULT_OUTPUT_JSON,
    output_report_path: str = DEFAULT_OUTPUT_REPORT,
    config: dict | None = None
) -> dict:
    """
    Executa o pipeline em lote:

    pasta de extrações
        -> valida cada extração
        -> converte cada extração em JSON canônico parcial
        -> consolida tudo em um JSON único
        -> detecta duplicidades simples
        -> valida JSON consolidado
        -> gera relatório
    """
    config = config or {}

    extracted_files = list_extracted_files(input_dir)

    consolidated = empty_canonical(config=config)

    processed_files = []
    skipped_files = []
    fatal_extraction_errors = []

    for file_path in extracted_files:
        extracted = load_json(str(file_path))
        extraction_validation = validate_extracted(extracted)

        if not extraction_validation["valid"]:
            invalid_item = {
                "file": str(file_path),
                "validation": extraction_validation
            }

            if should_skip_invalid_extraction(config):
                skipped_files.append(invalid_item)
                continue

            fatal_extraction_errors.append(invalid_item)
            continue

        partial_canonical = build_canonical_json(extracted)

        merge_canonical(
            consolidated,
            partial_canonical,
            source_file=str(file_path)
        )

        processed_files.append({
            "file": str(file_path),
            "validation": extraction_validation
        })

    if should_detect_duplicates(config):
        detect_duplicate_payments(consolidated)

    canonical_validation = validate_canonical_irpf(consolidated)

    Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_report_path).parent.mkdir(parents=True, exist_ok=True)

    consolidated = deduplicate_consolidated_records(consolidated)

    save_json(consolidated, output_json_path)

    report_generated = False

    if should_generate_report(config):
        report = generate_report(consolidated)
        save_report(report, output_report_path)
        report_generated = True

    return {
        "input_dir": input_dir,
        "output_json_path": output_json_path,
        "output_report_path": output_report_path,
        "report_generated": report_generated,
        "processed_files": processed_files,
        "skipped_files": skipped_files,
        "fatal_extraction_errors": fatal_extraction_errors,
        "canonical_validation": canonical_validation,
        "config": {
            "fail_on_invalid_extraction": config.get("fail_on_invalid_extraction", False),
            "fail_on_canonical_error": config.get("fail_on_canonical_error", True),
            "enable_duplicate_detection": config.get("enable_duplicate_detection", True),
            "enable_human_review_report": config.get("enable_human_review_report", True),
        }
    }


def print_validation_details(result: dict) -> None:
    """
    Imprime detalhes de validação do JSON consolidado.
    """
    validation = result["canonical_validation"]

    if validation["valid"]:
        print("Validação do JSON consolidado: válido.")
    else:
        print("Validação do JSON consolidado: inválido.")

    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])

    if errors:
        print("\nErros:")
        for error in errors:
            print(f"- {error['field']}: {error['message']}")

    if warnings:
        print("\nAvisos:")
        for warning in warnings:
            print(f"- {warning['field']}: {warning['message']}")


def print_skipped_files(result: dict) -> None:
    """
    Mostra arquivos ignorados por erro de validação da extração.
    """
    skipped_files = result["skipped_files"]

    if not skipped_files:
        return

    print("")
    print("Arquivos ignorados:")

    for item in skipped_files:
        print(f"- {item['file']}")

        validation = item["validation"]

        for error in validation.get("errors", []):
            print(f"  Erro: {error['field']}: {error['message']}")

        for warning in validation.get("warnings", []):
            print(f"  Aviso: {warning['field']}: {warning['message']}")


def print_fatal_extraction_errors(result: dict) -> None:
    """
    Mostra extrações inválidas que devem fazer o pipeline falhar.
    """
    fatal_errors = result.get("fatal_extraction_errors", [])

    if not fatal_errors:
        return

    print("")
    print("Extrações inválidas fatais:")

    for item in fatal_errors:
        print(f"- {item['file']}")

        validation = item["validation"]

        for error in validation.get("errors", []):
            print(f"  Erro: {error['field']}: {error['message']}")

        for warning in validation.get("warnings", []):
            print(f"  Aviso: {warning['field']}: {warning['message']}")


def print_processed_files(result: dict) -> None:
    """
    Mostra arquivos processados com sucesso.
    """
    processed_files = result["processed_files"]

    if not processed_files:
        return

    print("")
    print("Arquivos processados:")

    for item in processed_files:
        print(f"- {item['file']}")

        validation = item["validation"]

        for warning in validation.get("warnings", []):
            print(f"  Aviso: {warning['field']}: {warning['message']}")


def print_config_summary(result: dict) -> None:
    """
    Mostra resumo das flags de configuração usadas pelo pipeline.
    """
    config = result.get("config", {})

    print("")
    print("Configuração aplicada:")
    print(f"- fail_on_invalid_extraction: {config.get('fail_on_invalid_extraction')}")
    print(f"- fail_on_canonical_error: {config.get('fail_on_canonical_error')}")
    print(f"- enable_duplicate_detection: {config.get('enable_duplicate_detection')}")
    print(f"- enable_human_review_report: {config.get('enable_human_review_report')}")


def print_result(result: dict) -> None:
    """
    Mostra resultado geral do pipeline em lote.
    """
    print("Pipeline em lote finalizado.")
    print(f"Pasta de entrada: {result['input_dir']}")
    print(f"JSON consolidado: {result['output_json_path']}")

    if result.get("report_generated"):
        print(f"Relatório consolidado: {result['output_report_path']}")
    else:
        print("Relatório consolidado: não gerado por configuração.")

    print(f"Arquivos processados: {len(result['processed_files'])}")
    print(f"Arquivos ignorados: {len(result['skipped_files'])}")
    print(f"Extrações inválidas fatais: {len(result.get('fatal_extraction_errors', []))}")

    print_config_summary(result)
    print_processed_files(result)
    print_skipped_files(result)
    print_fatal_extraction_errors(result)

    print("")
    print_validation_details(result)


def parse_args(argv: list[str]) -> tuple[str, str, str, dict | None]:
    """
    Interpreta os argumentos de linha de comando.

    Modos suportados:

    1. Config:
        python3 tools/pipeline_batch.py --config config/project_config.json

    2. Pasta direta:
        python3 tools/pipeline_batch.py inputs/extracted

    3. Pasta direta com saídas explícitas:
        python3 tools/pipeline_batch.py inputs/extracted outputs/irpf.json outputs/irpf.report.md
    """
    if len(argv) == 3 and argv[1] == "--config":
        config_path = argv[2]
        config = load_config(config_path)
        input_dir, output_json, output_report = resolve_paths_from_config(config)
        return input_dir, output_json, output_report, config

    if len(argv) == 2:
        input_dir = argv[1]
        return input_dir, DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT, None

    if len(argv) == 4:
        input_dir = argv[1]
        output_json = argv[2]
        output_report = argv[3]
        return input_dir, output_json, output_report, None

    print("Uso:")
    print("python3 tools/pipeline_batch.py --config config/project_config.json")
    print("ou")
    print("python3 tools/pipeline_batch.py inputs/extracted")
    print("ou")
    print("python3 tools/pipeline_batch.py inputs/extracted outputs/irpf.json outputs/irpf.report.md")
    sys.exit(1)


def main() -> None:
    input_dir, output_json_path, output_report_path, config = parse_args(sys.argv)

    result = run_batch_pipeline(
        input_dir=input_dir,
        output_json_path=output_json_path,
        output_report_path=output_report_path,
        config=config
    )

    print_result(result)

    has_fatal_extraction_errors = bool(result.get("fatal_extraction_errors"))
    has_canonical_errors = not result["canonical_validation"]["valid"]
    must_fail_on_canonical = should_fail_on_canonical_error(config)

    if has_fatal_extraction_errors:
        sys.exit(1)

    if has_canonical_errors and must_fail_on_canonical:
        sys.exit(1)


if __name__ == "__main__":
    main()