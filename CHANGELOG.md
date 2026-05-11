# CHANGELOG — IRPF OCR DEC

Registro das principais etapas implementadas no projeto.

---

## 2026-05 — Fundação inicial do projeto

### Estrutura base

Criada a estrutura inicial do projeto com pastas `config/`, `inputs/`, `outputs/`, `skill/`, `tests/` e `tools/`.

### Objetivo definido

O projeto foi definido como base experimental para classificar documentos, simular decisão de agente, normalizar dados, gerar JSON canônico, validar inconsistências, gerar relatório humano e futuramente gerar `.DEC`.

---

## Núcleo determinístico

### Normalização

Implementado:

```text
tools/normalize.py
```

### Classificação simples

Implementado:

```text
tools/classify_document.py
tests/unit/test_classify_document.py
```

Tipos reconhecidos:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

### Simulador local individual

Implementado:

```text
tools/agent_simulator.py
tests/unit/test_agent_simulator.py
```

Comandos:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
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
```

---

## Extrações estruturadas

Implementado suporte a:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
```

---

## JSON canônico

Implementado:

```text
tools/build_canonical_json.py
```

---

## Pipelines

Implementado:

```text
tools/pipeline_from_extracted.py
tools/pipeline_batch.py
tools/run_project.py
```

---

## Relatório humano

Implementado:

```text
tools/report.py
```

---

## Configuração

Implementado:

```text
config/project_config.json
tools/validate_config.py
skill/schemas/project_config.json
```

---

## Ferramentas de manutenção

Implementado:

```text
tools/clean_outputs.py
tools/dev_check.py
```

---

## Testes automatizados

Testes atuais:

```text
test_normalize.py
test_validate.py
test_validate_config.py
test_validate_extracted.py
test_build_canonical_json.py
test_pipeline_batch.py
test_report.py
test_clean_outputs.py
test_run_project.py
test_classify_document.py
test_agent_simulator.py
test_agent_batch_simulator.py
```

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
