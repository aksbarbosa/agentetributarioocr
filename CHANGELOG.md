# CHANGELOG — IRPF OCR DEC

Registro das principais etapas implementadas no projeto.

---

## 2026-05 — Fundação inicial do projeto

### Estrutura base

Criada a estrutura inicial do projeto:

```text
irpf_ocr_dec/
├── config/
├── inputs/
├── outputs/
├── skill/
├── tests/
└── tools/
```

### Objetivo definido

O projeto foi definido como uma base experimental para:

- receber documentos, textos extraídos ou extrações estruturadas;
- classificar documentos;
- simular decisão inicial de agente;
- normalizar dados;
- gerar JSON canônico;
- validar inconsistências;
- gerar relatório humano;
- futuramente gerar arquivo `.DEC` experimental.

---

## Núcleo determinístico

### Normalização

Implementado:

```text
tools/normalize.py
```

### Classificação simples de documentos

Implementado:

```text
tools/classify_document.py
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

Também suporta:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Teste:

```text
tests/unit/test_classify_document.py
```

---

### Simulador local de agente individual

Implementado:

```text
tools/agent_simulator.py
```

Comandos:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Teste:

```text
tests/unit/test_agent_simulator.py
```

---

### Simulador local de agente em lote

Implementado:

```text
tools/agent_batch_simulator.py
```

O simulador em lote recebe uma pasta com arquivos `.txt`, executa a lógica de decisão local para cada documento e gera:

```text
outputs/agent-decisions.json
outputs/agent-decisions.report.md
```

Ele produz:

- decisões individuais;
- resumo por `document_type`;
- resumo por nível de confiança;
- contagem de documentos aptos a continuar;
- contagem de documentos que exigem revisão manual.

Teste:

```text
tests/unit/test_agent_batch_simulator.py
```

Comando:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
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

## Estado atual

O projeto já possui:

- versão local funcional com extrações simuladas;
- classificador simples;
- simulador local individual;
- simulador local em lote;
- pipeline determinístico;
- relatório humano;
- testes automatizados.

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

---

## Próximas etapas planejadas

1. Melhorar o simulador local em lote.
2. Melhorar o simulador local individual.
3. Melhorar o classificador simples.
4. Preparar OCR real.
5. Criar leitor de PDF/imagem.
6. Expandir schemas.
7. Iniciar estudo do builder `.DEC`.
8. Criar parser reverso `.DEC`.
