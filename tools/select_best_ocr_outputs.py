import json
import shutil
import sys
from pathlib import Path


DEFAULT_ORIGINAL_DIR = "outputs/extracted_text"
DEFAULT_PREPARED_DIR = "outputs/extracted_text_prepared"
DEFAULT_OUTPUT_DIR = "outputs/extracted_text_best"
DEFAULT_OUTPUT_JSON = "outputs/select-best-ocr-outputs.json"
DEFAULT_OUTPUT_REPORT = "outputs/select-best-ocr-outputs.report.md"


def collect_txt_files(directory: str) -> dict[str, Path]:
    path = Path(directory)

    if not path.exists():
        return {}

    return {item.name: item for item in sorted(path.glob("*.txt"))}


def read_text(path: Path | None) -> str:
    if path is None:
        return ""

    return path.read_text(encoding="utf-8", errors="replace")


def choose_best_file(name: str, original_path: Path | None, prepared_path: Path | None) -> dict:
    original_text = read_text(original_path)
    prepared_text = read_text(prepared_path)

    original_len = len(original_text.strip())
    prepared_len = len(prepared_text.strip())

    if original_path and not prepared_path:
        choice = "original"
        selected_path = original_path

    elif prepared_path and not original_path:
        choice = "prepared"
        selected_path = prepared_path

    elif original_path and prepared_path:
        if prepared_len > original_len:
            choice = "prepared"
            selected_path = prepared_path
        else:
            choice = "original"
            selected_path = original_path

    else:
        choice = "missing"
        selected_path = None

    return {
        "file": name,
        "choice": choice,
        "selected_path": str(selected_path) if selected_path else None,
        "original_path": str(original_path) if original_path else None,
        "prepared_path": str(prepared_path) if prepared_path else None,
        "original_chars": original_len,
        "prepared_chars": prepared_len,
        "delta_chars": prepared_len - original_len,
    }


def build_response(original_dir: str, prepared_dir: str, output_dir: str) -> dict:
    original_files = collect_txt_files(original_dir)
    prepared_files = collect_txt_files(prepared_dir)

    names = sorted(set(original_files.keys()) | set(prepared_files.keys()))

    output_path = Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)

    output_path.mkdir(parents=True, exist_ok=True)

    decisions = []

    for name in names:
        decision = choose_best_file(
            name=name,
            original_path=original_files.get(name),
            prepared_path=prepared_files.get(name),
        )

        selected_path = decision["selected_path"]

        if selected_path:
            destination = output_path / name
            shutil.copy2(selected_path, destination)
            decision["output_path"] = str(destination)
        else:
            decision["output_path"] = None

        decisions.append(decision)

    original_selected = sum(1 for item in decisions if item["choice"] == "original")
    prepared_selected = sum(1 for item in decisions if item["choice"] == "prepared")
    missing = sum(1 for item in decisions if item["choice"] == "missing")

    return {
        "original_dir": original_dir,
        "prepared_dir": prepared_dir,
        "output_dir": output_dir,
        "summary": {
            "files_seen": len(decisions),
            "original_selected": original_selected,
            "prepared_selected": prepared_selected,
            "missing": missing,
        },
        "decisions": decisions,
    }


def save_json(data: dict, output_json: str) -> None:
    path = Path(output_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_report(response: dict) -> str:
    lines = [
        "# Seleção do melhor OCR",
        "",
        f"OCR normal: `{response['original_dir']}`",
        f"OCR preparado: `{response['prepared_dir']}`",
        f"Pasta final: `{response['output_dir']}`",
        "",
        "## Resumo",
        "",
        f"- Arquivos analisados: {response['summary']['files_seen']}",
        f"- OCR normal selecionado: {response['summary']['original_selected']}",
        f"- OCR preparado selecionado: {response['summary']['prepared_selected']}",
        f"- Ausentes: {response['summary']['missing']}",
        "",
        "## Decisões",
        "",
    ]

    if not response["decisions"]:
        lines.append("Nenhum arquivo `.txt` encontrado.")
        return "\n".join(lines)

    for item in response["decisions"]:
        lines.append(f"### `{item['file']}`")
        lines.append("")
        lines.append(f"- Escolha: `{item['choice']}`")
        lines.append(f"- Caracteres no OCR normal: {item['original_chars']}")
        lines.append(f"- Caracteres no OCR preparado: {item['prepared_chars']}")
        lines.append(f"- Diferença preparado - normal: {item['delta_chars']}")
        lines.append(f"- Arquivo selecionado: `{item['selected_path']}`")
        lines.append(f"- Saída: `{item['output_path']}`")
        lines.append("")

    return "\n".join(lines)


def save_text(content: str, output_report: str) -> None:
    path = Path(output_report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[str, str, str, str, str]:
    args = argv[1:]

    if len(args) == 0:
        return (
            DEFAULT_ORIGINAL_DIR,
            DEFAULT_PREPARED_DIR,
            DEFAULT_OUTPUT_DIR,
            DEFAULT_OUTPUT_JSON,
            DEFAULT_OUTPUT_REPORT,
        )

    if len(args) == 3:
        return args[0], args[1], args[2], DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 5:
        return args[0], args[1], args[2], args[3], args[4]

    print("Uso:")
    print("python3 tools/select_best_ocr_outputs.py")
    print("python3 tools/select_best_ocr_outputs.py original_dir prepared_dir output_dir")
    print("python3 tools/select_best_ocr_outputs.py original_dir prepared_dir output_dir output.json output.report.md")
    sys.exit(1)


def main() -> None:
    original_dir, prepared_dir, output_dir, output_json, output_report = parse_args(sys.argv)

    response = build_response(original_dir, prepared_dir, output_dir)
    report = build_report(response)

    save_json(response, output_json)
    save_text(report, output_report)

    print("Seleção do melhor OCR finalizada.")
    print(f"OCR normal: {original_dir}")
    print(f"OCR preparado: {prepared_dir}")
    print(f"Pasta final: {output_dir}")
    print(f"JSON: {output_json}")
    print(f"Relatório: {output_report}")
    print("")
    print("Resumo:")
    print(f"- Arquivos analisados: {response['summary']['files_seen']}")
    print(f"- OCR normal selecionado: {response['summary']['original_selected']}")
    print(f"- OCR preparado selecionado: {response['summary']['prepared_selected']}")
    print(f"- Ausentes: {response['summary']['missing']}")


if __name__ == "__main__":
    main()
