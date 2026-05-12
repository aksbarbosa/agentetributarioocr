# CHANGELOG — IRPF OCR DEC

## 2026-05 — Fundação inicial

### Classificador simples

Implementado:

```text
tools/classify_document.py
tests/unit/test_classify_document.py
```

### Simulador individual

Implementado:

```text
tools/agent_simulator.py
tests/unit/test_agent_simulator.py
```

### Simulador em lote

Implementado:

```text
tools/agent_batch_simulator.py
tests/unit/test_agent_batch_simulator.py
```

Gera:

```text
outputs/agent-decisions.json
outputs/agent-decisions.report.md
recommended_action
```

### Pré-triagem de documentos

Implementado:

```text
tools/preflight_documents.py
tests/unit/test_preflight_documents.py
```

Gera:

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

Status possíveis:

```text
ready
blocked
```

### Pré-triagem no dev_check

Atualizado:

```text
tools/dev_check.py
```

A checagem de desenvolvimento agora executa:

```text
1. Validar configuração
2. Limpar outputs
3. Rodar pré-triagem de documentos
4. Rodar projeto
5. Rodar testes
```

A pré-triagem usada no `dev_check.py` roda sobre:

```text
tests/fixtures/raw_text
```

O cenário bloqueado com documento desconhecido permanece coberto pelos testes automatizados, pois retorna exit code `1` intencionalmente.
