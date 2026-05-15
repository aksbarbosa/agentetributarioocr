import json
import sys
from pathlib import Path
import re


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


def load_json(path: Path) -> dict:
    """
    Carrega JSON.
    """
    return json.loads(path.read_text(encoding="utf-8"))




def only_digits(value) -> str:
    """
    Mantém apenas dígitos.
    """
    return re.sub(r"\D", "", str(value or ""))


def is_valid_cpf(value) -> bool:
    """
    Valida CPF pelo dígito verificador.
    """
    cpf = only_digits(value)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    total = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit_1 = (total * 10) % 11
    if digit_1 == 10:
        digit_1 = 0

    total = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit_2 = (total * 10) % 11
    if digit_2 == 10:
        digit_2 = 0

    return cpf[-2:] == f"{digit_1}{digit_2}"


def is_valid_cnpj(value) -> bool:
    """
    Valida CNPJ pelo dígito verificador.
    """
    cnpj = only_digits(value)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    total = sum(int(cnpj[i]) * weights_1[i] for i in range(12))
    remainder = total % 11
    digit_1 = 0 if remainder < 2 else 11 - remainder

    total = sum(int(cnpj[i]) * weights_2[i] for i in range(13))
    remainder = total % 11
    digit_2 = 0 if remainder < 2 else 11 - remainder

    return cnpj[-2:] == f"{digit_1}{digit_2}"


def identifier_review_reason(field_name: str, value) -> str | None:
    """
    Retorna motivo de revisão para CPF/CNPJ inválido.
    """
    if value in {None, ""}:
        return None

    digits = only_digits(value)

    cpf_fields = {
        "cpf_declarante",
    }

    cnpj_fields = {
        "cnpj_pagador",
        "cnpj_operadora",
    }

    cpf_or_cnpj_fields = {
        "cpf_cnpj_prestador",
        "beneficiario_cpf_cnpj",
    }

    if field_name in cpf_fields and not is_valid_cpf(digits):
        return "CPF inválido"

    if field_name in cnpj_fields and not is_valid_cnpj(digits):
        return "CNPJ inválido"

    if field_name in cpf_or_cnpj_fields:
        if len(digits) == 11 and not is_valid_cpf(digits):
            return "CPF inválido"
        if len(digits) == 14 and not is_valid_cnpj(digits):
            return "CNPJ inválido"
        if len(digits) not in {11, 14}:
            return "CPF/CNPJ inválido"

    return None


def review_field(field_name: str, field_data: dict) -> dict:
    """
    Resume a revisão de um campo.
    """
    value = field_data.get("value")
    confidence = field_data.get("confidence", "unknown")
    source_hint = field_data.get("source_hint", "")

    needs_review = False
    reasons = []

    if value in {None, ""}:
        needs_review = True
        reasons.append("valor ausente")

    if confidence == "low":
        needs_review = True
        reasons.append("baixa confiança")

    identifier_reason = identifier_review_reason(field_name, value)

    if identifier_reason:
        needs_review = True
        reasons.append(identifier_reason)

    return {
        "field": field_name,
        "value": value,
        "confidence": confidence,
        "source_hint": source_hint,
        "needs_review": needs_review,
        "reasons": reasons,
    }


def review_extraction(path: Path) -> dict:
    """
    Revisa uma extração promovida.
    """
    data = load_json(path)

    fields = data.get("fields", {})
    field_reviews = []

    for field_name, field_data in fields.items():
        field_reviews.append(review_field(field_name, field_data))

    requires_review = data.get("requires_review", [])

    low_confidence_count = sum(
        1 for item in field_reviews if item["confidence"] == "low"
    )
    missing_value_count = sum(
        1 for item in field_reviews if item["value"] in {None, ""}
    )
    field_review_count = sum(
        1 for item in field_reviews if item["needs_review"]
    )

    ready_for_canonical_input = (
        len(requires_review) == 0
        and low_confidence_count == 0
        and missing_value_count == 0
    )

    return {
        "file_path": str(path),
        "file_name": path.name,
        "document_type": data.get("document_type"),
        "source_file": data.get("source_file"),
        "total_fields": len(fields),
        "low_confidence_count": low_confidence_count,
        "missing_value_count": missing_value_count,
        "field_review_count": field_review_count,
        "requires_review_count": len(requires_review),
        "ready_for_canonical_input": ready_for_canonical_input,
        "fields": field_reviews,
        "raw_requires_review": requires_review,
    }


def build_review_response(input_dir: str) -> dict:
    """
    Cria revisão das extrações promovidas.
    """
    files = collect_json_files(input_dir)
    reviews = [review_extraction(file_path) for file_path in files]

    summary = build_summary(reviews)

    return {
        "input_dir": input_dir,
        "total_files": len(files),
        "summary": summary,
        "reviews": reviews,
    }


