import json
import sys
from pathlib import Path

from pipeline_batch import run_batch_pipeline


DEFAULT_INPUT_DIR = "inputs/extracted"
DEFAULT_OUTPUT_JSON = "outputs/irpf-consolidado.json"
DEFAULT_OUTPUT_REPORT = "outputs/irpf-consolidado.report.md"
DEFAULT_CONFIG_PATH = "config/project_config.json"


def load_json(path: str) -> dict:
    """
    Carrega um arquivo JSON.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """
    Carrega a configuração do projeto.
    """
    return load_json(config_path)


def parse_args(argv: list[str]) -> tuple[str, str, str, str]:
    """
    Uso:
        python3 tools/run_project.py
        python3 tools/run_project.py input_dir
        python3 tools/run_project.py input_dir output_json output_report
        python3 tools/run_project.py input_dir output_json output_report config_path
    """
    args = argv[1:]

    input_dir = DEFAULT_INPUT_DIR
    output_json = DEFAULT_OUTPUT_JSON
    output_report = DEFAULT_OUTPUT_REPORT
    config_path = DEFAULT_CONFIG_PATH

    if len(args) == 0:
        return input_dir, output_json, output_report, config_path

    if len(args) == 1:
        input_dir = args[0]
        return input_dir, output_json, output_report, config_path

    if len(args) == 3:
        input_dir = args[0]
        output_json = args[1]
        output_report = args[2]
        return input_dir, output_json, output_report, config_path

    if len(args) == 4:
        input_dir = args[0]
        output_json = args[1]
        output_report = args[2]
        config_path = args[3]
        return input_dir, output_json, output_report, config_path

    print("Uso:")
    print("python3 tools/run_project.py")
    print("python3 tools/run_project.py input_dir")
    print("python3 tools/run_project.py input_dir output_json output_report")
    print("python3 tools/run_project.py input_dir output_json output_report config_path")
    sys.exit(1)


def get_summary_value(result: dict, key: str, default=0):
    """
    Busca uma chave primeiro em result['summary'] e depois no próprio result.
    Isso deixa o script tolerante a pequenas mudanças no formato de retorno.
    """
    summary = result.get("summary", {})

    if isinstance(summary, dict) and key in summary:
        return summary[key]

    return result.get(key, default)


def print_config(config: dict) -> None:
    """
    Imprime as principais opções de configuração.
    """
    print("")
    print("Configuração aplicada:")
    print(f"- fail_on_invalid_extraction: {config.get('fail_on_invalid_extraction')}")
    print(f"- fail_on_canonical_error: {config.get('fail_on_canonical_error')}")
    print(f"- enable_duplicate_detection: {config.get('enable_duplicate_detection')}")
    print(f"- enable_human_review_report: {config.get('enable_human_review_report')}")


def print_processed_files(result: dict) -> None:
    """
    Imprime arquivos processados e avisos, quando disponíveis.
    """
    processed_files = (
        result.get("processed_files")
        or result.get("processed")
        or result.get("files_processed")
        or []
    )

    if not processed_files:
        return

    print("")
    print("Arquivos processados:")

    for item in processed_files:
        if isinstance(item, str):
            print(f"- {item}")
            continue

        if not isinstance(item, dict):
            print(f"- {item}")
            continue

        path = (
            item.get("file_path")
            or item.get("path")
            or item.get("input_path")
            or item.get("source_file")
            or item.get("file")
            or "arquivo_desconhecido"
        )

        print(f"- {path}")

        warnings = item.get("warnings") or item.get("avisos") or []

        for warning in warnings:
            print(f"  Aviso: {warning}")


def collect_validation_errors(result: dict) -> list:
    """
    Coleta erros de validação em diferentes formatos possíveis de retorno.
    """
    validation = result.get("validation", {})
    canonical_validation = result.get("canonical_validation", {})

    errors = (
        result.get("errors")
        or validation.get("errors")
        or canonical_validation.get("errors")
        or []
    )

    return errors


def is_canonical_valid(result: dict) -> bool:
    """
    Determina se o JSON consolidado é válido.

    Considera diferentes formatos possíveis:
    - result['is_valid']
    - result['validation']['is_valid']
    - result['canonical_validation']['is_valid']
    - ausência de erros
    """
    validation = result.get("validation", {})
    canonical_validation = result.get("canonical_validation", {})

    if result.get("is_valid") is False:
        return False

    if validation.get("is_valid") is False:
        return False

    if canonical_validation.get("is_valid") is False:
        return False

    errors = collect_validation_errors(result)

    if errors:
        return False

    if result.get("is_valid") is True:
        return True

    if validation.get("is_valid") is True:
        return True

    if canonical_validation.get("is_valid") is True:
        return True

    return True


def print_validation_status(result: dict) -> None:
    """
    Imprime o status de validação do JSON consolidado.
    """
    errors = collect_validation_errors(result)

    if is_canonical_valid(result):
        print("")
        print("Validação do JSON consolidado: válido.")
        return

    print("")
    print("Validação do JSON consolidado: inválido.")

    for error in errors:
        print(f"- {error}")


def print_human_summary(
    result: dict,
    input_dir: str,
    output_json: str,
    output_report: str,
    config: dict,
) -> None:
    """
    Imprime resumo humano do pipeline.
    """
    processed_count = get_summary_value(result, "processed_count", 0)
    ignored_count = get_summary_value(result, "ignored_count", 0)
    fatal_invalid_count = get_summary_value(result, "fatal_invalid_count", 0)

    if processed_count == 0:
        processed_count = get_summary_value(result, "arquivos_processados", 0)

    if ignored_count == 0:
        ignored_count = get_summary_value(result, "arquivos_ignorados", 0)

    if fatal_invalid_count == 0:
        fatal_invalid_count = get_summary_value(result, "fatal_invalid_extractions", 0)

    print("Pipeline em lote finalizado.")
    print(f"Pasta de entrada: {input_dir}")
    print(f"JSON consolidado: {output_json}")
    print(f"Relatório consolidado: {output_report}")
    print(f"Arquivos processados: {processed_count}")
    print(f"Arquivos ignorados: {ignored_count}")
    print(f"Extrações inválidas fatais: {fatal_invalid_count}")

    print_config(config)
    print_processed_files(result)
    print_validation_status(result)


def should_fail_on_invalid_canonical(result: dict, config: dict) -> bool:
    """
    Decide se o script deve retornar erro quando o JSON consolidado for inválido.
    """
    fail_on_canonical_error = config.get("fail_on_canonical_error", True)

    if not fail_on_canonical_error:
        return False

    return not is_canonical_valid(result)


def main() -> None:
    input_dir, output_json, output_report, config_path = parse_args(sys.argv)

    config = load_config(config_path)

    result = run_batch_pipeline(
        input_dir=input_dir,
        output_json_path=output_json,
        output_report_path=output_report,
        config=config,
    )

    print_human_summary(
        result=result,
        input_dir=input_dir,
        output_json=output_json,
        output_report=output_report,
        config=config,
    )

    if should_fail_on_invalid_canonical(result, config):
        print("")
        print("Falha: JSON consolidado inválido.")
        sys.exit(1)


if __name__ == "__main__":
    main()