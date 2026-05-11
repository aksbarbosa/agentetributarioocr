import json
import sys
from pathlib import Path

from agent_simulator import build_agent_response


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


def build_summary(decisions: list[dict]) -> dict:
    """
    Cria resumo das decisões.
    """
    by_document_type = {}
    by_confidence = {}
    should_continue_count = 0

    for item in decisions:
        classification = item["classification"]
        decision = item["decision"]

        document_type = classification["document_type"]
        confidence = classification["confidence"]

        by_document_type[document_type] = by_document_type.get(document_type, 0) + 1
        by_confidence[confidence] = by_confidence.get(confidence, 0) + 1

        if decision["should_continue"]:
            should_continue_count += 1

    return {
        "by_document_type": by_document_type,
        "by_confidence": by_confidence,
        "should_continue_count": should_continue_count,
        "requires_manual_review_count": len(decisions) - should_continue_count,
    }


def build_batch_response(input_dir: str) -> dict:
    """
    Simula decisões de agente para todos os arquivos .txt de uma pasta.
    """
    files = collect_text_files(input_dir)

    decisions = []

    for file_path in files:
        response = build_agent_response(str(file_path))
        decisions.append(response)

    summary = build_summary(decisions)

    return {
        "input_dir": input_dir,
        "total_files": len(files),
        "summary": summary,
        "decisions": decisions,
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def generate_markdown_report(batch_response: dict) -> str:
    """
    Gera relatório Markdown das decisões em lote.
    """
    lines = []

    lines.append("# Relatório de simulação local do agente")
    lines.append("")
    lines.append(f"Pasta analisada: `{batch_response['input_dir']}`")
    lines.append(f"Arquivos analisados: {batch_response['total_files']}")
    lines.append("")

    summary = batch_response["summary"]

    lines.append("## Resumo por tipo de documento")
    lines.append("")

    if summary["by_document_type"]:
        for document_type, count in sorted(summary["by_document_type"].items()):
            lines.append(f"- `{document_type}`: {count}")
    else:
        lines.append("Nenhum documento analisado.")

    lines.append("")
    lines.append("## Resumo por confiança")
    lines.append("")

    if summary["by_confidence"]:
        for confidence, count in sorted(summary["by_confidence"].items()):
            lines.append(f"- `{confidence}`: {count}")
    else:
        lines.append("Nenhuma classificação disponível.")

    lines.append("")
    lines.append("## Decisões")
    lines.append("")

    for index, item in enumerate(batch_response["decisions"], start=1):
        classification = item["classification"]
        decision = item["decision"]

        lines.append(f"### Documento {index}")
        lines.append("")
        lines.append(f"- Arquivo: `{item['input_path']}`")
        lines.append(f"- Tipo provável: `{classification['document_type']}`")
        lines.append(f"- Rótulo: {classification['label']}")
        lines.append(f"- Confiança: `{classification['confidence']}`")
        lines.append(f"- Deve continuar: `{decision['should_continue']}`")
        lines.append(f"- Schema recomendado: `{decision['schema_path']}`")
        lines.append(f"- Próximo passo: {decision['next_step']}")
        lines.append("")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva relatório Markdown em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        file.write(report)


def print_human_summary(batch_response: dict, json_path: str, report_path: str) -> None:
    """
    Imprime resumo humano.
    """
    print("Simulação local do agente em lote finalizada.")
    print(f"Pasta analisada: {batch_response['input_dir']}")
    print(f"Arquivos analisados: {batch_response['total_files']}")
    print(f"JSON de decisões: {json_path}")
    print(f"Relatório de decisões: {report_path}")
    print("")

    print("Resumo por tipo:")
    for document_type, count in sorted(batch_response["summary"]["by_document_type"].items()):
        print(f"- {document_type}: {count}")

    print("")
    print("Resumo por confiança:")
    for confidence, count in sorted(batch_response["summary"]["by_confidence"].items()):
        print(f"- {confidence}: {count}")


def print_json_response(batch_response: dict) -> None:
    """
    Imprime a resposta em lote em JSON no terminal.
    """
    print(json.dumps(batch_response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, bool]:
    """
    Uso:
        python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
        python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
        python3 tools/agent_batch_simulator.py tests/fixtures/raw_text output.json output.report.md
        python3 tools/agent_batch_simulator.py tests/fixtures/raw_text output.json output.report.md --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/agent_batch_simulator.py pasta_de_textos")
        print("python3 tools/agent_batch_simulator.py pasta_de_textos --json")
        print("python3 tools/agent_batch_simulator.py pasta_de_textos output.json output.report.md")
        print("python3 tools/agent_batch_simulator.py pasta_de_textos output.json output.report.md --json")
        sys.exit(1)

    input_dir = argv[1]
    args = argv[2:]

    output_json = "outputs/agent-decisions.json"
    output_report = "outputs/agent-decisions.report.md"
    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    if len(args) == 0:
        return input_dir, output_json, output_report, print_json

    if len(args) == 2:
        output_json = args[0]
        output_report = args[1]
        return input_dir, output_json, output_report, print_json

    print("Uso:")
    print("python3 tools/agent_batch_simulator.py pasta_de_textos")
    print("python3 tools/agent_batch_simulator.py pasta_de_textos --json")
    print("python3 tools/agent_batch_simulator.py pasta_de_textos output.json output.report.md")
    print("python3 tools/agent_batch_simulator.py pasta_de_textos output.json output.report.md --json")
    sys.exit(1)


def main() -> None:
    input_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    batch_response = build_batch_response(input_dir)
    report = generate_markdown_report(batch_response)

    save_json(batch_response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(batch_response)
    else:
        print_human_summary(batch_response, output_json, output_report)


if __name__ == "__main__":
    main()