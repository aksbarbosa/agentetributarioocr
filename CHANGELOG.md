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

Com funções para:

- remover caracteres não numéricos;
- remover acentos;
- normalizar nomes;
- converter dinheiro para centavos;
- normalizar datas.

### Classificação simples de documentos

Implementado:

```text
tools/classify_document.py
```

Esse classificador recebe texto bruto e tenta identificar o `document_type` por palavras-chave.

Tipos reconhecidos atualmente:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

Fixtures de texto bruto criadas em:

```text
tests/fixtures/raw_text/
```

Arquivos atuais:

```text
crlv_veiculo_exemplo.txt
iptu_imovel_exemplo.txt
recibo_medico_exemplo.txt
```

Teste automatizado criado:

```text
tests/unit/test_classify_document.py
```

Observação:

- ainda não há OCR real;
- o classificador não lê PDF ou imagem diretamente;
- ele pressupõe que o texto já foi extraído ou simulado.

### Validação canônica

Implementado:

```text
tools/validate.py
```

Valida atualmente:

- CPF;
- CNPJ;
- CPF ou CNPJ;
- datas em `DDMMAAAA`;
- declarante;
- rendimentos PJ;
- pagamentos;
- bens imóveis;
- bens veículos;
- configuração geral do projeto.

---

## Extrações estruturadas

Criado o conceito de extração simulada em JSON.

Formato base:

```json
{
  "document_type": "...",
  "source_file": "...",
  "fields": {}
}
```

Cada campo extraído segue:

```json
{
  "value": "...",
  "confidence": "high | medium | low",
  "source_hint": "..."
}
```

### Validação de extrações

Implementado:

```text
tools/validate_extracted.py
```

Suporta atualmente:

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

Converte extrações para JSON canônico.

Tipos suportados:

| Documento | Destino |
|---|---|
| `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| `recibo_medico` | `pagamentos[]` |
| `plano_saude` | `pagamentos[]` |
| `bem_imovel` | `bens[]` |
| `bem_veiculo` | `bens[]` |

---

## Suporte a bens

### Bem imóvel

Implementado suporte inicial a:

```text
document_type = bem_imovel
```

Destino:

```text
bens[]
```

Formato atual:

```text
tipo_bem = IMOVEL
grupo_bem = 01
codigo_bem = 11
```

Campos principais:

- descrição;
- valor anterior;
- valor atual;
- endereço;
- IPTU;
- matrícula;
- data de aquisição.

---

### Bem veículo

Implementado suporte inicial a:

```text
document_type = bem_veiculo
```

Destino:

```text
bens[]
```

Formato atual:

```text
tipo_bem = VEICULO
grupo_bem = 02
codigo_bem = 01
```

Campos principais:

- descrição;
- valor anterior;
- valor atual;
- RENAVAM;
- placa;
- marca;
- modelo;
- ano de fabricação;
- data de aquisição.

---

## Pipelines

### Pipeline individual

Implementado:

```text
tools/pipeline_from_extracted.py
```

Processa uma extração individual.

### Pipeline em lote

Implementado:

```text
tools/pipeline_batch.py
```

Processa uma pasta de extrações:

```text
inputs/extracted/
```

Gera:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
```

O pipeline em lote também:

- ignora extrações inválidas quando configurado;
- registra arquivos ignorados;
- consolida rendimentos, pagamentos e bens;
- detecta pagamentos possivelmente duplicados;
- valida o JSON canônico consolidado;
- gera relatório humano.

### Comando principal

Implementado:

```text
tools/run_project.py
```

Comando principal atual:

```bash
python3 tools/run_project.py
```

Esse comando:

1. carrega `config/project_config.json`;
2. valida a configuração;
3. executa o pipeline em lote;
4. gera outputs.

---

## Relatório humano

Implementado:

```text
tools/report.py
```

O relatório contém:

