import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from classify_document import classify_document_file, classify_document_text


def test_classify_informe_pj_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "informe_pj_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "informe_rendimentos_pj"
    assert result["confidence"] in {"high", "medium"}
    assert result["scores"]["informe_rendimentos_pj"] > 0
    assert result["matched_keywords"]["informe_rendimentos_pj"]


def test_classify_plano_saude_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "plano_saude_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "plano_saude"
    assert result["confidence"] in {"high", "medium"}
    assert result["scores"]["plano_saude"] > 0
    assert result["matched_keywords"]["plano_saude"]


def test_classify_bem_veiculo_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "crlv_veiculo_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "bem_veiculo"
    assert result["confidence"] in {"high", "medium"}
    assert result["scores"]["bem_veiculo"] > 0
    assert result["matched_keywords"]["bem_veiculo"]


def test_classify_bem_imovel_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "iptu_imovel_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "bem_imovel"
    assert result["confidence"] in {"high", "medium"}
    assert result["scores"]["bem_imovel"] > 0
    assert result["matched_keywords"]["bem_imovel"]


def test_classify_recibo_medico_file():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "recibo_medico_exemplo.txt"

    result = classify_document_file(str(path))

    assert result["document_type"] == "recibo_medico"
    assert result["confidence"] in {"high", "medium"}
    assert result["scores"]["recibo_medico"] > 0
    assert result["matched_keywords"]["recibo_medico"]


def test_classify_unknown_text():
    result = classify_document_text("DOCUMENTO SEM PALAVRAS RELEVANTES")

    assert result["document_type"] == "desconhecido"
    assert result["confidence"] == "low"
    assert result["best_score"] == 0


def test_classify_document_json_cli():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "crlv_veiculo_exemplo.txt"

    result = subprocess.run(
        [
            sys.executable,
            "tools/classify_document.py",
            str(path),
            "--json"
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"document_type": "bem_veiculo"' in result.stdout
    assert '"confidence": "high"' in result.stdout or '"confidence": "medium"' in result.stdout


def run_tests():
    test_classify_informe_pj_file()
    test_classify_plano_saude_file()
    test_classify_bem_veiculo_file()
    test_classify_bem_imovel_file()
    test_classify_recibo_medico_file()
    test_classify_unknown_text()
    test_classify_document_json_cli()
    print("test_classify_document.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()
