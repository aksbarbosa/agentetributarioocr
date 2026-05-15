import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}

DEFAULT_INPUT_DIR = "inputs/raw"
DEFAULT_OUTPUT_DIR = "outputs/raw_prepared_for_ocr"
DEFAULT_OUTPUT_JSON = "outputs/prepare-raw-for-ocr.json"
DEFAULT_OUTPUT_REPORT = "outputs/prepare-raw-for-ocr.report.md"


def collect_files(input_dir: str) -> list[Path]:
    path = Path(input_dir)

    if not path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {input_dir}")

    if not path.is_dir():
        raise NotADirectoryError(f"Não é uma pasta: {input_dir}")

    return [item for item in sorted(path.iterdir()) if item.is_file()]


def preprocess_image(input_path: Path, output_path: Path) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)

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
        "original_size": list(original_size),
        "prepared_size": list(image.size),
    }


def prepare_file(input_path: Path, output_dir: Path) -> dict:
    suffix = input_path.suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        output_path = output_dir / f"{input_path.stem}_preprocessed.png"

        image_result = preprocess_image(input_path, output_path)

        return {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "kind": "image",
            "action": "preprocessed",
            "status": "ok",
            **image_result,
        }

    output_path = output_dir / input_path.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, output_path)

    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "kind": "non_image",
        "action": "copied",
        "status": "ok",
    }


def build_response(input_dir: str, output_dir: str) -> dict:
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)

    output_path.mkdir(parents=True, exist_ok=True)

    files = collect_files(input_dir)

    results = []

    for file_path in files:
        try:
            results.append(prepare_file(file_path, output_path))
        except Exception as exc:
            results.append(
                {
                    "input_path": str(file_path),
                    "output_path": None,
                    "kind": "unknown",
                    "action": "error",
                    "status": "error",
                    "error": str(exc),
                }
            )

    image_count = sum(1 for item in results if item.get("kind") == "image")
    copied_count = sum(1 for item in results if item.get("action") == "copied")
    preprocessed_count = sum(1 for item in results if item.get("action") == "preprocessed")
    error_count = sum(1 for item in results if item.get("status") == "error")

    return {
        "input_dir": str(input_path),
        "output_dir": str(output_path),
        "summary": {
            "files_found": len(files),
            "images_found": image_count,
            "files_copied": copied_count,
            "images_preprocessed": preprocessed_count,
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
        "# Relatório de preparação de documentos para OCR",
        "",
        f"Pasta de entrada: `{response['input_dir']}`",
        f"Pasta preparada: `{response['output_dir']}`",
        "",
        "## Resumo",
        "",
        f"- Arquivos encontrados: {response['summary']['files_found']}",
        f"- Imagens encontradas: {response['summary']['images_found']}",
        f"- Arquivos copiados: {response['summary']['files_copied']}",
        f"- Imagens pré-processadas: {response['summary']['images_preprocessed']}",
        f"- Erros: {response['summary']['error_count']}",
        "",
        "## Arquivos",
        "",
    ]

    if not response["files"]:
        lines.append("Nenhum arquivo encontrado.")
        return "\n".join(lines)

    for item in response["files"]:
        lines.append(f"### `{item['input_path']}`")
        lines.append("")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Tipo: `{item['kind']}`")
        lines.append(f"- Ação: `{item['action']}`")
        lines.append(f"- Saída: `{item.get('output_path')}`")

        if item.get("original_size"):
            lines.append(f"- Tamanho original: `{item.get('original_size')}`")

        if item.get("prepared_size"):
            lines.append(f"- Tamanho preparado: `{item.get('prepared_size')}`")

        if item.get("error"):
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
        return args[0], args[1], DEFAULT_OUTPUT_JSON, DEFAULT_OUTPUT_REPORT

    if len(args) == 4:
        return args[0], args[1], args[2], args[3]

    print("Uso:")
    print("python3 tools/prepare_raw_for_ocr.py")
    print("python3 tools/prepare_raw_for_ocr.py input_dir output_dir")
    print("python3 tools/prepare_raw_for_ocr.py input_dir output_dir output.json output.report.md")
    sys.exit(1)


def main() -> None:
    input_dir, output_dir, output_json, output_report = parse_args(sys.argv)

    response = build_response(input_dir, output_dir)
    report = build_report(response)

    save_json(response, output_json)
    save_text(report, output_report)

    print("Preparação de documentos para OCR finalizada.")
    print(f"Pasta de entrada: {input_dir}")
    print(f"Pasta preparada: {output_dir}")
    print(f"JSON: {output_json}")
    print(f"Relatório: {output_report}")
    print("")
    print("Resumo:")
    print(f"- Arquivos encontrados: {response['summary']['files_found']}")
    print(f"- Imagens encontradas: {response['summary']['images_found']}")
    print(f"- Arquivos copiados: {response['summary']['files_copied']}")
    print(f"- Imagens pré-processadas: {response['summary']['images_preprocessed']}")
    print(f"- Erros: {response['summary']['error_count']}")

    if response["summary"]["error_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()