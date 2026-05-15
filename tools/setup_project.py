import subprocess
import sys
from pathlib import Path


REQUIRED_PATHS = [
    Path("tools"),
    Path("tests"),
    Path("config/project_config.json"),
    Path("config/ocr_config.json"),
    Path("requirements.txt"),
]


def run_command(title: str, command: list[str]) -> None:
    print("")
    print(f"==> {title}")
    print("$ " + " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"Falhou: {title}")
        sys.exit(result.returncode)

    print(f"OK: {title}")


def ensure_project_root() -> None:
    missing = [str(path) for path in REQUIRED_PATHS if not path.exists()]

    if missing:
        print("Este comando deve ser executado na raiz do projeto.")
        print("")
        print("Itens esperados não encontrados:")

        for item in missing:
            print(f"- {item}")

        sys.exit(1)


def warn_if_not_in_venv() -> None:
    if sys.prefix == sys.base_prefix:
        print("")
        print("Aviso: você não parece estar dentro de um ambiente virtual.")
        print("Recomendado:")
        print("")
        print("python3 -m venv .venv")
        print("source .venv/bin/activate")
        print("pip install -r requirements.txt")
        print("")


def main() -> None:
    print("Iniciando setup do projeto IRPF OCR DEC.")

    ensure_project_root()
    warn_if_not_in_venv()

    run_command(
        "Instalar hooks de Git",
        [
            sys.executable,
            "tools/install_git_hooks.py",
        ],
    )

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
        "Rodar checagem completa",
        [
            sys.executable,
            "tools/dev_check.py",
        ],
    )

    print("")
    print("Setup concluído com sucesso.")
    print("")
    print("Comandos principais:")
    print("- python3 tools/irpf_ocr.py status")
    print("- python3 tools/irpf_ocr.py run")
    print("- python3 tools/irpf_ocr.py continue")
    print("- python3 tools/irpf_ocr.py check")


if __name__ == "__main__":
    main()
