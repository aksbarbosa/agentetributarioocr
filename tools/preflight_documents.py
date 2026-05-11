import json
import sys
from pathlib import Path

from agent_batch_simulator import build_batch_response


def build_preflight_response(input_dir: str) -> dict:
    """
    Executa a pré-triagem dos documentos.

    A pré-triagem usa o simulador em lote para classificar textos brutos
    e decide se o fluxo pode avançar para extração estruturada.
    """
    batch_response = build_batch_response(input_dir)

    recommended_action = batch_response["recommended_action"]

    status = "ready" if recommended_action["can_continue"] else "blocked"

    blocking_documents = [
        item for item in batch_response["decisions"]
        if not item["decision"]["should_continue"]
    ]

    return {
        "input_dir": input_dir,
        "status": status,
        "can_continue": recommended_action["can_continue"],
        "message": recommended_action["message"],
        "next_step": recommended_action["next_step"],
        "summary": batch_response["summary"],
        "blocking_documents": blocking_documents,
        "batch_response": batch_response,
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def generate_markdown_report(preflight_response: dict) -> str:
    """
    Gera relatório Markdown da pré-triagem.
    """
    lines = []

    lines.append("# Relatório de pré-triagem de documentos")
    lines.append("")
    lines.append(f"Pasta analisada: `{preflight_response['input_dir']}`")
    lines.append(f"Status: `{preflight_response['status']}`")
    lines.append(f"Pode continuar: `{preflight_response['can_continue']}`")
    lines.append("")

    lines.append("## Mensagem")
    lines.append("")
    lines.append(preflight_response["message"])
    lines.append("")

    lines.append("## Próximo passo")
    lines.append("")
    lines.append(preflight_response["next_step"])
    lines.append("")

    summary = preflight_response["summary"]

    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Documentos aptos a continuar: {summary['should_continue_count']}")
    lines.append(f"- Documentos que exigem revisão manual: {summary['requires_manual_review_count']}")
    lines.append("")

    lines.append("## Documentos bloqueantes")
    lines.append("")

    blocking_documents = preflight_response["blocking_documents"]

    if blocking_documents:
        for item in blocking_documents:
            classification = item["classification"]
            decision = item["decision"]
            file_name = Path(item["input_path"]).name

            lines.append(
                f"- `{file_name}` — "
                f"document_type: `{classification['document_type']}` — "
                f"confidence: `{classification['confidence']}` — "
                f"próximo passo: {decision['next_step']}"
            )
    else:
        lines.append("Nenhum documento bloqueante encontrado.")

    lines.append("")
    lines.append("## Decisão operacional")
    lines.append("")

    if preflight_response["can_continue"]:
        lines.append("A pré-triagem permite avançar para criação das extrações estruturadas JSON.")
    else:
        lines.append("A pré-triagem bloqueia o avanço automático até que os documentos pendentes sejam revisados.")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva relatório Markdown em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        file.write(report)


def print_human_summary(preflight_response: dict, output_json: str, output_report: str) -> None:
    """
    Imprime resumo humano da pré-triagem.
    """
    print("Pré-triagem de documentos finalizada.")
    print(f"Pasta analisada: {preflight_response['input_dir']}")
    print(f"Status: {preflight_response['status']}")
    print(f"Pode continuar: {preflight_response['can_continue']}")
    print(f"Mensagem: {preflight_response['message']}")
    print(f"Próximo passo: {preflight_response['next_step']}")
    print(f"JSON de pré-triagem: {output_json}")
    print(f"Relatório de pré-triagem: {output_report}")
    print("")

    summary = preflight_response["summary"]

    print("Resumo:")
    print(f"- Documentos aptos a continuar: {summary['should_continue_count']}")
    print(f"- Documentos que exigem revisão manual: {summary['requires_manual_review_count']}")


def print_json_response(preflight_response: dict) -> None:
    """
    Imprime JSON no terminal.
    """
    print(json.dumps(preflight_response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, bool]:
    """
    Uso:
        python3 tools/preflight_documents.py tests/fixtures/raw_text
        python3 tools/preflight_documents.py tests/fixtures/raw_text --json
        python3 tools/preflight_documents.py tests/fixtures/raw_text output.json output.report.md
        python3 tools/preflight_documents.py tests/fixtures/raw_text output.json output.report.md --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/preflight_documents.py pasta_de_textos")
        print("python3 tools/preflight_documents.py pasta_de_textos --json")
        print("python3 tools/preflight_documents.py pasta_de_textos output.json output.report.md")
        print("python3 tools/preflight_documents.py pasta_de_textos output.json output.report.md --json")
        sys.exit(1)

    input_dir = argv[1]
    args = argv[2:]

    output_json = "outputs/preflight-documents.json"
    output_report = "outputs/preflight-documents.report.md"
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
    print("python3 tools/preflight_documents.py pasta_de_textos")
    print("python3 tools/preflight_documents.py pasta_de_textos --json")
    print("python3 tools/preflight_documents.py pasta_de_textos output.json output.report.md")
    print("python3 tools/preflight_documents.py pasta_de_textos output.json output.report.md --json")
    sys.exit(1)


def main() -> None:
    input_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    preflight_response = build_preflight_response(input_dir)
    report = generate_markdown_report(preflight_response)

    save_json(preflight_response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(preflight_response)
    else:
        print_human_summary(preflight_response, output_json, output_report)

    if not preflight_response["can_continue"]:
        sys.exit(1)


if __name__ == "__main__":
    main()