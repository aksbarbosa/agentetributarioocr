import json
import sys
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".txt": "text",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tif": "image",
    ".tiff": "image",
}


def classify_file_extension(path: Path) -> str:
    """
    Classifica o tipo bruto do arquivo pela extensão.
    """
    return SUPPORTED_EXTENSIONS.get(path.suffix.lower(), "unsupported")


def scan_raw_inputs(input_dir: str) -> dict:
    """
    Escaneia a pasta de documentos brutos.
    """
    path = Path(input_dir)

    if not path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not path.is_dir():
        raise NotADirectoryError(f"Não é uma pasta: {input_dir}")

    files = []

    for file_path in sorted(path.iterdir()):
        if not file_path.is_file():
            continue

        file_type = classify_file_extension(file_path)

        files.append(
            {
                "path": str(file_path),
                "name": file_path.name,
                "extension": file_path.suffix.lower(),
                "size_bytes": file_path.stat().st_size,
                "file_type": file_type,
                "can_extract_text": file_type in {"text", "pdf", "image"},
                "requires_ocr": file_type in {"image"},
            }
        )

    summary = build_summary(files)

    return {
        "input_dir": input_dir,
        "total_files": len(files),
        "summary": summary,
        "files": files,
    }


def build_summary(files: list[dict]) -> dict:
    """
    Cria resumo dos arquivos encontrados.
    """
    by_file_type = {}
    extractable_count = 0
    unsupported_count = 0
    requires_ocr_count = 0

    for item in files:
        file_type = item["file_type"]

        by_file_type[file_type] = by_file_type.get(file_type, 0) + 1

        if item["can_extract_text"]:
            extractable_count += 1

        if file_type == "unsupported":
            unsupported_count += 1

        if item["requires_ocr"]:
            requires_ocr_count += 1

    return {
        "by_file_type": by_file_type,
        "extractable_count": extractable_count,
        "unsupported_count": unsupported_count,
        "requires_ocr_count": requires_ocr_count,
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def generate_markdown_report(manifest: dict) -> str:
    """
    Gera relatório Markdown do manifesto de documentos brutos.
    """
    lines = []

    lines.append("# Manifesto de documentos brutos")
    lines.append("")
    lines.append(f"Pasta analisada: `{manifest['input_dir']}`")
    lines.append(f"Arquivos encontrados: {manifest['total_files']}")
    lines.append("")

    summary = manifest["summary"]

    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Arquivos extraíveis: {summary['extractable_count']}")
    lines.append(f"- Arquivos que exigem OCR: {summary['requires_ocr_count']}")
    lines.append(f"- Arquivos não suportados: {summary['unsupported_count']}")
    lines.append("")

    lines.append("## Tipos encontrados")
    lines.append("")

    if summary["by_file_type"]:
        for file_type, count in sorted(summary["by_file_type"].items()):
            lines.append(f"- `{file_type}`: {count}")
    else:
        lines.append("Nenhum arquivo encontrado.")

    lines.append("")
    lines.append("## Arquivos")
    lines.append("")

    if manifest["files"]:
        for item in manifest["files"]:
            lines.append(f"### `{item['name']}`")
            lines.append("")
            lines.append(f"- Caminho: `{item['path']}`")
            lines.append(f"- Extensão: `{item['extension']}`")
            lines.append(f"- Tipo: `{item['file_type']}`")
            lines.append(f"- Tamanho: {item['size_bytes']} bytes")
            lines.append(f"- Pode extrair texto: `{item['can_extract_text']}`")
            lines.append(f"- Exige OCR: `{item['requires_ocr']}`")
            lines.append("")
    else:
        lines.append("Nenhum arquivo encontrado.")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva relatório Markdown em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        file.write(report)


def print_human_summary(manifest: dict, output_json: str, output_report: str) -> None:
    """
    Imprime resumo humano.
    """
    print("Escaneamento de documentos brutos finalizado.")
    print(f"Pasta analisada: {manifest['input_dir']}")
    print(f"Arquivos encontrados: {manifest['total_files']}")
    print(f"JSON do manifesto: {output_json}")
    print(f"Relatório do manifesto: {output_report}")
    print("")

    summary = manifest["summary"]

    print("Resumo:")
    print(f"- Arquivos extraíveis: {summary['extractable_count']}")
    print(f"- Arquivos que exigem OCR: {summary['requires_ocr_count']}")
    print(f"- Arquivos não suportados: {summary['unsupported_count']}")


def print_json_response(manifest: dict) -> None:
    """
    Imprime JSON no terminal.
    """
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, bool]:
    """
    Uso:
        python3 tools/scan_raw_inputs.py inputs/raw
        python3 tools/scan_raw_inputs.py inputs/raw --json
        python3 tools/scan_raw_inputs.py inputs/raw output.json output.report.md
        python3 tools/scan_raw_inputs.py inputs/raw output.json output.report.md --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/scan_raw_inputs.py pasta_de_arquivos")
        print("python3 tools/scan_raw_inputs.py pasta_de_arquivos --json")
        print("python3 tools/scan_raw_inputs.py pasta_de_arquivos output.json output.report.md")
        print("python3 tools/scan_raw_inputs.py pasta_de_arquivos output.json output.report.md --json")
        sys.exit(1)

    input_dir = argv[1]
    args = argv[2:]

    output_json = "outputs/raw-inputs-manifest.json"
    output_report = "outputs/raw-inputs-manifest.report.md"
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
    print("python3 tools/scan_raw_inputs.py pasta_de_arquivos")
    print("python3 tools/scan_raw_inputs.py pasta_de_arquivos --json")
    print("python3 tools/scan_raw_inputs.py pasta_de_arquivos output.json output.report.md")
    print("python3 tools/scan_raw_inputs.py pasta_de_arquivos output.json output.report.md --json")
    sys.exit(1)


def main() -> None:
    input_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    manifest = scan_raw_inputs(input_dir)
    report = generate_markdown_report(manifest)

    save_json(manifest, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(manifest)
    else:
        print_human_summary(manifest, output_json, output_report)


if __name__ == "__main__":
    main()