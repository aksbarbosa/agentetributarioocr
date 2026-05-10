from pathlib import Path

from pipeline_batch import (
    load_config,
    resolve_paths_from_config,
    run_batch_pipeline,
    print_result,
)


DEFAULT_CONFIG_PATH = "config/project_config.json"


def main() -> None:
    """
    Executa o pipeline principal do projeto usando o arquivo padrão:

        config/project_config.json

    Uso:
        python3 tools/run_project.py
    """
    config_path = Path(DEFAULT_CONFIG_PATH)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {DEFAULT_CONFIG_PATH}"
        )

    config = load_config(str(config_path))

    input_dir, output_json_path, output_report_path = resolve_paths_from_config(config)

    result = run_batch_pipeline(
        input_dir=input_dir,
        output_json_path=output_json_path,
        output_report_path=output_report_path,
        config=config
    )

    print_result(result)

    if result["skipped_files"] or not result["canonical_validation"]["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()