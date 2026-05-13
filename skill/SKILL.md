# Skill — IRPF OCR DEC

## Objetivo

Auxiliar na montagem inicial de dados para IRPF a partir de documentos, textos extraídos ou extrações estruturadas.

## Aviso importante

Esta skill não substitui PGD oficial, contador, revisão humana ou responsabilidade do contribuinte.

## Estado atual

O projeto possui:

- classificador simples;
- simulador local individual;
- simulador local em lote;
- pré-triagem de documentos;
- pipeline determinístico;
- validação canônica;
- relatório humano;
- limpeza de outputs conhecidos;
- checagem de desenvolvimento integrada;
- testes automatizados.

Ainda não possui OCR real, leitura direta de PDF/imagem, integração final com Agno nem geração `.DEC`.

## Fluxos

### Pré-triagem

```text
tests/fixtures/raw_text/
    ↓
tools/preflight_documents.py
    ↓
status ready ou blocked
    ↓
outputs/preflight-documents.json
    ↓
outputs/preflight-documents.report.md
```

### Checagem de desenvolvimento

```text
tools/dev_check.py
    ↓
Validar configuração
    ↓
Limpar outputs
    ↓
Rodar pré-triagem de documentos
    ↓
Rodar projeto
    ↓
Rodar testes
```

## Comandos

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown

python3 tools/preflight_documents.py tests/fixtures/raw_text
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true

python3 tools/clean_outputs.py
python3 tools/dev_check.py
python3 tools/run_project.py
```

## Limpeza de outputs

A limpeza é feita por:

```text
tools/clean_outputs.py
```

Ela remove:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

O `dev_check.py` executa essa limpeza antes da pré-triagem e do pipeline principal.

## Decisão recomendada e pré-triagem

O simulador em lote gera `recommended_action`.

A pré-triagem consome essa decisão e produz:

```text
ready
blocked
```

Quando `ready`, o agente pode avançar para criação de extrações estruturadas JSON.

Quando `blocked`, o agente deve interromper o avanço automático e solicitar revisão humana dos documentos bloqueantes.
