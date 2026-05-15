import json
import shutil
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_ready_files(review_json_path: str) -> list[dict]:
    path = Path(review_json_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo de revisão não encontrado: {review_json_path}")

    data = load_json(path)
    ready = []

    for item in data.get("reviews", []):
        if item.get("ready_for_canonical_input") is True:
            ready.append(item)

    return ready


def copy_ready_files(review_json_path: str, output_dir: str) -> dict:
    ready_items = collect_ready_files(review_json_path)

    destination_dir = Path(output_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for item in ready_items:
        source_path = Path(item["file_path"])
        destination_path = destination_dir / source_path.name

        shutil.copy2(source_path, destination_path)

        results.append(
            {
                "source_path": str(source_path),
                "destination_path": str(destination_path),
                "document_type": item.get("document_type"),
                "status": "approved",
            }
        )

    return {
        "review_json_path": review_json_path,
        "output_dir": output_dir,
        "approved_count": len(results),
        "results": results,
    }


def save_json(data: dict, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_markdown_report(response: dict) -> str:
    lines = []

    lines.append("# Relatório de aprovação de extrações promovidas")
    lines.append("")
    lines.append(f"Arquivo de revisão: `{response['review_json_path']}`")
    lines.append(f"Pasta de destino: `{response['output_dir']}`")
    lines.append(f"Arquivos aprovados: {response['approved_count']}")
    lines.append("")
    lines.append("## Arquivos")
    lines.append("")

    if not response["results"]:
        lines.append("Nenhum arquivo aprovado.")
        return "\n".join(lines)

    for item in response["results"]:
        lines.append(f"- `{Path(item['source_path']).name}` → `{item['destination_path']}` — `{item['document_type']}`")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[str, str, str, str, bool]:
    args = argv[1:]

    review_json = "outputs/review-promoted-extractions.json"
    output_dir = "inputs/extracted"
    output_json = "outputs/approve-promoted-extractions.json"
    output_report = "outputs/approve-promoted-extractions.report.md"
    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    if len(args) == 0:
        return review_json, output_dir, output_json, output_report, print_json

    if len(args) == 4:
        return args[0], args[1], args[2], args[3], print_json

    print("Uso:")
    print("python3 tools/approve_promoted_extractions.py")
    print("python3 tools/approve_promoted_extractions.py --json")
    print("python3 tools/approve_promoted_extractions.py review.json output_dir output.json output.report.md")
    sys.exit(1)


def main() -> None:
    review_json, output_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    response = copy_ready_files(review_json, output_dir)
    report = generate_markdown_report(response)

    save_json(response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("Aprovação de extrações promovidas finalizada.")
        print(f"Arquivo de revisão: {review_json}")
        print(f"Pasta de destino: {output_dir}")
        print(f"Arquivos aprovados: {response['approved_count']}")
        print(f"JSON da aprovação: {output_json}")
        print(f"Relatório da aprovação: {output_report}")


if __name__ == "__main__":
    main()