# Pipeline — IRPF OCR DEC

## Fluxo geral

### Classificação

```text
texto bruto simulado
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### Simulação em lote

```text
pasta com textos brutos
    ↓
tools/agent_batch_simulator.py
    ↓
recommended_action
    ↓
outputs/agent-decisions.json
    ↓
outputs/agent-decisions.report.md
```

### Pré-triagem

```text
pasta com textos brutos
    ↓
tools/preflight_documents.py
    ↓
agent_batch_simulator.py
    ↓
status ready ou blocked
    ↓
outputs/preflight-documents.json
    ↓
outputs/preflight-documents.report.md
```

### Pipeline principal

```text
config/project_config.json
    ↓
tools/run_project.py
    ↓
inputs/extracted/*.json
    ↓
JSON canônico consolidado
    ↓
relatório humano
```

### Checagem de desenvolvimento

```text
tools/dev_check.py
    ↓
tools/validate_config.py
    ↓
tools/clean_outputs.py
    ↓
tools/preflight_documents.py tests/fixtures/raw_text
    ↓
tools/run_project.py
    ↓
tests/run_tests.py
```

## Comandos

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text
python3 tools/preflight_documents.py tests/fixtures/raw_text --json
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown --json || true
python3 tools/dev_check.py
```

## Saídas da pré-triagem

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

Status possíveis:

```text
ready
blocked
```
