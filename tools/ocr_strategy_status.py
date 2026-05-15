import json
import sys
from pathlib import Path


DEFAULT_CONFIG_PATH = "config/ocr_config.json"

STRATEGY_COMMANDS = {
    "normal": "python3 tools/run_mvp_flow.py",
    "prepared": "python3 tools/run_prepared_raw_flow.py",
    "best": "python3 tools/run_best_mvp_flow.py",
}


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def parse_args(argv: list[str]) -> str:
    if len(argv) == 1:
        return DEFAULT_CONFIG_PATH

    if len(argv) == 2:
        return argv[1]

    print("Uso:")
    print("python3 tools/ocr_strategy_status.py")
    print("python3 tools/ocr_strategy_status.py config/ocr_config.json")
    sys.exit(1)


def main() -> None:
    config_path = parse_args(sys.argv)
    config = load_json(config_path)

    strategy = config.get("ocr_strategy")
    preprocessing = config.get("preprocessing", {})
    selection = config.get("selection", {})
    safety = config.get("safety", {})

    command = STRATEGY_COMMANDS.get(strategy)

    print("Status da estratégia OCR")
    print("")
    print(f"Arquivo de configuração: {config_path}")
    print(f"Estratégia configurada: {strategy}")
    print(f"Comando correspondente: {command or 'estratégia inválida'}")
    print("")
    print("Pré-processamento:")
    print(f"- Ativo: {preprocessing.get('enabled')}")
    print(f"- Escala: {preprocessing.get('scale_factor')}")
    print(f"- Contraste: {preprocessing.get('contrast_factor')}")
    print(f"- Nitidez: {preprocessing.get('sharpness_factor')}")
    print(f"- Limiar de binarização: {preprocessing.get('binarization_threshold')}")
    print("")
    print("Seleção:")
    print(f"- Método: {selection.get('method')}")
    print(f"- Preferir OCR normal em empate: {selection.get('prefer_original_on_tie')}")
    print("")
    print("Segurança:")
    print(f"- Permitir erros parciais no pré-processamento: {safety.get('allow_partial_preprocessing_errors')}")
    print(f"- Permitir falha de pré-triagem: {safety.get('allow_preflight_failure')}")
    print(f"- Revisar identificadores inválidos: {safety.get('require_manual_review_for_invalid_identifiers')}")

    if not command:
        sys.exit(1)


if __name__ == "__main__":
    main()
