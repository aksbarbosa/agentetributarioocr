import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


COMMANDS = [
    {
        "name": "Validar configuração",
        "command": [sys.executable, "tools/validate_config.py", "config/project_config.json"]
    },
    {
        "name": "Limpar outputs",
        "command": [sys.executable, "tools/clean_outputs.py"]
    },
    {
        "name": "Rodar projeto",
        "command": [sys.executable, "tools/run_project.py"]
    },
    {
        "name": "Rodar testes",
        "command": [sys.executable, "tests/run_tests.py"]
    },
]   


def run_command(name: str, command: list[str]) -> bool:
    """
    Executa um comando dentro da raiz do projeto.
    """
    print("")
    print(f"==> {name}")
    print("$ " + " ".join(command))

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        print(f"Falhou: {name}")
        return False

    print(f"OK: {name}")
    return True


def main() -> None:
    """
    Roda a checagem completa de desenvolvimento.

    Uso:
        python3 tools/dev_check.py
    """
    print("Iniciando checagem de desenvolvimento.")

    for item in COMMANDS:
        ok = run_command(
            name=item["name"],
            command=item["command"]
        )

        if not ok:
            print("")
            print("Checagem interrompida por erro.")
            sys.exit(1)

    print("")
    print("Checagem concluída com sucesso.")


if __name__ == "__main__":
    main()