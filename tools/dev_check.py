import subprocess
import sys


EXECUTED_STEPS = []


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

    EXECUTED_STEPS.append(title)
    print(f"OK: {title}")


def print_final_summary() -> None:
    """
    Imprime resumo final da checagem.
    """
    print("")
    print("Checagem concluída com sucesso.")
    print("")
    print("Etapas executadas:")

    for step in EXECUTED_STEPS:
        print(f"- {step}")


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

    print_final_summary()


if __name__ == "__main__":
    main()