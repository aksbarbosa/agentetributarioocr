# CHANGELOG — IRPF OCR DEC

Registro das principais etapas implementadas no projeto.

---

## 2026-05 — Fundação inicial do projeto

### Estrutura base

Criada a estrutura inicial do projeto com pastas `config/`, `inputs/`, `outputs/`, `skill/`, `tests/` e `tools/`.

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

Gera:

```text
outputs/agent-decisions.json
outputs/agent-decisions.report.md
```

Suporta:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

O simulador em lote passou a gerar:

```text
recommended_action
```

Esse campo indica:

- se o lote pode continuar;
- mensagem explicativa;
- próximo passo recomendado.

Exemplo quando todos os documentos podem continuar:

```json
{
  "can_continue": true,
  "message": "Todos os 5 documento(s) foram classificados com confiança suficiente para continuar.",
  "next_step": "Prosseguir para criação das extrações estruturadas JSON."
}
```

Exemplo quando há documento que exige revisão:

```json
{
  "can_continue": false,
  "message": "Há 1 documento(s) que exigem revisão manual antes de avançar para extração estruturada.",
  "next_step": "Revisar manualmente os documentos marcados antes de continuar."
}
```

O relatório do simulador em lote destaca:

```markdown
## Ação recomendada
## Status dos documentos
### Aptos a continuar
### Exigem revisão
## Documentos que exigem revisão manual
```

Também foi adicionada fixture com documento desconhecido:

```text
tests/fixtures/raw_text_with_unknown/documento_desconhecido.txt
```

Essa fixture testa o cenário em que o lote contém um documento que exige revisão manual.

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
