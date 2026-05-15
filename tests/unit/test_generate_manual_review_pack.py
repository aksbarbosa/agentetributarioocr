import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from generate_manual_review_pack import build_pack, collect_review_items


def make_review_data():
    return {
        "reviews": [
            {
                "file_path": "outputs/promoted_extractions/recibo.json",
                "document_type": "recibo_medico",
                "ready_for_canonical_input": False,
                "fields": [
                    {
                        "field": "cpf_declarante",
                        "value": "11122233344",
                        "confidence": "medium",
                        "source_hint": "CPF extraído automaticamente.",
                        "needs_review": True,
                        "reasons": ["CPF inválido"],
                    },
                    {
                        "field": "valor_pago",
                        "value": 50000,
                        "confidence": "high",
                        "source_hint": "Valor extraído automaticamente.",
                        "needs_review": False,
                        "reasons": [],
                    },
                ],
            }
        ]
    }


def test_collect_review_items_only_pending_fields():
    review_data = make_review_data()

    items = collect_review_items(review_data)

    assert len(items) == 1
    assert items[0]["file_path"] == "outputs/promoted_extractions/recibo.json"
    assert items[0]["document_type"] == "recibo_medico"
    assert items[0]["ready_for_canonical_input"] is False
    assert items[0]["field"] == "cpf_declarante"
    assert items[0]["current_value"] == "11122233344"
    assert items[0]["confidence"] == "medium"
    assert items[0]["reasons"] == ["CPF inválido"]
    assert items[0]["source_hint"] == "CPF extraído automaticamente."
    assert items[0]["suggested_value"] is None
    assert items[0]["status"] == "pending"


def test_build_pack_summary():
    review_data = make_review_data()

    pack = build_pack(review_data)

    assert pack["summary"]["files_with_pending_review"] == 1
    assert pack["summary"]["pending_field_count"] == 1
    assert len(pack["items"]) == 1
    assert "instructions" in pack
    assert len(pack["instructions"]) > 0


def test_build_pack_without_pending_items():
    review_data = {
        "reviews": [
            {
                "file_path": "outputs/promoted_extractions/recibo.json",
                "document_type": "recibo_medico",
                "ready_for_canonical_input": True,
                "fields": [
                    {
                        "field": "valor_pago",
                        "value": 50000,
                        "confidence": "high",
                        "source_hint": "Valor extraído automaticamente.",
                        "needs_review": False,
                        "reasons": [],
                    }
                ],
            }
        ]
    }

    pack = build_pack(review_data)

    assert pack["summary"]["files_with_pending_review"] == 0
    assert pack["summary"]["pending_field_count"] == 0
    assert pack["items"] == []


def test_build_pack_multiple_pending_same_file():
    review_data = {
        "reviews": [
            {
                "file_path": "outputs/promoted_extractions/recibo.json",
                "document_type": "recibo_medico",
                "ready_for_canonical_input": False,
                "fields": [
                    {
                        "field": "cpf_declarante",
                        "value": "11122233344",
                        "confidence": "medium",
                        "source_hint": "CPF extraído automaticamente.",
                        "needs_review": True,
                        "reasons": ["CPF inválido"],
                    },
                    {
                        "field": "cpf_cnpj_prestador",
                        "value": "123",
                        "confidence": "medium",
                        "source_hint": "Prestador extraído automaticamente.",
                        "needs_review": True,
                        "reasons": ["CPF/CNPJ inválido"],
                    },
                ],
            }
        ]
    }

    pack = build_pack(review_data)

    assert pack["summary"]["files_with_pending_review"] == 1
    assert pack["summary"]["pending_field_count"] == 2
    assert len(pack["items"]) == 2


def test_build_pack_multiple_files():
    review_data = {
        "reviews": [
            {
                "file_path": "outputs/promoted_extractions/recibo.json",
                "document_type": "recibo_medico",
                "ready_for_canonical_input": False,
                "fields": [
                    {
                        "field": "cpf_declarante",
                        "value": "11122233344",
                        "confidence": "medium",
                        "source_hint": "CPF extraído automaticamente.",
                        "needs_review": True,
                        "reasons": ["CPF inválido"],
                    }
                ],
            },
            {
                "file_path": "outputs/promoted_extractions/plano.json",
                "document_type": "plano_saude",
                "ready_for_canonical_input": False,
                "fields": [
                    {
                        "field": "cnpj_operadora",
                        "value": "11222333000144",
                        "confidence": "medium",
                        "source_hint": "CNPJ extraído automaticamente.",
                        "needs_review": True,
                        "reasons": ["CNPJ inválido"],
                    }
                ],
            },
        ]
    }

    pack = build_pack(review_data)

    assert pack["summary"]["files_with_pending_review"] == 2
    assert pack["summary"]["pending_field_count"] == 2
    assert len(pack["items"]) == 2


def run_tests():
    test_collect_review_items_only_pending_fields()
    test_build_pack_summary()
    test_build_pack_without_pending_items()
    test_build_pack_multiple_pending_same_file()
    test_build_pack_multiple_files()

    print("test_generate_manual_review_pack.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()