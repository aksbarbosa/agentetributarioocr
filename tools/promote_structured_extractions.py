import json
import shutil
import subprocess
import sys
from pathlib import Path


def collect_json_files(input_dir: str) -> list[Path]:
    """
    Coleta arquivos JSON de uma pasta.
    """
    path = Path(input_dir)

    if not path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not path.is_dir():
        raise NotADirectoryError(f"Não é uma pasta: {input_dir}")

    return sorted(path.glob("*.json"))


def validate_extraction(path: Path) -> tuple[bool, str]:
    """
    Valida uma extração usando tools/validate_extracted.py.
    """
    result = subprocess.run(
        [sys.executable, "tools/validate_extracted.py", str(path)],
        capture_output=True,
        text=True,
    )

    output = (result.stdout or "") + (result.stderr or "")

    return result.returncode == 0, output.strip()


def load_json(path: Path) -> dict:
    """
    Carrega JSON.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def build_promoted_name(path: Path, data: dict) -> str:
    """
    Cria nome de destino para o arquivo promovido.

    Exemplo:
    source: testemedic.json
    document_type: recibo_medico
    destino: recibo_medico_testemedic.json
    """
    document_type = data.get("document_type", "documento")
    return f"{document_type}_{path.stem}.json"


def promote_file(source_path: Path, output_dir: str) -> dict:
    """
    Valida e copia uma extração estruturada para a pasta de destino.

    Regra de segurança:
    - Só promove se validate_extracted.py aprovar.
    - Só promove se requires_review estiver vazio.
    """
    is_valid, validation_output = validate_extraction(source_path)

    if not is_valid:
        return {
            "source_path": str(source_path),
            "status": "invalid",
            "destination_path": None,
            "validation_output": validation_output,
        }

    data = load_json(source_path)

    requires_review = data.get("requires_review", [])

    if requires_review:
        return {
            "source_path": str(source_path),
            "status": "requires_review",
            "destination_path": None,
            "validation_output": (
                "Extração válida, mas contém itens em requires_review; "
                "não será promovida automaticamente."
            ),
        }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    destination = output_path / build_promoted_name(source_path, data)

    shutil.copy2(source_path, destination)

    return {
        "source_path": str(source_path),
        "status": "promoted",
        "destination_path": str(destination),
        "validation_output": validation_output,
    }


def build_summary(results: list[dict]) -> dict:
    """
    Resume a promoção.
    """
    promoted_count = 0
    invalid_count = 0
    requires_review_count = 0

    for item in results:
        if item["status"] == "promoted":
            promoted_count += 1
        elif item["status"] == "invalid":
            invalid_count += 1
        elif item["status"] == "requires_review":
            requires_review_count += 1

    return {
        "promoted_count": promoted_count,
        "invalid_count": invalid_count,
        "requires_review_count": requires_review_count,
    }


def build_promotion_response(input_dir: str, output_dir: str) -> dict:
    """
    Promove extrações estruturadas válidas e sem revisão pendente.
    """
    files = collect_json_files(input_dir)
    results = []

    for file_path in files:
        results.append(promote_file(file_path, output_dir))

    summary = build_summary(results)

    return {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_files": len(files),
        "summary": summary,
        "results": results,
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_markdown_report(response: dict) -> str:
    """
    Gera relatório Markdown da promoção.
    """
    lines = []

    lines.append("# Relatório de promoção de extrações estruturadas")
    lines.append("")
    lines.append(f"Pasta de origem: `{response['input_dir']}`")
    lines.append(f"Pasta de destino: `{response['output_dir']}`")
    lines.append(f"Arquivos analisados: {response['total_files']}")
    lines.append("")

    summary = response["summary"]

    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Extrações promovidas: {summary['promoted_count']}")
    lines.append(f"- Extrações inválidas: {summary['invalid_count']}")
    lines.append(f"- Extrações com revisão pendente: {summary['requires_review_count']}")
    lines.append("")

    lines.append("## Arquivos")
    lines.append("")

    if response["results"]:
        for item in response["results"]:
            source_name = Path(item["source_path"]).name

            lines.append(f"### `{source_name}`")
            lines.append("")
            lines.append(f"- Status: `{item['status']}`")
            lines.append(f"- Destino: `{item['destination_path']}`")
            lines.append("")
            lines.append("#### Resultado da validação")
            lines.append("")
            if item["validation_output"]:
                lines.append("```text")
                lines.append(item["validation_output"])
                lines.append("```")
            else:
                lines.append("Sem saída de validação.")
            lines.append("")
    else:
        lines.append("Nenhum arquivo encontrado.")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva relatório Markdown.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def print_human_summary(response: dict, output_json: str, output_report: str) -> None:
    """
    Imprime resumo humano.
    """
    print("Promoção de extrações estruturadas finalizada.")
    print(f"Pasta de origem: {response['input_dir']}")
    print(f"Pasta de destino: {response['output_dir']}")
    print(f"Arquivos analisados: {response['total_files']}")
    print(f"JSON da promoção: {output_json}")
    print(f"Relatório da promoção: {output_report}")
    print("")

    summary = response["summary"]

    print("Resumo:")
    print(f"- Extrações promovidas: {summary['promoted_count']}")
    print(f"- Extrações inválidas: {summary['invalid_count']}")
    print(f"- Extrações com revisão pendente: {summary['requires_review_count']}")


def print_json_response(response: dict) -> None:
    """
    Imprime JSON no terminal.
    """
    print(json.dumps(response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, str, bool]:
    """
    Uso:
        python3 tools/promote_structured_extractions.py
        python3 tools/promote_structured_extractions.py --json
        python3 tools/promote_structured_extractions.py input_dir output_dir output.json output.report.md
        python3 tools/promote_structured_extractions.py input_dir output_dir output.json output.report.md --json
    """
    args = argv[1:]

    input_dir = "outputs/structured_extractions"
    output_dir = "inputs/extracted"
    output_json = "outputs/promote-structured-extractions.json"
    output_report = "outputs/promote-structured-extractions.report.md"
    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    if len(args) == 0:
        return input_dir, output_dir, output_json, output_report, print_json

    if len(args) == 4:
        input_dir = args[0]
        output_dir = args[1]
        output_json = args[2]
        output_report = args[3]
        return input_dir, output_dir, output_json, output_report, print_json

    print("Uso:")
    print("python3 tools/promote_structured_extractions.py")
    print("python3 tools/promote_structured_extractions.py --json")
    print(
        "python3 tools/promote_structured_extractions.py "
        "input_dir output_dir output.json output.report.md"
    )
    print(
        "python3 tools/promote_structured_extractions.py "
        "input_dir output_dir output.json output.report.md --json"
    )
    sys.exit(1)


def main() -> None:
    input_dir, output_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    response = build_promotion_response(input_dir, output_dir)
    report = generate_markdown_report(response)

    save_json(response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(response)
    else:
        print_human_summary(response, output_json, output_report)


if __name__ == "__main__":
    main()