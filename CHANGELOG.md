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

A checagem de desenvolvimento passou a executar:

```text
1. Validar configuração
2. Limpar outputs
3. Rodar pré-triagem de documentos
4. Rodar projeto
5. Rodar testes
```

### Limpeza de outputs do agente e da pré-triagem

Atualizado:

```text
tools/clean_outputs.py
tests/unit/test_clean_outputs.py
```

A limpeza remove:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

### Resumo final no dev_check

Atualizado:

```text
tools/dev_check.py
```

A checagem de desenvolvimento agora imprime, ao final, um resumo das etapas executadas:

```text
Checagem concluída com sucesso.

Etapas executadas:
- Validar configuração
- Limpar outputs
- Rodar pré-triagem de documentos
- Rodar projeto
- Rodar testes
```

Essa melhoria facilita verificar rapidamente quais etapas foram executadas com sucesso.

## Ainda não implementado

- OCR real;
- leitura de PDF/imagem;
- classificação automática robusta;
- geração de `.DEC`;
- transmissão da declaração;
- parser reverso `.DEC`;
- suporte a dependentes;
- suporte a investimentos;
- cálculo completo de imposto.
