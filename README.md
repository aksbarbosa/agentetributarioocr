# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente capaz de auxiliar na montagem inicial da Declaração de Imposto de Renda Pessoa Física a partir de documentos digitalizados, textos extraídos ou extrações estruturadas.

A ideia central é transformar documentos fiscais em um JSON canônico revisável e, futuramente, gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Este projeto não substitui contador, revisão humana, PGD oficial da Receita Federal ou responsabilidade do contribuinte.

O fluxo correto é:

```text
documento
    ↓
OCR ou texto extraído
    ↓
classificação
    ↓
extração estruturada
    ↓
JSON canônico
    ↓
validação
    ↓
relatório humano
    ↓
revisão
    ↓
geração futura do .DEC
```

---

## Estado atual

Atualmente o projeto possui:

- classificador simples por palavras-chave;
- simulador local de agente individual;
- simulador local de agente em lote;
- pipeline determinístico de extrações simuladas;
- validação canônica;
- relatório humano;
- testes automatizados.

Ainda não possui OCR real, leitura direta de PDF/imagem, integração final com Agno nem geração `.DEC`.


---

## Fluxos atuais

### Classificador

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### Simulador local individual

```text
tests/fixtures/raw_text/
    ↓
tools/agent_simulator.py
    ↓
classificação
    ↓
decisão
    ↓
schema recomendado
    ↓
próximo passo
```

### Simulador local em lote

```text
tests/fixtures/raw_text/
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
inputs/extracted/
    ↓
tools/run_project.py
    ↓
validação da configuração
    ↓
validação das extrações
    ↓
normalização
    ↓
JSON canônico consolidado
    ↓
validação canônica
    ↓
relatório humano
```

---

## Documentos suportados

| Documento | `document_type` | Destino |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |

---

## Estrutura principal

```text
irpf_ocr_dec/
├── README.md
├── CHANGELOG.md
├── config/
│   └── project_config.json
├── inputs/
│   ├── raw/
│   └── extracted/
├── outputs/
├── skill/
│   ├── SKILL.md
│   ├── instructions.md
│   ├── references/
│   │   ├── codigos_bens.md
│   │   ├── codigos_pagamentos.md
│   │   ├── json_canonico.md
│   │   ├── pipeline.md
│   │   └── tipos_documentos.md
│   └── schemas/
├── tests/
│   ├── fixtures/raw_text/
│   ├── run_tests.py
│   └── unit/
└── tools/
    ├── agent_batch_simulator.py
    ├── agent_simulator.py
    ├── build_canonical_json.py
    ├── classify_document.py
    ├── clean_outputs.py
    ├── dev_check.py
    ├── normalize.py
    ├── pipeline_batch.py
    ├── pipeline_from_extracted.py
    ├── report.py
    ├── run_project.py
    ├── validate.py
    ├── validate_config.py
    └── validate_extracted.py
```

---

## Configuração

Arquivo:

```text
config/project_config.json
```

Exemplo:

```json
{
  "project_name": "IRPF OCR DEC",
  "schema_version": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "input_raw_dir": "inputs/raw",
  "input_extracted_dir": "inputs/extracted",
  "output_dir": "outputs",
  "output_json": "outputs/irpf-consolidado.json",
  "output_report": "outputs/irpf-consolidado.report.md",
  "fail_on_invalid_extraction": false,
  "fail_on_canonical_error": true,
  "enable_duplicate_detection": true,
  "enable_human_review_report": true
}
```

Validar configuração:

```bash
python3 tools/validate_config.py config/project_config.json
```

---

## Comandos principais

Rodar projeto:

```bash
python3 tools/run_project.py
```

Rodar testes:

```bash
python3 tests/run_tests.py
```

Rodar checagem completa:

```bash
python3 tools/dev_check.py
```

Classificar texto bruto:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Simular agente individual:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Simular agente em lote:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
```

---

## Saídas

O pipeline principal gera:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
```

O simulador individual pode gerar:

```text
outputs/agent-decision.json
```

O simulador em lote gera:

```text
outputs/agent-decisions.json
outputs/agent-decisions.report.md
```

---

## JSON canônico

Formato resumido:

```json
{
  "$schema": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "declarante": {},
  "rendimentos": {
    "tributaveis_pj": []
  },
  "pagamentos": [],
  "bens": [],
  "dividas": [],
  "avisos": [],
  "requires_review": []
}
```

---

## Testes cobertos

```text
normalize.py
validate.py
validate_config.py
validate_extracted.py
build_canonical_json.py
pipeline_batch.py
run_project.py
report.py
clean_outputs.py
classify_document.py
agent_simulator.py
agent_batch_simulator.py
```

---

## Git e versionamento

Fluxo recomendado:

```bash
git status
python3 tools/dev_check.py
git add .
git commit -m "Mensagem objetiva do que mudou"
git push
```

---

## Próximas etapas

1. Melhorar o simulador local em lote.
2. Melhorar o simulador local individual.
3. Melhorar o classificador simples.
4. Preparar OCR real.
5. Criar leitura de PDF/imagem.
6. Expandir schemas.
7. Estudar builder `.DEC`.
8. Integrar ao Agno.
