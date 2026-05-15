import json
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG_PATH = "config/ocr_config.json"


CONTINUATION_COMMANDS = {
    "normal": [sys.executable, "tools/continue_after_manual_review.py"],
    "best": [sys.executable, "tools/continue_after_best_manual_review.py"],
}


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def get_strategy(config: dict) -> str:
    strategy = config.get("ocr_strategy")

    if strategy not in {"normal", "prepared", "best"}:
        raise ValueError(
            f"ocr_strategy inválida: {strategy}. "
            "Valores aceitos: normal, prepared, best"
        )

    return strategy


def get_continuation_command(strategy: str) -> list[str] | None:
    return CONTINUATION_COMMANDS.get(strategy)


def parse_args(argv: list[str]) -> str:
    if len(argv) == 1:
        return DEFAULT_CONFIG_PATH

    if len(argv) == 2:
        return argv[1]

    print("Uso:")
    print("python3 tools/continue_after_ocr_strategy_review.py")
    print("python3 tools/continue_after_ocr_strategy_review.py config/ocr_config.json")
    sys.exit(1)


def main() -> None:
    config_path = parse_args(sys.argv)
    config = load_json(config_path)
    strategy = get_strategy(config)

    command = get_continuation_command(strategy)

    print("Continuação pós-revisão baseada na estratégia OCR.")
    print(f"Arquivo de configuração: {config_path}")
    print(f"Estratégia OCR: {strategy}")

    if command is None:
        print("")
        print("A estratégia 'prepared' ainda não possui continuação canônica completa.")
        print("Use uma destas opções:")
        print("- mudar config/ocr_config.json para 'normal' ou 'best';")
        print("- ou rodar manualmente o fluxo preparado até revisão.")
        sys.exit(1)

    print("$ " + " ".join(command))
    print("")

    result = subprocess.run(command)

    if result.returncode != 0:
        print("")
        print(f"Continuação terminou com código {result.returncode}.")
        sys.exit(result.returncode)

    print("")
    print("Continuação pós-revisão finalizada com sucesso.")


if __name__ == "__main__":
    main()
