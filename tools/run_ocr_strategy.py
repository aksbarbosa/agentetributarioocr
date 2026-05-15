import json
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG_PATH = "config/ocr_config.json"


STRATEGY_COMMANDS = {
    "normal": [sys.executable, "tools/run_mvp_flow.py"],
    "prepared": [sys.executable, "tools/run_prepared_raw_flow.py"],
    "best": [sys.executable, "tools/run_best_mvp_flow.py"],
}


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def get_strategy(config: dict) -> str:
    strategy = config.get("ocr_strategy")

    if strategy not in STRATEGY_COMMANDS:
        accepted = ", ".join(sorted(STRATEGY_COMMANDS))
        raise ValueError(
            f"ocr_strategy inválida: {strategy}. Valores aceitos: {accepted}"
        )

    return strategy


def run_strategy(strategy: str) -> int:
    command = STRATEGY_COMMANDS[strategy]

    print("Executando estratégia OCR configurada.")
    print(f"Estratégia: {strategy}")
    print("$ " + " ".join(command))
    print("")

    result = subprocess.run(command)

    return result.returncode


def parse_args(argv: list[str]) -> str:
    if len(argv) == 1:
        return DEFAULT_CONFIG_PATH

    if len(argv) == 2:
        return argv[1]

    print("Uso:")
    print("python3 tools/run_ocr_strategy.py")
    print("python3 tools/run_ocr_strategy.py config/ocr_config.json")
    sys.exit(1)


def main() -> None:
    config_path = parse_args(sys.argv)

    config = load_json(config_path)
    strategy = get_strategy(config)

    return_code = run_strategy(strategy)

    if return_code != 0:
        print("")
        print(f"Fluxo OCR terminou com código {return_code}.")
        sys.exit(return_code)

    print("")
    print("Fluxo OCR configurado finalizado com sucesso.")


if __name__ == "__main__":
    main()
