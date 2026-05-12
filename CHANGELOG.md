# CHANGELOG — IRPF OCR DEC

Registro das principais etapas implementadas no projeto.

---

## 2026-05 — Fundação inicial do projeto

### Classificação simples

Implementado:

```text
tools/classify_document.py
tests/unit/test_classify_document.py
```

### Simulador local individual

Implementado:

```text
tools/agent_simulator.py
tests/unit/test_agent_simulator.py
```

### Simulador local em lote

Implementado:

```text
tools/agent_batch_simulator.py
tests/unit/test_agent_batch_simulator.py
```

O simulador em lote gera:

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

A pré-triagem usa o simulador em lote e decide se o fluxo pode avançar.

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

Quando `ready`, o fluxo pode avançar para criação de extrações estruturadas JSON.

Quando `blocked`, o fluxo deve parar até revisão humana dos documentos bloqueantes.

---

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
