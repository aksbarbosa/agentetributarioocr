import json
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}

DEFAULT_INPUT_DIR = "inputs/raw"
DEFAULT_OUTPUT_DIR = "outputs/preprocessed_raw"
DEFAULT_OUTPUT_JSON = "outputs/preprocess-raw-images.json"
DEFAULT_OUTPUT_REPORT = "outputs/preprocess-raw-images.report.md"


def collect_image_files(input_dir: str) -> list[Path]:
    path = Path(input_dir)

    if not path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not path.is_dir():
        raise NotADirectoryError(f"Não é uma pasta: {input_dir}")

    files = []

    for item in sorted(path.iterdir()):
        if not item.is_file():
            continue

        if item.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(item)

    return files


def preprocess_image(input_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{input_path.stem}_preprocessed.png"

    image = Image.open(input_path)
    image = ImageOps.exif_transpose(image)

    original_size = image.size

    image = image.convert("L")

    width, height = image.size
    image = image.resize((width * 2, height * 2))

    image = ImageEnhance.Contrast(image).enhance(1.8)
    image = ImageEnhance.Sharpness(image).enhance(1.5)

    image = image.point(lambda pixel: 255 if pixel > 180 else 0)

    image.save(output_path)

    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "status": "preprocessed",
        "original_size": list(original_size),
        "processed_size": list(image.size),
    }


def build_response(input_dir: str, output_dir: str) -> dict:
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    files = collect_image_files(input_dir)

    results = []

    for file_path in files:
        try:
            results.append(preprocess_image(file_path, output_path))
        except Exception as exc:
            results.append(
                {
                    "input_path": str(file_path),
                    "output_path": None,
                    "status": "error",
                    "error": str(exc),
                }
            )

    success_count = sum(1 for item in results if item["status"] == "preprocessed")
    error_count = sum(1 for item in results if item["status"] == "error")

    return {
        "input_dir": str(input_path),
        "output_dir": str(output_path),
        "summary": {
            "files_found": len(files),
            "preprocessed_count": success_count,
            "error_count": error_count,
        },
        "files": results,
    }


def save_json(data: dict, output_json: str) -> None:
    path = Path(output_json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_report(response: dict) -> str:
    lines = [
        "# Relatório de pré-processamento de imagens",
        "",
        f"Pasta de entrada: `{response['input_dir']}`",
        f"Pasta de saída: `{response['output_dir']}`",
        "",
        "## Resumo",
        "",
        f"- Imagens encontradas: {response['summary']['files_found']}",
        f"- Imagens pré-processadas: {response['summary']['preprocessed_count']}",
        f"- Erros: {response['summary']['error_count']}",
        "",
        "## Arquivos",
        "",
    ]

    if not response["files"]:
        lines.append("Nenhuma imagem encontrada.")
        return "\n".join(lines)

    for item in response["files"]:
        lines.append(f"### `{item['input_path']}`")
        lines.append("")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Saída: `{item.get('output_path')}`")

        if item["status"] == "preprocessed":
            lines.append(f"- Tamanho original: `{item.get('original_size')}`")
            lines.append(f"- Tamanho processado: `{item.get('processed_size')}`")

        if item["status"] == "error":
            lines.append(f"- Erro: `{item.get('error')}`")

        lines.append("")

    return "\n".join(lines)


def save_text(content: str, output_report: str) -> None:
    path = Path(output_report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[str, str, str, str]:
    args = argv[1:]

    if len(args) == 0:
        return DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 2:
        input_dir = args[0]
        output_dir = args[1]
        return input_dir, output_dir, DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 4:
        return args[0], args[1], args[2], args[3]

    print("Uso:")
    print("python3 tools/preprocess_raw_images.py")
    print("python3 tools/preprocess_raw_images.py input_dir output_dir")
    print("python3 tools/preprocess_raw_images.py input_dir output_dir output.json output.report.md")
    sys.exit(1)


def main() -> None:
    input_dir, output_dir, output_json, output_report = parse_args(sys.argv)

    response = build_response(input_dir, output_dir)
    report = build_report(response)

    save_json(response, output_json)
    save_text(report, output_report)

    print("Pré-processamento de imagens finalizado.")
    print(f"Pasta de entrada: {input_dir}")
    print(f"Pasta de saída: {output_dir}")
    print(f"JSON: {output_json}")
    print(f"Relatório: {output_report}")
    print("")
    print("Resumo:")
    print(f"- Imagens encontradas: {response['summary']['files_found']}")
    print(f"- Imagens pré-processadas: {response['summary']['preprocessed_count']}")
    print(f"- Erros: {response['summary']['error_count']}")


if __name__ == "__main__":
    main()