def build_summary(reviews: list[dict]) -> dict:
    """
    Resume a revisão.
    """
    by_document_type = {}
    ready_count = 0
    needs_review_count = 0

    for item in reviews:
        document_type = item["document_type"]

        by_document_type[document_type] = by_document_type.get(document_type, 0) + 1

        if item["ready_for_canonical_input"]:
            ready_count += 1
        else:
            needs_review_count += 1

    return {
        "by_document_type": by_document_type,
        "ready_count": ready_count,
        "needs_review_count": needs_review_count,
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
    Gera relatório Markdown de revisão humana assistida.
    """
    lines = []

    lines.append("# Relatório de revisão das extrações promovidas")
    lines.append("")
    lines.append(f"Pasta analisada: `{response['input_dir']}`")
    lines.append(f"Arquivos analisados: {response['total_files']}")
    lines.append("")

    summary = response["summary"]

    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Prontos para entrada canônica: {summary['ready_count']}")
    lines.append(f"- Exigem revisão: {summary['needs_review_count']}")
    lines.append("")

    lines.append("## Por tipo de documento")
    lines.append("")

    if summary["by_document_type"]:
        for document_type, count in sorted(summary["by_document_type"].items()):
            lines.append(f"- `{document_type}`: {count}")
    else:
        lines.append("Nenhum documento encontrado.")

    lines.append("")
    lines.append("## Arquivos")
    lines.append("")

    if not response["reviews"]:
        lines.append("Nenhuma extração promovida encontrada.")
        return "\n".join(lines)

    for review in response["reviews"]:
        status = (
            "pronto"
            if review["ready_for_canonical_input"]
            else "exige revisão"
        )

        lines.append(f"### `{review['file_name']}`")
        lines.append("")
        lines.append(f"- Tipo: `{review['document_type']}`")
        lines.append(f"- Arquivo de origem: `{review['source_file']}`")
        lines.append(f"- Status: `{status}`")
        lines.append(f"- Campos totais: {review['total_fields']}")
        lines.append(f"- Campos com baixa confiança: {review['low_confidence_count']}")
        lines.append(f"- Campos com valor ausente: {review['missing_value_count']}")
        lines.append(f"- Itens em requires_review: {review['requires_review_count']}")
        lines.append("")

        lines.append("#### Campos")
        lines.append("")
        lines.append("| Campo | Valor | Confiança | Revisar? | Motivos |")
        lines.append("|---|---|---|---|---|")

        for field in review["fields"]:
            value = field["value"]
            value_text = "" if value is None else str(value)
            value_text = value_text.replace("\n", " ")

            if len(value_text) > 80:
                value_text = value_text[:77] + "..."

            needs_review = "sim" if field["needs_review"] else "não"
            reasons = ", ".join(field["reasons"]) if field["reasons"] else "-"

            lines.append(
                f"| `{field['field']}` | `{value_text}` | `{field['confidence']}` | {needs_review} | {reasons} |"
            )

        lines.append("")

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
    print("Revisão das extrações promovidas finalizada.")
    print(f"Pasta analisada: {response['input_dir']}")
    print(f"Arquivos analisados: {response['total_files']}")
    print(f"JSON da revisão: {output_json}")
    print(f"Relatório da revisão: {output_report}")
    print("")

    summary = response["summary"]

    print("Resumo:")
    print(f"- Prontos para entrada canônica: {summary['ready_count']}")
    print(f"- Exigem revisão: {summary['needs_review_count']}")


def print_json_response(response: dict) -> None:
    """
    Imprime JSON no terminal.
    """
    print(json.dumps(response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, bool]:
    """
    Uso:
        python3 tools/review_promoted_extractions.py
        python3 tools/review_promoted_extractions.py --json
        python3 tools/review_promoted_extractions.py input_dir output.json output.report.md
        python3 tools/review_promoted_extractions.py input_dir output.json output.report.md --json
    """
    args = argv[1:]

    input_dir = "outputs/promoted_extractions"
    output_json = "outputs/review-promoted-extractions.json"
    output_report = "outputs/review-promoted-extractions.report.md"
    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    if len(args) == 0:
        return input_dir, output_json, output_report, print_json

    if len(args) == 3:
        input_dir = args[0]
        output_json = args[1]
        output_report = args[2]
        return input_dir, output_json, output_report, print_json

    print("Uso:")
    print("python3 tools/review_promoted_extractions.py")
    print("python3 tools/review_promoted_extractions.py --json")
    print(
        "python3 tools/review_promoted_extractions.py "
        "input_dir output.json output.report.md"
    )
    print(
        "python3 tools/review_promoted_extractions.py "
        "input_dir output.json output.report.md --json"
    )
    sys.exit(1)


def main() -> None:
    input_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    response = build_review_response(input_dir)
    report = generate_markdown_report(response)

    save_json(response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(response)
    else:
        print_human_summary(response, output_json, output_report)


if __name__ == "__main__":
    main()
