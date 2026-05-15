import json
import sys
from pathlib import Path


DEFAULT_INPUT_JSON = "outputs/review-promoted-extractions.json"
DEFAULT_OUTPUT_JSON = "outputs/manual-review-pack.json"
DEFAULT_OUTPUT_REPORT = "outputs/manual-review-pack.report.md"


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


def collect_review_items(review_data: dict) -> list[dict]:
    items = []

    for review in review_data.get("reviews", []):
        file_path = review.get("file_path")
        document_type = review.get("document_type")
        ready = review.get("ready_for_canonical_input")

        for field in review.get("fields", []):
            if not field.get("needs_review"):
                continue

            items.append(
                {
                    "file_path": file_path,
                    "document_type": document_type,
                    "ready_for_canonical_input": ready,
                    "field": field.get("field"),
                    "current_value": field.get("value"),
                    "confidence": field.get("confidence"),
                    "reasons": field.get("reasons", []),
                    "source_hint": field.get("source_hint", ""),
                    "suggested_value": None,
                    "status": "pending",
                }
            )

    return items


def build_pack(review_data: dict) -> dict:
    items = collect_review_items(review_data)

    files = sorted({item["file_path"] for item in items if item.get("file_path")})

    return {
        "source_review_json": DEFAULT_INPUT_JSON,
        "summary": {
            "files_with_pending_review": len(files),
            "pending_field_count": len(items),
        },
        "items": items,
        "instructions": [
            "Preencha suggested_value para cada item quando souber o valor correto.",
            "Mude status para resolved quando o campo tiver sido corrigido.",
            "Este pacote é apenas apoio à revisão humana.",
        ],
    }


def build_report(pack: dict) -> str:
    lines = [
        "# Pacote de revisão manual",
        "",
        "Este relatório lista campos que impedem aprovação automática.",
        "",
        "## Resumo",
        "",
        f"- Arquivos com pendência: {pack['summary']['files_with_pending_review']}",
        f"- Campos pendentes: {pack['summary']['pending_field_count']}",
        "",
    ]

    if not pack["items"]:
        lines.append("Nenhuma pendência encontrada.")
        return "\n".join(lines)

    current_file = None

    for item in pack["items"]:
        if item["file_path"] != current_file:
            current_file = item["file_path"]
            lines.append("")
            lines.append(f"## `{current_file}`")
            lines.append("")
            lines.append(f"- Tipo: `{item['document_type']}`")
            lines.append("")

        reasons = ", ".join(item.get("reasons", [])) or "sem motivo informado"

        lines.append(f"### Campo `{item['field']}`")
        lines.append("")
        lines.append(f"- Valor atual: `{item['current_value']}`")
        lines.append(f"- Confiança: `{item['confidence']}`")
        lines.append(f"- Motivos: {reasons}")
        lines.append(f"- Fonte: {item.get('source_hint', '')}")
        lines.append("- Valor sugerido: `preencher manualmente`")
        lines.append("")

    return "\n".join(lines)


def parse_args(argv: list[str]) -> tuple[str, str, str]:
    args = argv[1:]

    if len(args) == 0:
        return DEFAULT_INPUT_JSON, DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 3:
        return args[0], args[1], args[2]

    print("Uso:")
    print("python3 tools/generate_manual_review_pack.py")
    print("python3 tools/generate_manual_review_pack.py input_review.json output_pack.json output_report.md")
    sys.exit(1)


def main() -> None:
    input_json, output_json, output_report = parse_args(sys.argv)

    review_data = load_json(input_json)
    pack = build_pack(review_data)
    report = build_report(pack)

    save_json(pack, output_json)
    save_text(report, output_report)

    print("Pacote de revisão manual gerado.")
    print(f"Entrada: {input_json}")
    print(f"JSON: {output_json}")
    print(f"Relatório: {output_report}")
    print(f"Campos pendentes: {pack['summary']['pending_field_count']}")

    if pack["summary"]["pending_field_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()