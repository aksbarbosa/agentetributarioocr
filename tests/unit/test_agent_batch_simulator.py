import json
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from agent_batch_simulator import build_batch_response


def test_agent_batch_simulator_build_response():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    response = build_batch_response(str(input_dir))

    assert response["total_files"] == 5
    assert len(response["decisions"]) == 5

    document_types = [
        item["classification"]["document_type"]
        for item in response["decisions"]
    ]

    assert "informe_rendimentos_pj" in document_types
    assert "recibo_medico" in document_types
    assert "plano_saude" in document_types
    assert "bem_imovel" in document_types
    assert "bem_veiculo" in document_types

    assert response["summary"]["should_continue_count"] == 5
    assert response["summary"]["requires_manual_review_count"] == 0


def test_agent_batch_simulator_cli_outputs():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_json = Path(temp_dir) / "agent-decisions.json"
        output_report = Path(temp_dir) / "agent-decisions.report.md"

        result = subprocess.run(
            [
                sys.executable,
                "tools/agent_batch_simulator.py",
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

        with output_json.open("r", encoding="utf-8") as file:
            data = json.load(file)

        assert data["total_files"] == 5
        assert len(data["decisions"]) == 5
        assert data["summary"]["should_continue_count"] == 5
        assert data["summary"]["requires_manual_review_count"] == 0

        report_text = output_report.read_text(encoding="utf-8")

        assert "# Relatório de simulação local do agente" in report_text
        assert "informe_rendimentos_pj" in report_text
        assert "bem_veiculo" in report_text
        assert "## Resumo geral" in report_text
        assert "Documentos aptos a continuar: 5" in report_text
        assert "Documentos que exigem revisão manual: 0" in report_text
        assert "## Documentos que exigem revisão manual" in report_text
        assert "Nenhum documento exige revisão manual." in report_text


def test_agent_batch_simulator_json_cli():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    result = subprocess.run(
        [
            sys.executable,
            "tools/agent_batch_simulator.py",
            str(input_dir),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    data = json.loads(result.stdout)

    assert data["total_files"] == 5
    assert len(data["decisions"]) == 5
    assert data["summary"]["should_continue_count"] == 5
    assert data["summary"]["requires_manual_review_count"] == 0


def test_agent_batch_simulator_custom_paths_json_cli():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_json = Path(temp_dir) / "custom-agent-decisions.json"
        output_report = Path(temp_dir) / "custom-agent-decisions.report.md"

        result = subprocess.run(
            [
                sys.executable,
                "tools/agent_batch_simulator.py",
                str(input_dir),
                str(output_json),
                str(output_report),
                "--json",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_json.exists()
        assert output_report.exists()

        stdout_data = json.loads(result.stdout)

        assert stdout_data["total_files"] == 5
        assert stdout_data["summary"]["should_continue_count"] == 5
        assert stdout_data["summary"]["requires_manual_review_count"] == 0

        with output_json.open("r", encoding="utf-8") as file:
            saved_data = json.load(file)

        assert saved_data["total_files"] == 5
        assert len(saved_data["decisions"]) == 5
        assert saved_data["summary"]["should_continue_count"] == 5
        assert saved_data["summary"]["requires_manual_review_count"] == 0


def test_agent_batch_simulator_with_unknown_document():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text_with_unknown"

    response = build_batch_response(str(input_dir))

    assert response["total_files"] == 6
    assert len(response["decisions"]) == 6
    assert response["summary"]["should_continue_count"] == 5
    assert response["summary"]["requires_manual_review_count"] == 1

    unknown_items = [
        item for item in response["decisions"]
        if item["classification"]["document_type"] == "desconhecido"
    ]

    assert len(unknown_items) == 1
    assert unknown_items[0]["decision"]["should_continue"] is False
    assert unknown_items[0]["classification"]["confidence"] == "low"


def test_agent_batch_simulator_with_unknown_document_report():
    input_dir = PROJECT_ROOT / "tests" / "fixtures" / "raw_text_with_unknown"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_json = Path(temp_dir) / "agent-decisions.json"
        output_report = Path(temp_dir) / "agent-decisions.report.md"

        result = subprocess.run(
            [
                sys.executable,
                "tools/agent_batch_simulator.py",
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

        with output_json.open("r", encoding="utf-8") as file:
            data = json.load(file)

        assert data["total_files"] == 6
        assert data["summary"]["should_continue_count"] == 5
        assert data["summary"]["requires_manual_review_count"] == 1

        report_text = output_report.read_text(encoding="utf-8")

        assert "## Documentos que exigem revisão manual" in report_text
        assert "documento_desconhecido.txt" in report_text
        assert "document_type: `desconhecido`" in report_text
        assert "confidence: `low`" in report_text


def run_tests():
    test_agent_batch_simulator_build_response()
    test_agent_batch_simulator_cli_outputs()
    test_agent_batch_simulator_json_cli()
    test_agent_batch_simulator_custom_paths_json_cli()
    test_agent_batch_simulator_with_unknown_document()
    test_agent_batch_simulator_with_unknown_document_report()
    print("test_agent_batch_simulator.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()