import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from validate_extracted import validate_extracted


def load_json(path: Path) -> dict:
    import json

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_informe_pj_fixture():
    path = PROJECT_ROOT / "inputs" / "extracted" / "informe_pj_exemplo.json"
    data = load_json(path)

    result = validate_extracted(data)

    assert result["valid"] is True


def test_recibo_medico_fixture():
    path = PROJECT_ROOT / "inputs" / "extracted" / "recibo_medico_exemplo.json"
    data = load_json(path)

    result = validate_extracted(data)

    assert result["valid"] is True


def test_plano_saude_fixture():
    path = PROJECT_ROOT / "inputs" / "extracted" / "plano_saude_exemplo.json"
    data = load_json(path)

    result = validate_extracted(data)

    assert result["valid"] is True


def test_bem_imovel_fixture():
    path = PROJECT_ROOT / "inputs" / "extracted" / "bem_imovel_exemplo.json"
    data = load_json(path)

    result = validate_extracted(data)

    assert result["valid"] is True

    warnings = result.get("warnings", [])
    warning_fields = [warning["field"] for warning in warnings]

    assert "fields.matricula" in warning_fields


def test_bem_veiculo_fixture():
    path = PROJECT_ROOT / "inputs" / "extracted" / "bem_veiculo_exemplo.json"
    data = load_json(path)

    result = validate_extracted(data)

    assert result["valid"] is True


def test_document_type_invalido():
    data = {
        "document_type": "tipo_invalido",
        "source_file": "arquivo.pdf",
        "fields": {}
    }

    result = validate_extracted(data)

    assert result["valid"] is False
    assert result["errors"][0]["field"] == "document_type"


def run_tests():
    test_informe_pj_fixture()
    test_recibo_medico_fixture()
    test_plano_saude_fixture()
    test_bem_imovel_fixture()
    test_bem_veiculo_fixture()
    test_document_type_invalido()
    print("test_validate_extracted.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()