import json
import sys
from pathlib import Path

from scan_raw_inputs import scan_raw_inputs


def safe_output_name(source_path: str) -> str:
    """
    Cria um nome seguro para o arquivo de texto extraído.
    """
    path = Path(source_path)
    stem = path.stem.replace(" ", "_")
    return f"{stem}.txt"


def read_text_file(path: Path) -> tuple[str, list[str]]:
    """
    Lê arquivo .txt.
    """
    warnings = []

    try:
        return path.read_text(encoding="utf-8"), warnings
    except UnicodeDecodeError:
        warnings.append("Falha ao ler como UTF-8; tentando latin-1.")
        return path.read_text(encoding="latin-1"), warnings


def extract_pdf_text(path: Path) -> tuple[str, list[str]]:
    """
    Tenta extrair texto de PDF pesquisável.

    Nesta primeira versão, usa PyPDF se estiver disponível.
    Se PyPDF não estiver instalado ou o PDF for escaneado, o texto pode sair vazio.
    """
    warnings = []

    try:
        from pypdf import PdfReader
    except ImportError:
        warnings.append("Biblioteca pypdf não instalada; não foi possível extrair texto do PDF.")
        return "", warnings

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        warnings.append(f"Falha ao abrir PDF: {exc}")
        return "", warnings

    pages_text = []

    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            warnings.append(f"Falha ao extrair texto da página {index}: {exc}")
            text = ""

        pages_text.append(text)

    extracted = "\n\n".join(pages_text).strip()

    if not extracted:
        warnings.append(
            "Nenhum texto extraído do PDF. O arquivo pode ser escaneado e exigir OCR real."
        )

    return extracted, warnings

def extract_image_text(path: Path) -> tuple[str, list[str]]:
    """
    Extrai texto de imagem usando Tesseract.

    Requer:
    - tesseract instalado no sistema;
    - pillow instalado no ambiente Python;
    - pytesseract instalado no ambiente Python.
    """
    warnings = []

    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        warnings.append("pillow/pytesseract não instalados; OCR de imagem indisponível.")
        return "", warnings

    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang="por+eng")
    except Exception as exc:
        warnings.append(f"Falha no OCR da imagem: {exc}")
        return "", warnings

    extracted = text.strip()

    if not extracted:
        warnings.append("OCR executado, mas nenhum texto foi extraído da imagem.")

    return extracted, warnings


