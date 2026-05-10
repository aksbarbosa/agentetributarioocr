import sys
from pathlib import Path
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))

from pipeline_batch import run_batch_pipeline


def test_pipeline_batch_outputs():
    input_dir = PROJECT_ROOT / "inputs" / "extracted"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        output_json = temp_path / "irpf-teste.json"
        output_report = temp_path / "irpf-teste.report.md"

        result = run_batch_pipeline(
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

        assert result["canonical_validation"]["valid"] is True
        assert len(result["skipped_files"]) == 0
        assert len(result["processed_files"]) == 5

        assert output_json.exists()
        assert output_report.exists()


def test_pipeline_batch_consolidated_content():
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

        import json

        with output_json.open("r", encoding="utf-8") as file:
            data = json.load(file)

        assert data["$schema"] == "irpf-2026-v1"
        assert data["exercicio"] == 2026
        assert data["ano_calendario"] == 2025
        assert data["tipo_declaracao"] == "AJUSTE_ANUAL"
        assert data["modelo"] == "AUTO"

        assert data["declarante"]["cpf"] == "12345678909"
        assert data["declarante"]["nome"] == "JOSE DA SILVA"

        assert len(data["rendimentos"]["tributaveis_pj"]) == 1
        assert len(data["pagamentos"]) == 2
        assert len(data["bens"]) == 2

        pagamento_codigos = [pagamento["codigo"] for pagamento in data["pagamentos"]]

        assert "10" in pagamento_codigos
        assert "26" in pagamento_codigos

        tipos_bens = [bem["tipo_bem"] for bem in data["bens"]]

        assert "IMOVEL" in tipos_bens
        assert "VEICULO" in tipos_bens

        bem_imovel = next(bem for bem in data["bens"] if bem["tipo_bem"] == "IMOVEL")
        bem_veiculo = next(bem for bem in data["bens"] if bem["tipo_bem"] == "VEICULO")

        assert bem_imovel["grupo_bem"] == "01"
        assert bem_imovel["codigo_bem"] == "11"
        assert bem_imovel["endereco"]["uf"] == "SP"

        assert bem_veiculo["grupo_bem"] == "02"
        assert bem_veiculo["codigo_bem"] == "01"
        assert bem_veiculo["renavam"] == "12345678901"
        assert bem_veiculo["placa"] == "ABC1D23"
        assert bem_veiculo["marca"] == "TOYOTA"
        assert bem_veiculo["modelo"] == "COROLLA XEI"
        assert bem_veiculo["ano_fabricacao"] == "2020"

        requires_review = data["requires_review"]
        review_fields = [item["field"] for item in requires_review]

        assert "matricula" in review_fields


def test_pipeline_batch_report_content():
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

        report_text = output_report.read_text(encoding="utf-8")

        assert "## Declarante" in report_text
        assert "## Rendimentos tributáveis PJ" in report_text
        assert "## Pagamentos" in report_text
        assert "## Bens e direitos" in report_text
        assert "## Pendências de revisão" in report_text
        assert "matricula" in report_text

        assert "APARTAMENTO RESIDENCIAL" in report_text
        assert "AUTOMOVEL MARCA TOYOTA" in report_text


def run_tests():
    test_pipeline_batch_outputs()
    test_pipeline_batch_consolidated_content()
    test_pipeline_batch_report_content()
    print("test_pipeline_batch.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()