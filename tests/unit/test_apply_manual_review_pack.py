import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from apply_manual_review_pack import apply_manual_review_pack


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_extraction(path: Path) -> None:
    data = {
        "source_file": "documento_teste.txt",
        "document_type": "recibo_medico",
        "fields": {
            "cpf_declarante": {
                "value": "11122233344",
                "confidence": "medium",
                "source_hint": "Valor original extraído automaticamente.",
            },
            "cpf_cnpj_prestador": {
                "value": "12345678909",
                "confidence": "high",
                "source_hint": "Valor já correto.",
            },
            "valor_pago": {
                "value": 50000,
                "confidence": "high",
                "source_hint": "Valor extraído automaticamente.",
            },
        },
        "requires_review": [
            {
                "field": "cpf_declarante",
                "reason": "CPF inválido",
            }
        ],
    }

    write_json(path, data)


def make_pack(path: Path, extraction_path: Path) -> None:
    data = {
        "source_review_json": "outputs/review-promoted-extractions.json",
        "summary": {
            "files_with_pending_review": 1,
            "pending_field_count": 1,
        },
        "items": [
            {
                "file_path": str(extraction_path),
                "document_type": "recibo_medico",
                "ready_for_canonical_input": True,
                "field": "cpf_declarante",
                "current_value": "11122233344",
                "confidence": "medium",
                "reasons": ["CPF inválido"],
                "source_hint": "Valor original extraído automaticamente.",
                "suggested_value": "12345678909",
                "status": "resolved",
            }
        ],
    }

    write_json(path, data)


def test_apply_resolved_item_updates_field():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        extraction_path = tmp_dir / "promoted" / "recibo.json"
        pack_path = tmp_dir / "manual-review-pack.json"

        make_extraction(extraction_path)
        make_pack(pack_path, extraction_path)

        response = apply_manual_review_pack(str(pack_path))

        assert response["summary"]["resolved_item_count"] == 1
        assert response["summary"]["updated_file_count"] == 1
        assert response["summary"]["error_count"] == 0

        updated = load_json(extraction_path)

        assert updated["fields"]["cpf_declarante"]["value"] == "12345678909"
        assert updated["fields"]["cpf_declarante"]["confidence"] == "high"
        assert "Corrigido manualmente" in updated["fields"]["cpf_declarante"]["source_hint"]
        assert updated["requires_review"] == []


def test_pending_item_is_not_applied():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        extraction_path = tmp_dir / "promoted" / "recibo.json"
        pack_path = tmp_dir / "manual-review-pack.json"

        make_extraction(extraction_path)

        pack = {
            "items": [
                {
                    "file_path": str(extraction_path),
                    "field": "cpf_declarante",
                    "suggested_value": "12345678909",
                    "status": "pending",
                }
            ]
        }

        write_json(pack_path, pack)

        response = apply_manual_review_pack(str(pack_path))

        assert response["summary"]["resolved_item_count"] == 0
        assert response["summary"]["updated_file_count"] == 0
        assert response["summary"]["error_count"] == 0

        updated = load_json(extraction_path)

        assert updated["fields"]["cpf_declarante"]["value"] == "11122233344"
        assert updated["fields"]["cpf_declarante"]["confidence"] == "medium"
        assert len(updated["requires_review"]) == 1


def test_missing_file_returns_error():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        missing_path = tmp_dir / "promoted" / "arquivo_inexistente.json"
        pack_path = tmp_dir / "manual-review-pack.json"

        pack = {
            "items": [
                {
                    "file_path": str(missing_path),
                    "field": "cpf_declarante",
                    "suggested_value": "12345678909",
                    "status": "resolved",
                }
            ]
        }

        write_json(pack_path, pack)

        response = apply_manual_review_pack(str(pack_path))

        assert response["summary"]["resolved_item_count"] == 0
        assert response["summary"]["updated_file_count"] == 0
        assert response["summary"]["error_count"] == 1
        assert response["files"][0]["status"] == "missing_file"


def test_missing_field_returns_error():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        extraction_path = tmp_dir / "promoted" / "recibo.json"
        pack_path = tmp_dir / "manual-review-pack.json"

        make_extraction(extraction_path)

        pack = {
            "items": [
                {
                    "file_path": str(extraction_path),
                    "field": "campo_inexistente",
                    "suggested_value": "12345678909",
                    "status": "resolved",
                }
            ]
        }

        write_json(pack_path, pack)

        response = apply_manual_review_pack(str(pack_path))

        assert response["summary"]["resolved_item_count"] == 0
        assert response["summary"]["updated_file_count"] == 0
        assert response["summary"]["error_count"] == 1
        assert "Campo não encontrado" in response["files"][0]["errors"][0]


def run_tests():
    test_apply_resolved_item_updates_field()
    test_pending_item_is_not_applied()
    test_missing_file_returns_error()
    test_missing_field_returns_error()

    print("test_apply_manual_review_pack.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()