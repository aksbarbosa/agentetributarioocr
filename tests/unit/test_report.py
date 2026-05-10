import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from pipeline_batch import run_batch_pipeline
from report import generate_report


def build_consolidated_data() -> dict:
    """
    Gera um JSON consolidado em memória usando o pipeline em lote.
    """
    import tempfile

    input_dir = PROJECT_ROOT / "inputs" / "extracted"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        output_json = temp_path / "irpf-teste.json"
        output_report = temp_path / "irpf-teste.report.md"

        run_batch_pipeline(
            input_dir=str(input_dir),
            output_json_path=str(output_json),
            output_report_path=str(output_report),
            config={
                "exercicio": 2026,
                "ano_calendario": 2025,
                "schema_version": "irpf-2026-v1",
                "tipo_declaracao": "AJUSTE_ANUAL",
                "modelo": "AUTO",
                "enable_duplicate_detection": True,
                "enable_human_review_report": True,
                "fail_on_invalid_extraction": False,
                "fail_on_canonical_error": True,
            }
        )

        with output_json.open("r", encoding="utf-8") as file:
            return json.load(file)


def test_report_has_main_sections():
    data = build_consolidated_data()
    report = generate_report(data)

    assert "# Relatório IRPF 2026" in report
    assert "## Aviso" in report
    assert "## Declarante" in report
    assert "## Validação" in report
    assert "## Avisos do processamento" in report
    assert "## Rendimentos tributáveis PJ" in report
    assert "## Pagamentos" in report
    assert "## Bens e direitos" in report
    assert "## Pendências de revisão" in report
    assert "## Próximos passos" in report


def test_report_has_current_document_data():
    data = build_consolidated_data()
    report = generate_report(data)

    assert "JOSE DA SILVA" in report
    assert "EMPRESA EXEMPLO LTDA" in report
    assert "CONSULTA MEDICA" in report
    assert "PLANO DE SAUDE" in report
    assert "APARTAMENTO RESIDENCIAL" in report


def test_report_has_imovel_details():
    data = build_consolidated_data()
    report = generate_report(data)

    assert "Tipo do bem: IMOVEL" in report
    assert "#### Endereço" in report
    assert "CEP:" in report
    assert "Logradouro:" in report
    assert "Município:" in report
    assert "UF:" in report
    assert "#### Dados do imóvel" in report
    assert "IPTU:" in report
    assert "Matrícula:" in report


def test_report_has_veiculo_details():
    data = build_consolidated_data()
    report = generate_report(data)

    assert "Tipo do bem: VEICULO" in report
    assert "AUTOMOVEL MARCA TOYOTA" in report
    assert "#### Dados do veículo" in report
    assert "RENAVAM: 12345678901" in report
    assert "Placa: ABC1D23" in report
    assert "Marca: TOYOTA" in report
    assert "Modelo: COROLLA XEI" in report
    assert "Ano de fabricação: 2020" in report


def test_report_has_review_item_for_matricula():
    data = build_consolidated_data()
    report = generate_report(data)

    assert "matricula" in report
    assert "Campo extraído com baixa confiança" in report


def run_tests():
    test_report_has_main_sections()
    test_report_has_current_document_data()
    test_report_has_imovel_details()
    test_report_has_veiculo_details()
    test_report_has_review_item_for_matricula()
    print("test_report.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()