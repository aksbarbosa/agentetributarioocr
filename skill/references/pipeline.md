# Pipeline — IRPF OCR DEC

Este arquivo documenta o fluxo atual do projeto.

O pipeline atual trabalha com extrações simuladas em JSON, textos brutos simulados, classificador simples, simulador local individual, simulador local em lote e validação determinística.

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
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown

python3 tools/run_project.py
python3 tools/dev_check.py
```

---

## Decisão recomendada do simulador em lote

O JSON de saída do simulador em lote contém:

```text
recommended_action
```

Formato quando pode continuar:

```json
{
  "can_continue": true,
  "message": "Todos os 5 documento(s) foram classificados com confiança suficiente para continuar.",
  "next_step": "Prosseguir para criação das extrações estruturadas JSON."
}
```

Formato quando exige revisão:

```json
{
  "can_continue": false,
  "message": "Há 1 documento(s) que exigem revisão manual antes de avançar para extração estruturada.",
  "next_step": "Revisar manualmente os documentos marcados antes de continuar."
}
```

---

## Relatório do simulador em lote

O relatório em lote contém:

```markdown
## Resumo geral
## Ação recomendada
## Resumo por tipo de documento
## Resumo por confiança
## Status dos documentos
### Aptos a continuar
### Exigem revisão
## Documentos que exigem revisão manual
## Decisões
```
