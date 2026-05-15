import json
import sys
from pathlib import Path


DEFAULT_INPUT_PACK = "outputs/manual-review-pack.json"
DEFAULT_OUTPUT_JSON = "outputs/apply-manual-review-pack.json"
DEFAULT_OUTPUT_REPORT = "outputs/apply-manual-review-pack.report.md"


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def save_json(data: dict, path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_text(content: str, path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def normalize_status(value) -> str:
    return str(value or "").strip().lower()


def is_resolved_item(item: dict) -> bool:
    status = normalize_status(item.get("status"))
    suggested_value = item.get("suggested_value")

    return status == "resolved" and suggested_value not in {None, ""}


def group_resolved_items_by_file(pack: dict) -> dict[str, list[dict]]:
    grouped = {}

    for item in pack.get("items", []):
        if not is_resolved_item(item):
            continue

        file_path = item.get("file_path")

        if not file_path:
            continue

        grouped.setdefault(file_path, []).append(item)

    return grouped


def apply_items_to_file(file_path: str, items: list[dict]) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {
            "file_path": file_path,
            "status": "missing_file",
            "applied_count": 0,
            "errors": [f"Arquivo não encontrado: {file_path}"],
        }

    data = load_json(file_path)
    fields = data.get("fields", {})

    applied = []
    errors = []

    for item in items:
        field_name = item.get("field")
        suggested_value = item.get("suggested_value")

        if not field_name:
            errors.append("Item sem nome de campo.")
            continue

        if field_name not in fields:
            errors.append(f"Campo não encontrado no JSON: {field_name}")
            continue

        fields[field_name]["value"] = suggested_value
        fields[field_name]["confidence"] = "high"

        old_hint = fields[field_name].get("source_hint", "")
        review_hint = "Corrigido manualmente via manual-review-pack."

        if old_hint:
            fields[field_name]["source_hint"] = f"{old_hint} {review_hint}"
        else:
            fields[field_name]["source_hint"] = review_hint

        applied.append(
            {
                "field": field_name,
                "new_value": suggested_value,
            }
        )

    resolved_fields = {item["field"] for item in applied}

    remaining_requires_review = []

    for review_item in data.get("requires_review", []):
        field_name = review_item.get("field")

        if field_name in resolved_fields:
            continue

        remaining_requires_review.append(review_item)

    data["requires_review"] = remaining_requires_review

    save_json(data, file_path)

    return {
        "file_path": file_path,
        "status": "updated" if applied else "unchanged",
        "applied_count": len(applied),
        "applied": applied,
        "errors": errors,
    }


def build_report(response: dict) -> str:
    lines = [
        "# Relatório de aplicação do pacote de revisão manual",
        "",
        f"Pacote: `{response['input_pack']}`",
        "",
        "## Resumo",
        "",
        f"- Itens resolvidos no pacote: {response['summary']['resolved_item_count']}",
        f"- Arquivos atualizados: {response['summary']['updated_file_count']}",
        f"- Erros: {response['summary']['error_count']}",
        "",
    ]

    if not response["files"]:
        lines.append("Nenhum item resolvido foi aplicado.")
        return "\n".join(lines)

    lines.append("## Arquivos")
    lines.append("")

    for file_result in response["files"]:
        lines.append(f"### `{file_result['file_path']}`")
        lines.append("")
        lines.append(f"- Status: `{file_result['status']}`")
        lines.append(f"- Campos aplicados: {file_result['applied_count']}")
        lines.append("")

        for applied in file_result.get("applied", []):
            lines.append(f"- `{applied['field']}` → `{applied['new_value']}`")

        for error in file_result.get("errors", []):
            lines.append(f"- Erro: {error}")

        lines.append("")

    return "\n".join(lines)


def apply_manual_review_pack(input_pack: str) -> dict:
    pack = load_json(input_pack)
    grouped = group_resolved_items_by_file(pack)

    file_results = []

    for file_path, items in grouped.items():
        file_results.append(apply_items_to_file(file_path, items))

    resolved_item_count = sum(
        result.get("applied_count", 0) for result in file_results
    )

    updated_file_count = sum(
        1 for result in file_results if result.get("status") == "updated"
    )

    error_count = sum(
        len(result.get("errors", [])) for result in file_results
    )

    return {
        "input_pack": input_pack,
        "summary": {
            "resolved_item_count": resolved_item_count,
            "updated_file_count": updated_file_count,
            "error_count": error_count,
        },
        "files": file_results,
    }


def parse_args(argv: list[str]) -> tuple[str, str, str]:
    args = argv[1:]

    if len(args) == 0:
        return DEFAULT_INPUT_PACK, DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 3:
        return args[0], args[1], args[2]

    print("Uso:")
    print("python3 tools/apply_manual_review_pack.py")
    print("python3 tools/apply_manual_review_pack.py input_pack.json output.json output.report.md")
    sys.exit(1)


def main() -> None:
    input_pack, output_json, output_report = parse_args(sys.argv)

    response = apply_manual_review_pack(input_pack)
    report = build_report(response)

    save_json(response, output_json)
    save_text(report, output_report)

    print("Aplicação do pacote de revisão manual finalizada.")
    print(f"Pacote: {input_pack}")
    print(f"JSON: {output_json}")
    print(f"Relatório: {output_report}")
    print(f"Itens aplicados: {response['summary']['resolved_item_count']}")
    print(f"Arquivos atualizados: {response['summary']['updated_file_count']}")
    print(f"Erros: {response['summary']['error_count']}")

    if response["summary"]["error_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()