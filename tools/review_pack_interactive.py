import json
import sys
from pathlib import Path


DEFAULT_INPUT_PACK = "outputs/manual-review-pack.json"


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return json.loads(file_path.read_text(encoding="utf-8"))


def save_json(data: dict, path: str) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_pending(item: dict) -> bool:
    return item.get("status") != "resolved"


def ask_value(item: dict) -> str | None:
    print("")
    print("=" * 80)
    print(f"Arquivo: {item.get('file_path')}")
    print(f"Documento: {item.get('document_type')}")
    print(f"Campo: {item.get('field')}")
    print(f"Valor atual: {item.get('current_value')}")
    print(f"Confiança: {item.get('confidence')}")
    print(f"Motivos: {', '.join(item.get('reasons', []))}")
    print(f"Dica de origem: {item.get('source_hint')}")
    print("")
    print("Digite:")
    print("- novo valor para resolver")
    print("- ENTER para manter pendente")
    print("- !skip para pular")
    print("- !quit para sair salvando")
    print("")

    value = input("Valor corrigido: ").strip()

    if value == "":
        return None

    return value


def update_summary(data: dict) -> None:
    items = data.get("items", [])

    pending_count = sum(1 for item in items if item.get("status") != "resolved")
    files_with_pending = {
        item.get("file_path")
        for item in items
        if item.get("status") != "resolved"
    }

    data["summary"] = {
        "files_with_pending_review": len(files_with_pending),
        "pending_field_count": pending_count,
    }


def review_pack(data: dict) -> dict:
    items = data.get("items", [])

    if not isinstance(items, list):
        raise ValueError("Pacote inválido: campo 'items' deve ser uma lista.")

    total = len(items)
    pending_items = [item for item in items if is_pending(item)]

    print("Revisão interativa de pacote manual")
    print("")
    print(f"Itens totais: {total}")
    print(f"Itens pendentes: {len(pending_items)}")

    for index, item in enumerate(items, start=1):
        if not is_pending(item):
            continue

        print("")
        print(f"Item {index}/{total}")

        value = ask_value(item)

        if value == "!quit":
            print("")
            print("Saindo e salvando alterações feitas até agora.")
            break

        if value == "!skip" or value is None:
            print("Item mantido como pendente.")
            continue

        item["suggested_value"] = value
        item["status"] = "resolved"

        print("Item marcado como resolvido.")

    update_summary(data)

    return data


def parse_args(argv: list[str]) -> tuple[str, str]:
    args = argv[1:]

    if len(args) == 0:
        return DEFAULT_INPUT_PACK, DEFAULT_INPUT_PACK

    if len(args) == 1:
        return args[0], args[0]

    if len(args) == 2:
        return args[0], args[1]

    print("Uso:")
    print("python3 tools/review_pack_interactive.py")
    print("python3 tools/review_pack_interactive.py outputs/manual-review-pack.json")
    print("python3 tools/review_pack_interactive.py input.json output.json")
    sys.exit(1)


def main() -> None:
    input_path, output_path = parse_args(sys.argv)

    data = load_json(input_path)
    updated = review_pack(data)
    save_json(updated, output_path)

    print("")
    print("Pacote de revisão salvo.")
    print(f"Entrada: {input_path}")
    print(f"Saída: {output_path}")
    print(f"Pendências restantes: {updated.get('summary', {}).get('pending_field_count')}")


if __name__ == "__main__":
    main()
