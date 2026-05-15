import subprocess
import sys


def run_command(title: str, command: list[str]) -> None:
    """
    Executa um comando de checagem de desenvolvimento.
    """
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")


def main() -> None:
    """
    Executa checagens principais do projeto.
    """
    print("Iniciando checagem de desenvolvimento.")

    run_command(
        "Validar configuração principal",
        [
            sys.executable,
            "tools/validate_config.py",
            "config/project_config.json",
        ],
    )

    run_command(
        "Validar configuração OCR",
        [
            sys.executable,
            "tools/validate_ocr_config.py",
        ],
    )

    run_command(
        "Rodar testes unitários",
        [
            sys.executable,
            "tests/run_tests.py",
        ],
    )

    print("")
    print("Checagem concluída com sucesso.")


if __name__ == "__main__":
    main()
