import json
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from promote_structured_extractions import (
    build_promoted_name,
    build_promotion_response,
    build_summary,
    collect_json_files,
    promote_file,
)


def make_valid_recibo(requires_review=None):
    if requires_review is None:
        requires_review = []

    return {
        "source_file": "teste.txt",
        "document_type": "recibo_medico",
        "fields": {
            "cpf_declarante": {
                "value": "11122233344",
                "confidence": "medium",
                "source_hint": "teste",
            },
            "nome_declarante": {
                "value": "JOSE DA SILVA",
                "confidence": "medium",
                "source_hint": "teste",
            },
            "data_nascimento": {
                "value": "01011980",
                "confidence": "medium",
                "source_hint": "teste",
            },
            "cpf_cnpj_prestador": {
                "value": "12345678909",
                "confidence": "medium",
                "source_hint": "teste",
            },
            "nome_prestador": {
                "value": "DR. CARLOS PEREIRA",
                "confidence": "medium",
                "source_hint": "teste",
            },
            "valor_pago": {
                "value": 30000,
                "confidence": "medium",
                "source_hint": "teste",
            },
            "data_pagamento": {
                "value": "10032025",
                "confidence": "medium",
                "source_hint": "teste",
            },
            "descricao": {
                "value": "CONSULTA MEDICA",
                "confidence": "medium",
                "source_hint": "teste",
            },
        },
        "requires_review": requires_review,
    }


def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_collect_json_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir)

        (input_dir / "a.json").write_text("{}", encoding="utf-8")
        (input_dir / "b.json").write_text("{}", encoding="utf-8")
        (input_dir / "c.txt").write_text("texto", encoding="utf-8")

        files = collect_json_files(str(input_dir))

        assert [file.name for file in files] == ["a.json", "b.json"]


def test_build_promoted_name():
    data = {"document_type": "recibo_medico"}

    assert build_promoted_name(Path("testemedic.json"), data) == "recibo_medico_testemedic.json"


def test_promote_file_valid_without_review():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"

        input_dir.mkdir()

        source = input_dir / "testemedic.json"
        write_json(source, make_valid_recibo(requires_review=[]))

        result = promote_file(source, str(output_dir))

        assert result["status"] == "promoted"
        assert result["destination_path"] is not None

        destination = Path(result["destination_path"])

        assert destination.exists()
        assert destination.name == "recibo_medico_testemedic.json"


def test_promote_file_valid_with_review_is_not_promoted():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"

        input_dir.mkdir()

        source = input_dir / "testemedic.json"
        write_json(
            source,
            make_valid_recibo(
                requires_review=[
                    {
                        "field": "data_nascimento",
                        "reason": "Campo com baixa confiança.",
                    }
                ]
            ),
        )

        result = promote_file(source, str(output_dir))

        assert result["status"] == "requires_review"
        assert result["destination_path"] is None
        assert not output_dir.exists() or not list(output_dir.glob("*.json"))


def test_promote_file_invalid_is_not_promoted():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"

        input_dir.mkdir()

        source = input_dir / "invalid.json"
        write_json(
            source,
            {
                "source_file": "teste.txt",
                "document_type": "desconhecido",
                "fields": {},
                "requires_review": [],
            },
        )

        result = promote_file(source, str(output_dir))

        assert result["status"] == "invalid"
        assert result["destination_path"] is None
        assert not output_dir.exists() or not list(output_dir.glob("*.json"))


def test_build_summary():
    results = [
        {"status": "promoted"},
        {"status": "invalid"},
        {"status": "requires_review"},
        {"status": "promoted"},
    ]

    summary = build_summary(results)

    assert summary["promoted_count"] == 2
    assert summary["invalid_count"] == 1
    assert summary["requires_review_count"] == 1


def test_build_promotion_response():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"

        input_dir.mkdir()

        write_json(input_dir / "ok.json", make_valid_recibo(requires_review=[]))
        write_json(
            input_dir / "review.json",
            make_valid_recibo(
                requires_review=[
                    {
                        "field": "cpf_declarante",
                        "reason": "Campo com baixa confiança.",
                    }
                ]
            ),
        )
        write_json(
            input_dir / "invalid.json",
            {
                "source_file": "teste.txt",
                "document_type": "desconhecido",
                "fields": {},
                "requires_review": [],
            },
        )

        response = build_promotion_response(str(input_dir), str(output_dir))

        assert response["total_files"] == 3
        assert response["summary"]["promoted_count"] == 1
        assert response["summary"]["requires_review_count"] == 1
        assert response["summary"]["invalid_count"] == 1

        promoted_files = list(output_dir.glob("*.json"))

        assert len(promoted_files) == 1
        assert promoted_files[0].name == "recibo_medico_ok.json"


def run_tests():
    test_collect_json_files()
    test_build_promoted_name()
    test_promote_file_valid_without_review()
    test_promote_file_valid_with_review_is_not_promoted()
    test_promote_file_invalid_is_not_promoted()
    test_build_summary()
    test_build_promotion_response()
    print("test_promote_structured_extractions.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()