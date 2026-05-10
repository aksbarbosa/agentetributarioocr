import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from classify_document import classify_document_file, classify_document_text


def test_classify_bem_veiculo_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "crlv_veiculo_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "bem_veiculo"
    assert result["confidence"] in {"high", "medium"}


def test_classify_bem_imovel_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "iptu_imovel_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "bem_imovel"
    assert result["confidence"] in {"high", "medium"}


def test_classify_recibo_medico_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "recibo_medico_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "recibo_medico"
    assert result["confidence"] in {"high", "medium"}


def test_classify_unknown_text():
    result = classify_document_text("DOCUMENTO SEM PALAVRAS RELEVANTES")

    assert result["document_type"] == "desconhecido"
    assert result["confidence"] == "low"


def run_tests():
    test_classify_bem_veiculo_file()
    test_classify_bem_imovel_file()
    test_classify_recibo_medico_file()
    test_classify_unknown_text()
    print("test_classify_document.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()