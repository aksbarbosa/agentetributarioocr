import json
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG_PATH = "config/ocr_config.json"


PACK_BY_STRATEGY = {
    "normal": "outputs/manual-review-pack.json",
    "best": "outputs/manual-review-pack-best.json",
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


def get_pack_path(strategy: str) -> str | None:
    return PACK_BY_STRATEGY.get(strategy)


def parse_args(argv: list[str]) -> str:
    if len(argv) == 1:
        return DEFAULT_CONFIG_PATH

    if len(argv) == 2:
        return argv[1]

    print("Uso:")
    print("python3 tools/review_ocr_strategy_pack.py")
    print("python3 tools/review_ocr_strategy_pack.py config/ocr_config.json")
    sys.exit(1)


def main() -> None:
    config_path = parse_args(sys.argv)
    config = load_json(config_path)
    strategy = get_strategy(config)

    pack_path = get_pack_path(strategy)

    print("Revisão interativa conforme estratégia OCR.")
    print(f"Arquivo de configuração: {config_path}")
    print(f"Estratégia OCR: {strategy}")

    if pack_path is None:
        print("")
        print("A estratégia 'prepared' ainda não possui pacote canônico de revisão automática.")
        print("Use manualmente:")
        print("python3 tools/review_pack_interactive.py <pacote.json>")
        sys.exit(1)

    if not Path(pack_path).exists():
        print("")
        print(f"Pacote de revisão não encontrado: {pack_path}")
        print("")
        print("Execute primeiro:")
        print("python3 tools/irpf_ocr.py run")
        sys.exit(1)

    command = [
        sys.executable,
        "tools/review_pack_interactive.py",
        pack_path,
    ]

    print(f"Pacote selecionado: {pack_path}")
    print("$ " + " ".join(command))
    print("")

    result = subprocess.run(command)

    if result.returncode != 0:
        print("")
        print(f"Revisão interativa terminou com código {result.returncode}.")
        sys.exit(result.returncode)

    print("")
    print("Revisão interativa finalizada com sucesso.")
    print("")
    print("Próximo passo:")
    print("python3 tools/irpf_ocr.py continue")


if __name__ == "__main__":
    main()
