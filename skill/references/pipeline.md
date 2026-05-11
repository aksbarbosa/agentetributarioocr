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
outputs/agent-decisions.json
    ↓
outputs/agent-decisions.report.md
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
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
python3 tools/run_project.py
python3 tools/dev_check.py
```

---

## Saídas atuais

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
```

---

## Tipos suportados

| `document_type` | Destino |
|---|---|
| `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| `recibo_medico` | `pagamentos[]` |
| `plano_saude` | `pagamentos[]` |
| `bem_imovel` | `bens[]` |
| `bem_veiculo` | `bens[]` |

---

## Estado atual

O projeto já possui classificador individual, simulador individual, simulador em lote, pipeline canônico, relatório humano e testes automatizados.

Ainda não há OCR real, leitura direta de PDF/imagem, classificação robusta nem geração `.DEC`.
