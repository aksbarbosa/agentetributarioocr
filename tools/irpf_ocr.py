import subprocess
import sys


COMMANDS = {
    "setup": {
        "description": "Configura o projeto localmente, instala hooks e roda checagens.",
        "command": [sys.executable, "tools/setup_project.py"],
    },
    "status": {
        "description": "Mostra a estratégia OCR configurada e o próximo fluxo.",
        "command": [sys.executable, "tools/ocr_strategy_status.py"],
    },
    "run": {
        "description": "Executa o fluxo definido em config/ocr_config.json.",
        "command": [sys.executable, "tools/run_ocr_strategy.py"],
    },
    "continue": {
        "description": "Continua o fluxo após revisão manual conforme a estratégia OCR.",
        "command": [sys.executable, "tools/continue_after_ocr_strategy_review.py"],
    },
    "review": {
        "description": "Abre revisão interativa do pacote manual conforme a estratégia OCR.",
        "command": [sys.executable, "tools/review_ocr_strategy_pack.py"],
    },
    "check": {
        "description": "Roda validações e testes do projeto.",
        "command": [sys.executable, "tools/dev_check.py"],
    },
    "project-status": {
        "description": "Mostra status dos outputs e próximo passo provável.",
        "command": [sys.executable, "tools/project_status.py"],
    },
}


def print_help() -> None:
    print("IRPF OCR DEC")
    print("")
    print("Uso:")
    print("python3 tools/irpf_ocr.py <comando>")
    print("")
    print("Comandos:")

    for name, data in COMMANDS.items():
        print(f"- {name}: {data['description']}")

    print("")
    print("Exemplos:")
    print("python3 tools/irpf_ocr.py setup")
    print("python3 tools/irpf_ocr.py status")
    print("python3 tools/irpf_ocr.py run")
    print("python3 tools/irpf_ocr.py continue")
    print("python3 tools/irpf_ocr.py review")
    print("python3 tools/irpf_ocr.py check")


def parse_args(argv: list[str]) -> str:
    if len(argv) != 2:
        print_help()
        sys.exit(1)

    command_name = argv[1]

    if command_name in {"-h", "--help", "help"}:
        print_help()
        sys.exit(0)

    if command_name not in COMMANDS:
        print(f"Comando desconhecido: {command_name}")
        print("")
        print_help()
        sys.exit(1)

    return command_name


def run_command(command_name: str) -> int:
    data = COMMANDS[command_name]
    command = data["command"]

    print(f"Executando: {command_name}")
    print(data["description"])
    print("$ " + " ".join(command))
    print("")

    result = subprocess.run(command)

    return result.returncode


def main() -> None:
    command_name = parse_args(sys.argv)

    return_code = run_command(command_name)

    if return_code != 0:
        print("")
        print(f"Comando terminou com código {return_code}.")
        sys.exit(return_code)

    print("")
    print("Comando finalizado com sucesso.")


if __name__ == "__main__":
    main()
