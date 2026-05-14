import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

def test_run_raw_flow_cli():
    result = subprocess.run(
        [
            sys.executable,
            "tools/run_raw_flow.py",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert "Iniciando fluxo real a partir de inputs/raw." in result.stdout
    assert "Escanear documentos brutos" in result.stdout
    assert "Extrair texto dos documentos brutos" in result.stdout
    assert "Rodar pré-triagem dos textos extraídos" in result.stdout
    assert "Gerar extrações estruturadas em lote" in result.stdout
    assert "Validar extrações estruturadas geradas" in result.stdout
    assert "OK: Validar extrações estruturadas geradas" in result.stdout
    assert "Promover extrações estruturadas válidas para pasta segura" in result.stdout
    assert "Fluxo real a partir de inputs/raw finalizado." in result.stdout

    assert (PROJECT_ROOT / "outputs/raw-inputs-manifest.json").exists()
    assert (PROJECT_ROOT / "outputs/raw-inputs-manifest.report.md").exists()
    assert (PROJECT_ROOT / "outputs/extract-text.json").exists()
    assert (PROJECT_ROOT / "outputs/extract-text.report.md").exists()
    assert (PROJECT_ROOT / "outputs/structured-extractions-batch.json").exists()
    assert (PROJECT_ROOT / "outputs/structured-extractions-batch.report.md").exists()
    assert (PROJECT_ROOT / "outputs/promote-structured-extractions.json").exists()
    assert (PROJECT_ROOT / "outputs/promote-structured-extractions.report.md").exists()
    assert (PROJECT_ROOT / "outputs/promoted_extractions").exists()

def run_tests():
    test_run_raw_flow_cli()
    print("test_run_raw_flow.py: todos os testes passaram.")


if __name__ == "__main__":
    run_tests()