- aviso geral;
- declarante;
- validação;
- avisos do processamento;
- rendimentos tributáveis PJ;
- pagamentos;
- bens e direitos;
- detalhes de imóvel;
- detalhes de veículo;
- pendências de revisão;
- próximos passos.

---

## Organização de entradas e saídas

Criadas as pastas:

```text
inputs/raw/
inputs/extracted/
outputs/
tests/fixtures/raw_text/
```

Atualmente:

- `inputs/raw/` está reservado para documentos reais futuros;
- `inputs/extracted/` contém extrações simuladas;
- `tests/fixtures/raw_text/` contém textos brutos simulados para o classificador;
- `outputs/` recebe JSON consolidado e relatório.

---

## Configuração

Criado:

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

---

## Configuração validada

Criado:

```text
tools/validate_config.py
```

Esse arquivo valida:

- campos obrigatórios do `project_config.json`;
- tipos esperados;
- tipo de declaração;
- modelo;
- coerência entre exercício e ano-calendário;
- existência da pasta de extrações;
- extensão dos arquivos de saída.

Também foi criado o schema formal:

```text
skill/schemas/project_config.json
```

Esse schema documenta os campos esperados em:

```text
config/project_config.json
```

---

## Ferramentas de manutenção

### Limpeza de outputs

Implementado:

```text
tools/clean_outputs.py
```

Remove outputs gerados conhecidos.

### Checagem de desenvolvimento

Implementado:

```text
tools/dev_check.py
```

Executa:

```text
1. validate_config.py
2. clean_outputs.py
3. run_project.py
4. tests/run_tests.py
```

Comando:

```bash
python3 tools/dev_check.py
```

---

## Testes automatizados

Criada estrutura:

```text
tests/
├── fixtures/
│   └── raw_text/
├── run_tests.py
└── unit/
```

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
```

Comando:

```bash
python3 tests/run_tests.py
```

---

## Skill

Criada a estrutura inicial da skill:

```text
skill/
├── SKILL.md
├── instructions.md
├── references/
└── schemas/
```

### Referências criadas

```text
skill/references/codigos_bens.md
skill/references/codigos_pagamentos.md
skill/references/json_canonico.md
skill/references/pipeline.md
skill/references/tipos_documentos.md
```

### Schemas criados

```text
skill/schemas/canonical_irpf_2026.json
skill/schemas/extracted_bem_imovel.json
skill/schemas/extracted_bem_veiculo.json
skill/schemas/extracted_informe_pj.json
skill/schemas/extracted_plano_saude.json
skill/schemas/extracted_recibo_medico.json
skill/schemas/project_config.json
```

---

## Estado atual

O projeto já possui uma versão local funcional com extrações simuladas e classificador simples de textos.

Fluxo atual de classificação:

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

Fluxo atual do pipeline principal:

```text
config/project_config.json
    ↓
tools/run_project.py
    ↓
validação da configuração
    ↓
inputs/extracted/
    ↓
validação das extrações
    ↓
JSON canônico consolidado
    ↓
validação canônica
    ↓
relatório humano
```

Documentos suportados:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
```

---

## Ainda não implementado

O projeto ainda não possui:

- OCR real;
- leitura de PDF/imagem;
- classificação automática robusta de documentos reais;
- geração de `.DEC`;
- transmissão da declaração;
- parser reverso `.DEC`;
- suporte a dependentes;
- suporte a investimentos;
- suporte a rendimentos isentos/exclusivos;
- cálculo completo de imposto.

---

## Próximas etapas planejadas

1. Expandir fixtures de texto bruto para informe PJ e plano de saúde.
2. Melhorar o classificador simples.
3. Preparar camada de OCR real.
4. Criar leitor de PDF/imagem.
5. Expandir schemas.
6. Iniciar estudo do builder `.DEC`.
7. Criar parser reverso `.DEC`.
8. Expandir suporte a dependentes, investimentos e outros rendimentos.
