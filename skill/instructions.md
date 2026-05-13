# Instruções do Agente — IRPF OCR DEC

## Papel do agente

Auxiliar o usuário a transformar documentos, textos extraídos ou extrações estruturadas em classificação provável, pré-triagem, JSON canônico, validações e relatório humano.

O agente não substitui contador, PGD oficial, revisão humana ou responsabilidade do contribuinte.

## Fluxo obrigatório

```text
documento, texto bruto ou extração
    ↓
classificação
    ↓
pré-triagem
    ↓
extração estruturada
    ↓
normalização
    ↓
validação
    ↓
JSON canônico
    ↓
relatório humano
    ↓
revisão do usuário
    ↓
geração futura do .DEC
```

## Pré-triagem

Use:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text
python3 tools/preflight_documents.py tests/fixtures/raw_text --json
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown --json || true
```

Se `status = ready`, o agente pode avançar para extrações estruturadas JSON.

Se `status = blocked`, o agente deve pedir revisão humana dos documentos bloqueantes.

## Limpeza de outputs

Use:

```bash
python3 tools/clean_outputs.py
```

Esse comando remove outputs conhecidos do pipeline, do simulador individual, do simulador em lote e da pré-triagem.

Arquivos removidos quando existirem:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

## Checagem de desenvolvimento

Use:

```bash
python3 tools/dev_check.py
```

Esse comando valida:

```text
configuração
limpeza dos outputs
pré-triagem de documentos
pipeline principal
testes automatizados
```

O agente deve orientar o usuário a rodar `tools/dev_check.py` antes de commits importantes.
