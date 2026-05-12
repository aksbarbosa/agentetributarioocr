# Pipeline — IRPF OCR DEC

Este arquivo documenta o fluxo atual do projeto.

O pipeline atual trabalha com extrações simuladas em JSON, textos brutos simulados, classificador simples, simulador local individual, simulador local em lote, pré-triagem e validação determinística.

Ainda não há OCR real, leitura direta de PDF/imagem ou geração `.DEC`.

---

## Fluxo geral

### Classificação simples

```text
texto bruto simulado
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### Simulação individual

```text
texto bruto simulado
    ↓
tools/agent_simulator.py
    ↓
classificação
    ↓
decisão estruturada
    ↓
schema recomendado
    ↓
próximo passo sugerido
```

### Simulação em lote

```text
pasta com textos brutos
    ↓
tools/agent_batch_simulator.py
    ↓
decisões individuais
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
validação da configuração
    ↓
inputs/extracted/*.json
    ↓
validação das extrações
    ↓
conversão para JSON canônico parcial
    ↓
consolidação
    ↓
validação canônica
    ↓
relatório humano
```

---

## Comandos

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json

python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json

python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown

python3 tools/preflight_documents.py tests/fixtures/raw_text
python3 tools/preflight_documents.py tests/fixtures/raw_text --json
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown --json || true

python3 tools/run_project.py
python3 tools/dev_check.py
```

---

## Saídas da pré-triagem

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

O JSON contém:

```text
input_dir
status
can_continue
message
next_step
summary
blocking_documents
batch_response
```

Status possíveis:

```text
ready
blocked
```