def extract_text_from_file(file_info: dict, output_dir: str) -> dict:
    """
    Extrai texto de um arquivo individual, quando possível.
    """
    source_path = Path(file_info["path"])
    file_type = file_info["file_type"]

    output_path = Path(output_dir) / safe_output_name(file_info["path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    warnings = []
    text = ""
    status = "skipped"

    if file_type == "text":
        text, warnings = read_text_file(source_path)
        text = text.strip()

        if text:
            status = "extracted"
        else:
            warnings.append("Arquivo de texto vazio; nada foi extraído.")
            status = "empty"

    elif file_type == "pdf":
        text, warnings = extract_pdf_text(source_path)
        status = "extracted" if text else "requires_ocr"

    elif file_type == "image":
        text, warnings = extract_image_text(source_path)
        status = "extracted" if text else "requires_ocr"

    else:
        warnings.append("Tipo de arquivo não suportado para extração de texto.")
        status = "unsupported"

    wrote_output = False

    if text:
        output_path.write_text(text, encoding="utf-8")
        wrote_output = True

    return {
        "source_path": str(source_path),
        "source_name": source_path.name,
        "file_type": file_type,
        "status": status,
        "text_output_path": str(output_path) if wrote_output else None,
        "text_length": len(text),
        "warnings": warnings,
    }
    
def build_summary(results: list[dict]) -> dict:
    """
    Resume os resultados da extração.
    """
    by_status = {}
    extracted_count = 0
    requires_ocr_count = 0
    unsupported_count = 0
    empty_count = 0

    for item in results:
        status = item["status"]
        by_status[status] = by_status.get(status, 0) + 1

        if status == "extracted":
            extracted_count += 1
        elif status == "requires_ocr":
            requires_ocr_count += 1
        elif status == "unsupported":
            unsupported_count += 1
        elif status == "empty":
            empty_count += 1

    return {
        "by_status": by_status,
        "extracted_count": extracted_count,
        "requires_ocr_count": requires_ocr_count,
        "unsupported_count": unsupported_count,
        "empty_count": empty_count,
    }


def extract_text_from_raw_inputs(input_dir: str, output_text_dir: str) -> dict:
    """
    Escaneia inputs/raw e extrai texto quando possível.
    """
    manifest = scan_raw_inputs(input_dir)

    results = []

    for file_info in manifest["files"]:
        result = extract_text_from_file(file_info, output_text_dir)
        results.append(result)

    summary = build_summary(results)

    return {
        "input_dir": input_dir,
        "output_text_dir": output_text_dir,
        "total_files": len(results),
        "summary": summary,
        "results": results,
        "manifest": manifest,
    }


def save_json(data: dict, output_path: str) -> None:
    """
    Salva JSON em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def generate_markdown_report(response: dict) -> str:
    """
    Gera relatório Markdown da extração de texto.
    """
    lines = []

    lines.append("# Relatório de extração de texto")
    lines.append("")
    lines.append(f"Pasta de entrada: `{response['input_dir']}`")
    lines.append(f"Pasta de textos extraídos: `{response['output_text_dir']}`")
    lines.append(f"Arquivos analisados: {response['total_files']}")
    lines.append("")

    summary = response["summary"]

    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Textos extraídos: {summary['extracted_count']}")
    lines.append(f"- Arquivos que exigem OCR real: {summary['requires_ocr_count']}")
    lines.append(f"- Arquivos não suportados: {summary['unsupported_count']}")
    lines.append(f"- Arquivos vazios: {summary['empty_count']}")
    lines.append("")

    lines.append("## Status")
    lines.append("")

    if summary["by_status"]:
        for status, count in sorted(summary["by_status"].items()):
            lines.append(f"- `{status}`: {count}")
    else:
        lines.append("Nenhum arquivo analisado.")

    lines.append("")
    lines.append("## Arquivos")
    lines.append("")

    if response["results"]:
        for item in response["results"]:
            lines.append(f"### `{item['source_name']}`")
            lines.append("")
            lines.append(f"- Caminho: `{item['source_path']}`")
            lines.append(f"- Tipo: `{item['file_type']}`")
            lines.append(f"- Status: `{item['status']}`")
            lines.append(f"- Texto extraído: `{item['text_output_path']}`")
            lines.append(f"- Tamanho do texto: {item['text_length']}")
            if item["warnings"]:
                lines.append("- Avisos:")
                for warning in item["warnings"]:
                    lines.append(f"  - {warning}")
            else:
                lines.append("- Avisos: nenhum")
            lines.append("")
    else:
        lines.append("Nenhum arquivo analisado.")

    return "\n".join(lines)


def save_report(report: str, output_path: str) -> None:
    """
    Salva relatório Markdown em arquivo.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        file.write(report)


def print_human_summary(response: dict, output_json: str, output_report: str) -> None:
    """
    Imprime resumo humano.
    """
    print("Extração de texto finalizada.")
    print(f"Pasta de entrada: {response['input_dir']}")
    print(f"Pasta de textos extraídos: {response['output_text_dir']}")
    print(f"Arquivos analisados: {response['total_files']}")
    print(f"JSON da extração: {output_json}")
    print(f"Relatório da extração: {output_report}")
    print("")

    summary = response["summary"]

    print("Resumo:")
    print(f"- Textos extraídos: {summary['extracted_count']}")
    print(f"- Arquivos que exigem OCR real: {summary['requires_ocr_count']}")
    print(f"- Arquivos não suportados: {summary['unsupported_count']}")
    print(f"- Arquivos vazios: {summary['empty_count']}")


def print_json_response(response: dict) -> None:
    """
    Imprime JSON no terminal.
    """
    print(json.dumps(response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, str, str, str, bool]:
    """
    Uso:
        python3 tools/extract_text.py inputs/raw
        python3 tools/extract_text.py inputs/raw --json
        python3 tools/extract_text.py inputs/raw outputs/extracted_text output.json output.report.md
        python3 tools/extract_text.py inputs/raw outputs/extracted_text output.json output.report.md --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/extract_text.py pasta_de_arquivos")
        print("python3 tools/extract_text.py pasta_de_arquivos --json")
        print("python3 tools/extract_text.py pasta_de_arquivos output_text_dir output.json output.report.md")
        print("python3 tools/extract_text.py pasta_de_arquivos output_text_dir output.json output.report.md --json")
        sys.exit(1)

    input_dir = argv[1]
    args = argv[2:]

    output_text_dir = "outputs/extracted_text"
    output_json = "outputs/extract-text.json"
    output_report = "outputs/extract-text.report.md"
    print_json = False

    if "--json" in args:
        print_json = True
        args = [arg for arg in args if arg != "--json"]

    if len(args) == 0:
        return input_dir, output_text_dir, output_json, output_report, print_json

    if len(args) == 3:
        output_text_dir = args[0]
        output_json = args[1]
        output_report = args[2]
        return input_dir, output_text_dir, output_json, output_report, print_json

    print("Uso:")
    print("python3 tools/extract_text.py pasta_de_arquivos")
    print("python3 tools/extract_text.py pasta_de_arquivos --json")
    print("python3 tools/extract_text.py pasta_de_arquivos output_text_dir output.json output.report.md")
    print("python3 tools/extract_text.py pasta_de_arquivos output_text_dir output.json output.report.md --json")
    sys.exit(1)


def main() -> None:
    input_dir, output_text_dir, output_json, output_report, should_print_json = parse_args(sys.argv)

    response = extract_text_from_raw_inputs(input_dir, output_text_dir)
    report = generate_markdown_report(response)

    save_json(response, output_json)
    save_report(report, output_report)

    if should_print_json:
        print_json_response(response)
    else:
        print_human_summary(response, output_json, output_report)


if __name__ == "__main__":
    main()