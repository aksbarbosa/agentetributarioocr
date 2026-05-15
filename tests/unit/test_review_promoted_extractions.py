import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from review_promoted_extractions import (
    build_review_response,
    build_summary,
    collect_json_files,
    review_extraction,
    review_field,
)


def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def make_extraction(document_type="recibo_medico", low_confidence=False, missing_value=False):
    confidence = "low" if low_confidence else "medium"
    value = None if missing_value else "JOSE DA SILVA"

    return {
        "source_file": "teste.txt",
        "document_type": document_type,
        "fields": {
            "nome_declarante": {
                "value": value,
                "confidence": confidence,
                "source_hint": "teste",
            },
            "cpf_declarante": {
                "value": "12345678909",
                "confidence": "medium",
                "source_hint": "teste",
            },
        },
        "requires_review": [],
    }


def test_collect_json_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir)

        (input_dir / "a.json").write_text("{}", encoding="utf-8")
        (input_dir / "b.json").write_text("{}", encoding="utf-8")
        (input_dir / "c.txt").write_text("texto", encoding="utf-8")

        files = collect_json_files(str(input_dir))

        assert [file.name for file in files] == ["a.json", "b.json"]


def test_review_field_ready():
    result = review_field(
        "nome_declarante",
        {
            "value": "JOSE DA SILVA",
            "confidence": "medium",
            "source_hint": "teste",
        },
    )

    assert result["field"] == "nome_declarante"
    assert result["value"] == "JOSE DA SILVA"
    assert result["confidence"] == "medium"
    assert result["needs_review"] is False
    assert result["reasons"] == []


def test_review_field_low_confidence():
    result = review_field(
        "nome_declarante",
        {
            "value": "JOSE DA SILVA",
            "confidence": "low",
            "source_hint": "teste",
        },
    )

    assert result["needs_review"] is True
    assert "baixa confiança" in result["reasons"]


def test_review_field_missing_value():
    result = review_field(
        "nome_declarante",
        {
            "value": None,
            "confidence": "medium",
            "source_hint": "teste",
        },
    )

    assert result["needs_review"] is True
    assert "valor ausente" in result["reasons"]


def test_review_extraction_ready():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "ok.json"
        write_json(path, make_extraction())

        result = review_extraction(path)

        assert result["file_name"] == "ok.json"
        assert result["document_type"] == "recibo_medico"
        assert result["total_fields"] == 2
        assert result["low_confidence_count"] == 0
        assert result["missing_value_count"] == 0
        assert result["field_review_count"] == 0
        assert result["requires_review_count"] == 0
        assert result["ready_for_canonical_input"] is True


def test_review_extraction_with_low_confidence_is_not_ready():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "low.json"
        write_json(path, make_extraction(low_confidence=True))

        result = review_extraction(path)

        assert result["low_confidence_count"] == 1
        assert result["field_review_count"] == 1
        assert result["ready_for_canonical_input"] is False


def test_review_extraction_with_missing_value_is_not_ready():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "missing.json"
        write_json(path, make_extraction(missing_value=True))

        result = review_extraction(path)

        assert result["missing_value_count"] == 1
        assert result["field_review_count"] == 1
        assert result["ready_for_canonical_input"] is False


def test_build_summary():
    reviews = [
        {
            "document_type": "recibo_medico",
            "ready_for_canonical_input": True,
        },
        {
            "document_type": "recibo_medico",
            "ready_for_canonical_input": False,
        },
        {
            "document_type": "plano_saude",
            "ready_for_canonical_input": True,
        },
    ]

    summary = build_summary(reviews)

    assert summary["ready_count"] == 2
    assert summary["needs_review_count"] == 1
    assert summary["by_document_type"]["recibo_medico"] == 2
    assert summary["by_document_type"]["plano_saude"] == 1


def test_build_review_response():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir)

        write_json(input_dir / "ok.json", make_extraction("recibo_medico"))
        write_json(
            input_dir / "low.json",
            make_extraction("plano_saude", low_confidence=True),
        )

        response = build_review_response(str(input_dir))

        assert response["total_files"] == 2
        assert response["summary"]["ready_count"] == 1
        assert response["summary"]["needs_review_count"] == 1
        assert response["summary"]["by_document_type"]["recibo_medico"] == 1
        assert response["summary"]["by_document_type"]["plano_saude"] == 1


def run_tests():
    test_collect_json_files()
    test_review_field_ready()
    test_review_field_low_confidence()
    test_review_field_missing_value()
    test_review_extraction_ready()
    test_review_extraction_with_low_confidence_is_not_ready()
    test_review_extraction_with_missing_value_is_not_ready()
    test_build_summary()
    test_build_review_response()
    print("test_review_promoted_extractions.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()