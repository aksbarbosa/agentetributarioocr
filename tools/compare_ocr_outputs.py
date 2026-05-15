import json
import sys
from pathlib import Path


DEFAULT_ORIGINAL_DIR = "outputs/extracted_text"
DEFAULT_PREPARED_DIR = "outputs/extracted_text_prepared"
DEFAULT_OUTPUT_JSON = "outputs/compare-ocr-outputs.json"
DEFAULT_OUTPUT_REPORT = "outputs/compare-ocr-outputs.report.md"


def collect_txt_files(directory: str) -> dict[str, Path]:
    path = Path(directory)

    if not path.exists():
        return {}

    files = {}

    for item in sorted(path.glob("*.txt")):
        files[item.name] = item

    return files


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def compare_file(name: str, original_path: Path | None, prepared_path: Path | None) -> dict:
    original_text = read_text(original_path) if original_path else ""
    prepared_text = read_text(prepared_path) if prepared_path else ""

    original_len = len(original_text)
    prepared_len = len(prepared_text)
    delta = prepared_len - original_len

    if original_path and prepared_path:
        if delta > 0:
            status = "prepared_longer"
        elif delta < 0:
            status = "prepared_shorter"
        else:
            status = "same_length"
    elif original_path and not prepared_path:
        status = "missing_prepared"
    elif prepared_path and not original_path:
        status = "missing_original"
    else:
        status = "missing_both"

    return {
        "file": name,
        "status": status,
        "original_path": str(original_path) if original_path else None,
        "prepared_path": str(prepared_path) if prepared_path else None,
        "original_chars": original_len,
        "prepared_chars": prepared_len,
        "delta_chars": delta,
    }


def build_response(original_dir: str, prepared_dir: str) -> dict:
    original_files = collect_txt_files(original_dir)
    prepared_files = collect_txt_files(prepared_dir)

    names = sorted(set(original_files.keys()) | set(prepared_files.keys()))

    comparisons = [
        compare_file(
            name=name,
            original_path=original_files.get(name),
            prepared_path=prepared_files.get(name),
        )
        for name in names
    ]

    prepared_longer = sum(1 for item in comparisons if item["status"] == "prepared_longer")
    prepared_shorter = sum(1 for item in comparisons if item["status"] == "prepared_shorter")
    same_length = sum(1 for item in comparisons if item["status"] == "same_length")
    missing_prepared = sum(1 for item in comparisons if item["status"] == "missing_prepared")
    missing_original = sum(1 for item in comparisons if item["status"] == "missing_original")

    return {
        "original_dir": original_dir,
        "prepared_dir": prepared_dir,
        "summary": {
            "files_compared": len(comparisons),
            "prepared_longer": prepared_longer,
            "prepared_shorter": prepared_shorter,
            "same_length": same_length,
            "missing_prepared": missing_prepared,
            "missing_original": missing_original,
        },
        "comparisons": comparisons,
    }


def save_json(data: dict, output_json: str) -> None:
    path = Path(output_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_report(response: dict) -> str:
    lines = [
        "# Comparação de OCR normal vs OCR preparado",
        "",
        f"OCR normal: `{response['original_dir']}`",
        f"OCR preparado: `{response['prepared_dir']}`",
        "",
        "## Resumo",
        "",
        f"- Arquivos comparados: {response['summary']['files_compared']}",
        f"- Preparado maior: {response['summary']['prepared_longer']}",
        f"- Preparado menor: {response['summary']['prepared_shorter']}",
        f"- Mesmo tamanho: {response['summary']['same_length']}",
        f"- Ausente no preparado: {response['summary']['missing_prepared']}",
        f"- Ausente no original: {response['summary']['missing_original']}",
        "",
        "## Arquivos",
        "",
    ]

    if not response["comparisons"]:
        lines.append("Nenhum arquivo `.txt` encontrado para comparação.")
        return "\n".join(lines)

    for item in response["comparisons"]:
        lines.append(f"### `{item['file']}`")
        lines.append("")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Caracteres no OCR normal: {item['original_chars']}")
        lines.append(f"- Caracteres no OCR preparado: {item['prepared_chars']}")
        lines.append(f"- Diferença: {item['delta_chars']}")
        lines.append(f"- Original: `{item['original_path']}`")
        lines.append(f"- Preparado: `{item['prepared_path']}`")
        lines.append("")

    return "\n".join(lines)


def save_text(content: str, output_report: str) -> None:
    path = Path(output_report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[str, str, str, str]:
    args = argv[1:]

    if len(args) == 0:
        return DEFAULT_ORIGINAL_DIR, DEFAULT_PREPARED_DIR, DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 2:
        return args[0], args[1], DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 4:
        return args[0], args[1], args[2], args[3]

    print("Uso:")
    print("python3 tools/compare_ocr_outputs.py")
    print("python3 tools/compare_ocr_outputs.py original_dir prepared_dir")
    print("python3 tools/compare_ocr_outputs.py original_dir prepared_dir output.json output.report.md")
    sys.exit(1)


def main() -> None:
    original_dir, prepared_dir, output_json, output_report = parse_args(sys.argv)

    response = build_response(original_dir, prepared_dir)
    report = build_report(response)

    save_json(response, output_json)
    save_text(report, output_report)

    print("Comparação de OCR finalizada.")
    print(f"OCR normal: {original_dir}")
    print(f"OCR preparado: {prepared_dir}")
    print(f"JSON: {output_json}")
    print(f"Relatório: {output_report}")
    print("")
    print("Resumo:")
    print(f"- Arquivos comparados: {response['summary']['files_compared']}")
    print(f"- Preparado maior: {response['summary']['prepared_longer']}")
    print(f"- Preparado menor: {response['summary']['prepared_shorter']}")
    print(f"- Mesmo tamanho: {response['summary']['same_length']}")
    print(f"- Ausente no preparado: {response['summary']['missing_prepared']}")
    print(f"- Ausente no original: {response['summary']['missing_original']}")


if __name__ == "__main__":
    main()
