import json
import sys
from pathlib import Path

from extract_structured_from_text import build_structured_extraction


def collect_text_files(input_dir: str) -> list[Path]:
    """
    Coleta arquivos .txt de uma pasta.
    """
    path = Path(input_dir)

    if not path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not path.is_dir():
        raise NotADirectoryError(f"Não é uma pasta: {input_dir}")

    return sorted(path.glob("*.txt"))


def safe_json_name(text_path: Path) -> str:
    """
    Cria nome seguro para a extração estruturada JSON.
    """
    return f"{text_path.stem}.json"


def should_save_extraction(response: dict) -> bool:
    """
    Define se a extração deve ser salva como JSON individual.

    Salva apenas tipos com extração estruturada automática implementada.
    """
    document_type = response["extraction"]["document_type"]

    return document_type in {
        "recibo_medico",
        "informe_rendimentos_pj",
        "plano_saude",
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def build_summary(results: list[dict]) -> dict:
    """
    Resume os resultados do lote.
    """
    by_document_type = {}
    by_status = {}
    saved_count = 0
    requires_review_count = 0

    for item in results:
        document_type = item["document_type"]
        status = item["status"]

        by_document_type[document_type] = by_document_type.get(document_type, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

        if status == "saved":
            saved_count += 1

        if status == "requires_review":
            requires_review_count += 1

    return {
        "by_document_type": by_document_type,
        "by_status": by_status,
        "saved_count": saved_count,
        "requires_review_count": requires_review_count,
    }


def build_batch_response(input_dir: str, output_dir: str) -> dict:
    """
    Gera extrações estruturadas em lote a partir de textos extraídos.
    """
    files = collect_text_files(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    for file_path in files:
        response = build_structured_extraction(str(file_path))
        extraction = response["extraction"]
        classification = response["classification"]

        saved_output_path = None

        if should_save_extraction(response):
            saved_output_path = output_path / safe_json_name(file_path)
            save_json(extraction, str(saved_output_path))
            status = "saved"
        else:
            status = "requires_review"

        results.append(
            {
                "input_path": str(file_path),
                "document_type": extraction["document_type"],
                "classification_confidence": classification["confidence"],
                "status": status,
                "output_path": str(saved_output_path) if saved_output_path else None,
                "requires_review_count": len(extraction.get("requires_review", [])),
                "classification": classification,
                "extraction": extraction,
            }
        )

    summary = build_summary(results)

    return {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_files": len(files),
        "summary": summary,
        "results": results,
    }


def generate_markdown_report(batch_response: dict) -> str:
    """
    Gera relatório Markdown do lote de extrações estruturadas.
    """
    lines = []

    lines.append("# Relatório de extração estruturada em lote")
    lines.append("")
    lines.append(f"Pasta de entrada: `{batch_response['input_dir']}`")
    lines.append(f"Pasta de saída: `{batch_response['output_dir']}`")
    lines.append(f"Arquivos analisados: {batch_response['total_files']}")
    lines.append("")

    summary = batch_response["summary"]

    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Extrações salvas: {summary['saved_count']}")
    lines.append(f"- Arquivos que exigem revisão: {summary['requires_review_count']}")
    lines.append("")

    lines.append("## Por tipo de documento")
    lines.append("")

    if summary["by_document_type"]:
        for document_type, count in sorted(summary["by_document_type"].items()):
            lines.append(f"- `{document_type}`: {count}")
    else:
        lines.append("Nenhum arquivo analisado.")

    lines.append("")
    lines.append("## Por status")
    lines.append("")

    if summary["by_status"]:
        for status, count in sorted(summary["by_status"].items()):
            lines.append(f"- `{status}`: {count}")
    else:
        lines.append("Nenhum status disponível.")

    lines.append("")
    lines.append("## Arquivos")
    lines.append("")

    if batch_response["results"]:
        for item in batch_response["results"]:
            lines.append(f"### `{Path(item['input_path']).name}`")
            lines.append("")
            lines.append(f"- Tipo: `{item['document_type']}`")
            lines.append(f"- Confiança da classificação: `{item['classification_confidence']}`")
            lines.append(f"- Status: `{item['status']}`")
            lines.append(f"- Saída: `{item['output_path']}`")
            lines.append(f"- Itens de revisão: {item['requires_review_count']}")
            lines.append("")
    else:
        lines.append("Nenhum arquivo analisado.")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva relatório Markdown.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        file.write(report)


def print_human_summary(batch_response: dict, output_json: str, output_report: str) -> None:
    """
    Imprime resumo humano.
    """
    print("Extração estruturada em lote finalizada.")
    print(f"Pasta de entrada: {batch_response['input_dir']}")
    print(f"Pasta de saída: {batch_response['output_dir']}")
    print(f"Arquivos analisados: {batch_response['total_files']}")
    print(f"JSON do lote: {output_json}")
    print(f"Relatório do lote: {output_report}")
    print("")

    summary = batch_response["summary"]

    print("Resumo:")
    print(f"- Extrações salvas: {summary['saved_count']}")
    print(f"- Arquivos que exigem revisão: {summary['requires_review_count']}")


def print_json_response(batch_response: dict) -> None:
    """
    Imprime JSON no terminal.
    """
    print(json.dumps(batch_response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, str, bool]:
    """
    Uso:
        python3 tools/extract_structured_batch.py input_text_dir
        python3 tools/extract_structured_batch.py input_text_dir --json
        python3 tools/extract_structured_batch.py input_text_dir output_dir output.json output.report.md
        python3 tools/extract_structured_batch.py input_text_dir output_dir output.json output.report.md --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/extract_structured_batch.py input_text_dir")
        print("python3 tools/extract_structured_batch.py input_text_dir --json")
        print(
            "python3 tools/extract_structured_batch.py "
            "input_text_dir output_dir output.json output.report.md"
        )
        print(
            "python3 tools/extract_structured_batch.py "
            "input_text_dir output_dir output.json output.report.md --json"
        )
        sys.exit(1)

    input_dir = argv[1]
    args = argv[2:]

    output_dir = "outputs/structured_extractions"
    output_json = "outputs/structured-extractions-batch.json"
    output_report = "outputs/structured-extractions-batch.report.md"
    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    if len(args) == 0:
        return input_dir, output_dir, output_json, output_report, print_json

    if len(args) == 3:
        output_dir = args[0]
        output_json = args[1]
        output_report = args[2]
        return input_dir, output_dir, output_json, output_report, print_json

    print("Uso inválido.")
    print("python3 tools/extract_structured_batch.py input_text_dir")
    print("python3 tools/extract_structured_batch.py input_text_dir --json")
    print(
        "python3 tools/extract_structured_batch.py "
        "input_text_dir output_dir output.json output.report.md"
    )
    print(
        "python3 tools/extract_structured_batch.py "
        "input_text_dir output_dir output.json output.report.md --json"
    )
    sys.exit(1)


def main() -> None:
    input_dir, output_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    batch_response = build_batch_response(input_dir, output_dir)
    report = generate_markdown_report(batch_response)

    save_json(batch_response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(batch_response)
    else:
        print_human_summary(batch_response, output_json, output_report)


if __name__ == "__main__":
    main()