import subprocess
import sys


def run_step(title: str, command: list[str]) -> None:
    """
    Executa uma etapa da checagem de desenvolvimento.
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
    print("Iniciando checagem de desenvolvimento.")

    run_step(
        "Validar configuração",
        [sys.executable, "tools/validate_config.py", "config/project_config.json"],
    )

    run_step(
        "Limpar outputs",
        [sys.executable, "tools/clean_outputs.py"],
    )

    run_step(
        "Rodar pré-triagem de documentos",
        [sys.executable, "tools/preflight_documents.py", "tests/fixtures/raw_text"],
    )

    run_step(
        "Rodar projeto",
        [sys.executable, "tools/run_project.py"],
    )

    run_step(
        "Rodar testes",
        [sys.executable, "tests/run_tests.py"],
    )

    print("")
    print("Checagem concluída com sucesso.")


if __name__ == "__main__":
    main()