import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from agent_simulator import build_agent_response


def test_agent_simulator_bem_veiculo():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "crlv_veiculo_exemplo.txt"

    response = build_agent_response(str(path))

    assert response["classification"]["document_type"] == "bem_veiculo"
    assert response["decision"]["should_continue"] is True
    assert response["decision"]["schema_path"] == "skill/schemas/extracted_bem_veiculo.json"


def test_agent_simulator_bem_imovel():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "iptu_imovel_exemplo.txt"

    response = build_agent_response(str(path))

    assert response["classification"]["document_type"] == "bem_imovel"
    assert response["decision"]["should_continue"] is True
    assert response["decision"]["schema_path"] == "skill/schemas/extracted_bem_imovel.json"


def test_agent_simulator_recibo_medico():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "recibo_medico_exemplo.txt"

    response = build_agent_response(str(path))

    assert response["classification"]["document_type"] == "recibo_medico"
    assert response["decision"]["should_continue"] is True
    assert response["decision"]["schema_path"] == "skill/schemas/extracted_recibo_medico.json"


def test_agent_simulator_json_cli():
    path = PROJECT_ROOT / "tests" / "fixtures" / "raw_text" / "crlv_veiculo_exemplo.txt"

    result = subprocess.run(
        [
            sys.executable,
            "tools/agent_simulator.py",
            str(path),
            "--json"
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"document_type": "bem_veiculo"' in result.stdout
    assert '"should_continue": true' in result.stdout
    assert '"schema_path": "skill/schemas/extracted_bem_veiculo.json"' in result.stdout


def run_tests():
    test_agent_simulator_bem_veiculo()
    test_agent_simulator_bem_imovel()
    test_agent_simulator_recibo_medico()
    test_agent_simulator_json_cli()
    print("test_agent_simulator.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()
