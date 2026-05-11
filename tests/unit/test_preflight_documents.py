import json
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from preflight_documents import build_preflight_response


def test_preflight_documents_ready():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    response = build_preflight_response(str(input_dir))

    assert response["status"] == "ready"
    assert response["can_continue"] is True
    assert response["summary"]["should_continue_count"] == 5
    assert response["summary"]["requires_manual_review_count"] == 0
    assert len(response["blocking_documents"]) == 0
    assert "Todos os 5 documento(s)" in response["message"]


def test_preflight_documents_blocked():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text_with_unknown"

    response = build_preflight_response(str(input_dir))

    assert response["status"] == "blocked"
    assert response["can_continue"] is False
    assert response["summary"]["should_continue_count"] == 5
    assert response["summary"]["requires_manual_review_count"] == 1
    assert len(response["blocking_documents"]) == 1
    assert "Há 1 documento(s) que exigem revisão manual" in response["message"]

    blocking_item = response["blocking_documents"][0]

    assert blocking_item["classification"]["document_type"] == "desconhecido"
    assert blocking_item["classification"]["confidence"] == "low"
    assert blocking_item["decision"]["should_continue"] is False


def test_preflight_documents_cli_ready():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_json = Path(temp_dir) / "preflight.json"
        output_report = Path(temp_dir) / "preflight.report.md"

        result = subprocess.run(
            [
                sys.executable,
                "tools/preflight_documents.py",
                str(input_dir),
                str(output_json),
                str(output_report),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_json.exists()
        assert output_report.exists()

        data = json.loads(output_json.read_text(encoding="utf-8"))

        assert data["status"] == "ready"
        assert data["can_continue"] is True
        assert len(data["blocking_documents"]) == 0

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Relatório de pré-triagem de documentos" in report_text
        assert "Status: `ready`" in report_text
        assert "Pode continuar: `True`" in report_text
        assert "Nenhum documento bloqueante encontrado." in report_text


def test_preflight_documents_cli_blocked():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text_with_unknown"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_json = Path(temp_dir) / "preflight.json"
        output_report = Path(temp_dir) / "preflight.report.md"

        result = subprocess.run(
            [
                sys.executable,
                "tools/preflight_documents.py",
                str(input_dir),
                str(output_json),
                str(output_report),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert output_json.exists()
        assert output_report.exists()

        data = json.loads(output_json.read_text(encoding="utf-8"))

        assert data["status"] == "blocked"
        assert data["can_continue"] is False
        assert len(data["blocking_documents"]) == 1

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Relatório de pré-triagem de documentos" in report_text
        assert "Status: `blocked`" in report_text
        assert "Pode continuar: `False`" in report_text
        assert "documento_desconhecido.txt" in report_text
        assert "A pré-triagem bloqueia o avanço automático" in report_text


def test_preflight_documents_json_cli_ready():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    result = subprocess.run(
        [
            sys.executable,
            "tools/preflight_documents.py",
            str(input_dir),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    data = json.loads(result.stdout)

    assert data["status"] == "ready"
    assert data["can_continue"] is True


def test_preflight_documents_json_cli_blocked():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text_with_unknown"

    result = subprocess.run(
        [
            sys.executable,
            "tools/preflight_documents.py",
            str(input_dir),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1

    data = json.loads(result.stdout)

    assert data["status"] == "blocked"
    assert data["can_continue"] is False
    assert len(data["blocking_documents"]) == 1


def run_tests():
    test_preflight_documents_ready()
    test_preflight_documents_blocked()
    test_preflight_documents_cli_ready()
    test_preflight_documents_cli_blocked()
    test_preflight_documents_json_cli_ready()
    test_preflight_documents_json_cli_blocked()
    print("test_preflight_documents.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()